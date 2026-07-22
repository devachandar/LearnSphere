from rest_framework import serializers

from .models import AuditLog, Organization, SupportTicket


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "invite_code", "subscription_plan", "status", "created_at", "updated_at"]


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ["id", "organization_id", "created_by", "subject", "body", "status", "created_at", "updated_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "organization_id", "actor_id", "action", "metadata", "created_at"]
