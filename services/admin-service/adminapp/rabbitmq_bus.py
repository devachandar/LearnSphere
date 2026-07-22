"""
Cross-service event bus, built directly on a RabbitMQ topic exchange -
matches the original Node.js LearnSphere design. Every service that binds
a queue to `domain_events` gets its own durable copy of a matching event:
genuine pub/sub fan-out (not a job queue, where a message goes to
whichever single worker grabs it first), and because each service's queue
is durable, an event published while that service is briefly down is
still there waiting when it reconnects.
"""
import json
import logging

import pika
from django.conf import settings

logger = logging.getLogger(__name__)

EXCHANGE = "domain_events"

_publish_connection = None
_publish_channel = None


def _get_publish_channel():
    global _publish_connection, _publish_channel
    if _publish_channel is None or _publish_channel.is_closed:
        _publish_connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        _publish_channel = _publish_connection.channel()
        _publish_channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    return _publish_channel


def publish_event(event_name: str, payload: dict):
    """The event bus being briefly unavailable should never fail the
    customer-facing request that triggered it."""
    try:
        channel = _get_publish_channel()
        body = json.dumps({"event": event_name, "payload": payload}, default=str)
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=event_name,
            body=body,
            properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not publish %s: %s", event_name, exc)


def start_event_consumer(queue_name: str, handlers: dict):
    """Declares this service's own durable queue, binds it to every
    routing key (event name) in `handlers`, and blocks consuming. Run via
    `python manage.py listen_events` as its own process/container."""
    routing_keys = list(handlers.keys())
    if not routing_keys:
        return

    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=queue_name, durable=True)
    for key in routing_keys:
        channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=key)

    def _on_message(ch, method, properties, body):
        try:
            message = json.loads(body)
            handler = handlers.get(message["event"])
            if handler:
                handler(message["payload"])
                print(f"Handled {message['event']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:  # noqa: BLE001
            print(f"Error handling event, requeueing: {exc}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue=queue_name, on_message_callback=_on_message)
    print(f"[events] {queue_name} listening for: {', '.join(routing_keys)}")
    channel.start_consuming()
