import uuid

from django.db import models


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    invite_code = models.CharField(max_length=20, unique=True)
    subscription_plan = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("starter", "Starter"), ("business", "Business"), ("enterprise", "Enterprise")],
        default="free",
    )
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("suspended", "Suspended")], default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SupportTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(null=True, blank=True)
    created_by = models.UUIDField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[("open", "Open"), ("in_progress", "In progress"), ("resolved", "Resolved"), ("closed", "Closed")],
        default="open",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(null=True, blank=True)
    actor_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PlatformSetting(models.Model):
    key = models.CharField(max_length=100, primary_key=True)
    value = models.JSONField()
