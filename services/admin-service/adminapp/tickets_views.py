from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SupportTicket
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import SupportTicketSerializer


class SupportTicketListCreateView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def post(self, request):
        subject = request.data.get("subject")
        body = request.data.get("body")
        if not subject or not body:
            return Response({"error": "subject and body are required"}, status=400)
        ticket = SupportTicket.objects.create(
            organization_id=request.user.organization_id, created_by=request.user.id, subject=subject, body=body
        )
        return Response(SupportTicketSerializer(ticket).data, status=201)

    def get(self, request):
        if request.user.role == "platform_admin":
            qs = SupportTicket.objects.order_by("-created_at")[:200]
        else:
            qs = SupportTicket.objects.filter(organization_id=request.user.organization_id).order_by("-created_at")
        return Response(SupportTicketSerializer(qs, many=True).data)


class SupportTicketDetailView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def patch(self, request, pk):
        status_value = request.data.get("status")
        if status_value not in ("open", "in_progress", "resolved", "closed"):
            return Response({"error": "Invalid status"}, status=400)
        try:
            ticket = SupportTicket.objects.get(id=pk)
        except (SupportTicket.DoesNotExist, ValueError):
            return Response({"error": "Ticket not found"}, status=404)
        ticket.status = status_value
        ticket.save(update_fields=["status", "updated_at"])
        return Response(SupportTicketSerializer(ticket).data)
