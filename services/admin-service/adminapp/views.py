import secrets

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog, Organization
from .permissions import IsRole, IsTenantScoped
from .rabbitmq_bus import publish_event
from .serializers import OrganizationSerializer


def _generate_invite_code() -> str:
    return secrets.token_hex(5).upper()  # 10 chars


class InternalCreateOrganizationView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        name = request.data.get("name")
        if not name:
            return Response({"error": "name is required"}, status=400)

        invite_code = _generate_invite_code()
        for _ in range(5):
            if not Organization.objects.filter(invite_code=invite_code).exists():
                break
            invite_code = _generate_invite_code()

        org = Organization.objects.create(name=name, invite_code=invite_code)
        publish_event("OrganizationCreated", {"organizationId": str(org.id), "name": org.name})
        return Response(OrganizationSerializer(org).data, status=201)


class InternalResolveInviteView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, code):
        try:
            org = Organization.objects.get(invite_code=code.upper(), status="active")
        except Organization.DoesNotExist:
            return Response({"error": "Invalid invite code"}, status=404)
        return Response(OrganizationSerializer(org).data)


class InternalOrganizationDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        try:
            org = Organization.objects.get(id=pk)
        except (Organization.DoesNotExist, ValueError):
            return Response({"error": "Organization not found"}, status=404)
        return Response(OrganizationSerializer(org).data)


class MyOrganizationView(APIView):
    permission_classes = [IsRole("org_admin"), IsTenantScoped]

    def get(self, request):
        try:
            org = Organization.objects.get(id=request.user.organization_id)
        except (Organization.DoesNotExist, ValueError):
            return Response({"error": "Organization not found"}, status=404)
        return Response(OrganizationSerializer(org).data)


class OrganizationListView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def get(self, request):
        qs = Organization.objects.order_by("-created_at")
        return Response(OrganizationSerializer(qs, many=True).data)


class OrganizationStatusView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def patch(self, request, pk):
        status_value = request.data.get("status")
        if status_value not in ("active", "suspended"):
            return Response({"error": "status must be 'active' or 'suspended'"}, status=400)
        try:
            org = Organization.objects.get(id=pk)
        except (Organization.DoesNotExist, ValueError):
            return Response({"error": "Organization not found"}, status=404)
        org.status = status_value
        org.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            organization_id=org.id, actor_id=request.user.id, action="ORGANIZATION_STATUS_CHANGED", metadata={"status": status_value}
        )
        return Response(OrganizationSerializer(org).data)


class OrganizationPlanView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def patch(self, request, pk):
        plan = request.data.get("plan")
        if plan not in ("free", "starter", "business", "enterprise"):
            return Response({"error": "Invalid subscription plan"}, status=400)
        try:
            org = Organization.objects.get(id=pk)
        except (Organization.DoesNotExist, ValueError):
            return Response({"error": "Organization not found"}, status=404)
        org.subscription_plan = plan
        org.save(update_fields=["subscription_plan", "updated_at"])
        return Response(OrganizationSerializer(org).data)
