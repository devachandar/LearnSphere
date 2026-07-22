from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .permissions import IsAuthenticatedStateless


class MyNotificationsView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = Notification.objects.filter(user_id=request.user.id).order_by("-created_at")[:50]
        return Response(
            [
                {"id": str(n.id), "type": n.type, "title": n.title, "body": n.body, "read_at": n.read_at, "created_at": n.created_at}
                for n in qs
            ]
        )


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def patch(self, request, pk):
        Notification.objects.filter(id=pk, user_id=request.user.id).update(read_at=timezone.now())
        return Response(status=204)
