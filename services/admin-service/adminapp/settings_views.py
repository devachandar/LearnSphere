from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, PlatformSetting
from .permissions import IsRole
from .serializers import AuditLogSerializer


class InternalAuditLogCreateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        action = request.data.get("action")
        if not action:
            return Response({"error": "action is required"}, status=400)
        AuditLog.objects.create(
            organization_id=request.data.get("organizationId"),
            actor_id=request.data.get("actorId"),
            action=action,
            metadata=request.data.get("metadata") or {},
        )
        return Response({"ok": True}, status=201)


class AuditLogListView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def get(self, request):
        qs = AuditLog.objects.order_by("-created_at")[:300]
        return Response(AuditLogSerializer(qs, many=True).data)


class PlatformSettingsView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def get(self, request):
        return Response({row.key: row.value for row in PlatformSetting.objects.all()})


class PlatformSettingDetailView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def put(self, request, key):
        value = request.data.get("value")
        PlatformSetting.objects.update_or_create(key=key, defaults={"value": value})
        return Response({"key": key, "value": value})
