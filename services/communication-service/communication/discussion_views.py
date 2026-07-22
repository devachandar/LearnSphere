from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Announcement, DiscussionPost, DiscussionThread
from .permissions import IsAuthenticatedStateless, IsRole


class AnnouncementCreateView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def post(self, request):
        course_id = request.data.get("courseId")
        title = request.data.get("title")
        body = request.data.get("body")
        if not course_id or not title or not body:
            return Response({"error": "courseId, title and body are required"}, status=400)
        a = Announcement.objects.create(
            course_id=course_id, organization_id=request.user.organization_id, author_id=request.user.id, title=title, body=body
        )
        return Response({"id": str(a.id), "title": a.title, "body": a.body, "created_at": a.created_at}, status=201)


class AnnouncementByCourseView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request, course_id):
        qs = Announcement.objects.filter(course_id=course_id).order_by("-created_at")
        return Response([{"id": str(a.id), "title": a.title, "body": a.body, "created_at": a.created_at} for a in qs])


class DiscussionThreadCreateView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def post(self, request):
        course_id = request.data.get("courseId")
        title = request.data.get("title")
        if not course_id or not title:
            return Response({"error": "courseId and title are required"}, status=400)
        thread = DiscussionThread.objects.create(course_id=course_id, author_id=request.user.id, title=title)
        return Response({"id": str(thread.id), "title": thread.title, "created_at": thread.created_at}, status=201)


class DiscussionThreadsByCourseView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request, course_id):
        qs = DiscussionThread.objects.filter(course_id=course_id).order_by("-created_at")
        return Response([{"id": str(t.id), "title": t.title, "created_at": t.created_at} for t in qs])


class DiscussionPostsView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def post(self, request, thread_id):
        body = request.data.get("body")
        if not body:
            return Response({"error": "body is required"}, status=400)
        post = DiscussionPost.objects.create(thread_id=thread_id, author_id=request.user.id, body=body)
        return Response(
            {"id": str(post.id), "author_id": str(post.author_id), "body": post.body, "created_at": post.created_at}, status=201
        )

    def get(self, request, thread_id):
        qs = DiscussionPost.objects.filter(thread_id=thread_id).order_by("created_at")
        return Response(
            [{"id": str(p.id), "author_id": str(p.author_id), "body": p.body, "created_at": p.created_at} for p in qs]
        )
