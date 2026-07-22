from .models import AuditLog

QUEUE_NAME = "admin-service.events"


def handle_user_registered(payload):
    AuditLog.objects.create(
        organization_id=payload.get("organizationId"),
        actor_id=payload["userId"],
        action="USER_REGISTERED",
        metadata={"email": payload["email"], "role": payload["role"]},
    )


HANDLERS = {
    "UserRegistered": handle_user_registered,
}
