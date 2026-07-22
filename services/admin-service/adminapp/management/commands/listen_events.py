"""
Each service that subscribes to events copies this file into
<app>/management/commands/listen_events.py and customizes the handler
dispatch table in `events_handlers.py` of that same app. Run with:

    python manage.py listen_events
"""
from django.core.management.base import BaseCommand

from .. import events_handlers
from ..rabbitmq_bus import start_event_consumer


class Command(BaseCommand):
    help = "Subscribe to domain events on RabbitMQ and dispatch to handlers"

    def handle(self, *args, **options):
        queue_name = f"{events_handlers.QUEUE_NAME}"
        start_event_consumer(queue_name, events_handlers.HANDLERS)
