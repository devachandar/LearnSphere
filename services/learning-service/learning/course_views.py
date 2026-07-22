from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from rest_framework.response import Response
from rest_framework.views import APIView

from .cache import get_cached_course, invalidate_course_cache, set_cached_course
from .models import Course, Lesson, Module
from .permissions import IsAuthenticatedStateless, IsRole, IsTenantScoped
from .rabbitmq_bus import publish_event
from .serializers import CourseListSerializer, CourseSerializer


def _update_search_vector(course_id):
    Course.objects.filter(id=course_id).update(
        search_vector=SearchVector("title", weight="A") + SearchVector("description", weight="B")
    )


def _load_full_course(course_id):
    cached = get_cached_course(str(course_id))
    if cached:
        return cached
    try:
        course = Course.objects.prefetch_related("modules__lessons").get(id=course_id)
    except (Course.DoesNotExist, ValueError):
        return None
    data = CourseSerializer(course).data
    set_cached_course(str(course_id), data)
    return data


class CourseCreateListView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsRole("instructor", "org_admin"), IsTenantScoped]
        return [IsAuthenticatedStateless, IsTenantScoped]

    def post(self, request):
        title = request.data.get("title")
        if not title:
            return Response({"error": "title is required"}, status=400)
        course = Course.objects.create(
            organization_id=request.user.organization_id,
            instructor_id=request.user.id,
            title=title,
            description=request.data.get("description", ""),
            category=request.data.get("category", "general"),
            thumbnail_url=request.data.get("thumbnailUrl"),
        )
        _update_search_vector(course.id)
        return Response(CourseSerializer(course).data, status=201)

    def get(self, request):
        org_filter = {} if request.user.role == "platform_admin" else {"organization_id": request.user.organization_id}
        qs = Course.objects.filter(status="published", **org_filter).order_by("-created_at")[:100]
        return Response(CourseListSerializer(qs, many=True).data)


class CourseSearchView(APIView):
    permission_classes = [IsAuthenticatedStateless, IsTenantScoped]

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response([])
        query = SearchQuery(q, search_type="websearch")
        qs = (
            Course.objects.filter(organization_id=request.user.organization_id, status="published", search_vector=query)
            .annotate(rank=SearchRank("search_vector", query))
            .order_by("-rank")[:50]
        )
        return Response(CourseListSerializer(qs, many=True).data)


class MyCoursesView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def get(self, request):
        qs = Course.objects.filter(instructor_id=request.user.id).order_by("-created_at")
        return Response(CourseListSerializer(qs, many=True).data)


class CourseDetailView(APIView):
    permission_classes = []

    def get(self, request, pk):
        full = _load_full_course(pk)
        if not full:
            return Response({"error": "Course not found"}, status=404)
        return Response(full)

    def patch(self, request, pk):
        if not request.user or request.user.role not in ("instructor", "org_admin"):
            return Response({"error": "Insufficient permissions"}, status=403)
        try:
            course = Course.objects.get(id=pk)
        except (Course.DoesNotExist, ValueError):
            return Response({"error": "Course not found"}, status=404)
        if str(course.instructor_id) != str(request.user.id) and request.user.role != "org_admin":
            return Response({"error": "You don't own this course"}, status=403)

        field_map = {"title": "title", "description": "description", "category": "category", "thumbnailUrl": "thumbnail_url"}
        updated = False
        for key, column in field_map.items():
            if key in request.data:
                setattr(course, column, request.data[key])
                updated = True
        if not updated:
            return Response({"error": "No valid fields to update"}, status=400)
        course.save()
        _update_search_vector(course.id)
        invalidate_course_cache(str(pk))

        full = _load_full_course(pk)
        return Response(full)


class PublishCourseView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def post(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
        except (Course.DoesNotExist, ValueError):
            return Response({"error": "Course not found"}, status=404)
        course.status = "published"
        course.save(update_fields=["status", "updated_at"])
        invalidate_course_cache(str(pk))
        publish_event("CoursePublished", CourseListSerializer(course).data)
        return Response(CourseListSerializer(course).data)


class ModuleCreateView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def post(self, request, pk):
        title = request.data.get("title")
        if not title:
            return Response({"error": "title is required"}, status=400)
        module = Module.objects.create(course_id=pk, title=title, sort_order=request.data.get("sortOrder", 0))
        invalidate_course_cache(str(pk))
        return Response({"id": str(module.id), "title": module.title, "sort_order": module.sort_order}, status=201)


class LessonCreateView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def post(self, request, module_id):
        title = request.data.get("title")
        if not title:
            return Response({"error": "title is required"}, status=400)
        try:
            module = Module.objects.get(id=module_id)
        except (Module.DoesNotExist, ValueError):
            return Response({"error": "Module not found"}, status=404)

        lesson = Lesson.objects.create(
            module=module,
            title=title,
            content_type=request.data.get("contentType", "text"),
            content_url=request.data.get("contentUrl"),
            text_content=request.data.get("textContent"),
            duration_minutes=request.data.get("durationMinutes", 0),
            sort_order=request.data.get("sortOrder", 0),
        )
        invalidate_course_cache(str(module.course_id))
        return Response(
            {
                "id": str(lesson.id),
                "title": lesson.title,
                "content_type": lesson.content_type,
                "duration_minutes": lesson.duration_minutes,
            },
            status=201,
        )
