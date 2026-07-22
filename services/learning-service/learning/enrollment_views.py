from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Bookmark, Certificate, Course, Enrollment, Lesson, LessonProgress, Note
from .permissions import IsRole
from .rabbitmq_bus import publish_event
from .serializers import CertificateSerializer, EnrollmentSerializer


def _count_lessons(course_id) -> int:
    return Lesson.objects.filter(module__course_id=course_id).count()


def _maybe_complete_enrollment(enrollment):
    total = _count_lessons(enrollment.course_id)
    done = LessonProgress.objects.filter(enrollment=enrollment).count()
    if total > 0 and done >= total and enrollment.status != "completed":
        from django.utils import timezone

        enrollment.status = "completed"
        enrollment.completed_at = timezone.now()
        enrollment.save(update_fields=["status", "completed_at", "updated_at"])

        cert = Certificate.objects.create(enrollment=enrollment, course_id=enrollment.course_id, learner_id=enrollment.learner_id)
        publish_event(
            "CertificateIssued",
            {
                "certificateId": str(cert.id),
                "courseId": str(enrollment.course_id),
                "learnerId": str(enrollment.learner_id),
                "enrollmentId": str(enrollment.id),
            },
        )


class EnrollView(APIView):
    permission_classes = [IsRole("learner")]

    def post(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id, status="published")
        except (Course.DoesNotExist, ValueError):
            return Response({"error": "Course not found or not published"}, status=404)

        existing = Enrollment.objects.filter(course_id=course_id, learner_id=request.user.id).first()
        if existing:
            return Response(EnrollmentSerializer(existing).data, status=200)

        enrollment = Enrollment.objects.create(
            course=course, learner_id=request.user.id, organization_id=request.user.organization_id
        )
        publish_event(
            "EnrollmentCreated",
            {
                "enrollmentId": str(enrollment.id),
                "courseId": str(course.id),
                "courseTitle": course.title,
                "learnerId": str(request.user.id),
                "organizationId": str(request.user.organization_id),
            },
        )
        return Response(EnrollmentSerializer(enrollment).data, status=201)


class MyEnrollmentsView(APIView):
    permission_classes = [IsRole("learner")]

    def get(self, request):
        enrollments = Enrollment.objects.filter(learner_id=request.user.id).select_related("course").order_by("-enrolled_at")
        results = []
        for e in enrollments:
            total = _count_lessons(e.course_id)
            done = LessonProgress.objects.filter(enrollment=e).count()
            data = EnrollmentSerializer(e).data
            data["course_title"] = e.course.title
            data["thumbnail_url"] = e.course.thumbnail_url
            data["progressPercent"] = round((done / total) * 100) if total else 0
            results.append(data)
        return Response(results)


class CourseEnrollmentsView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def get(self, request, course_id):
        qs = Enrollment.objects.filter(course_id=course_id).order_by("-enrolled_at")
        return Response(EnrollmentSerializer(qs, many=True).data)


class CompleteLessonView(APIView):
    permission_classes = [IsRole("learner")]

    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.select_related("module").get(id=lesson_id)
        except (Lesson.DoesNotExist, ValueError):
            return Response({"error": "Lesson not found"}, status=404)

        enrollment = Enrollment.objects.filter(course_id=lesson.module.course_id, learner_id=request.user.id).first()
        if not enrollment:
            return Response({"error": "You're not enrolled in this course"}, status=403)

        LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
        _maybe_complete_enrollment(enrollment)
        return Response(status=204)


class LessonNotesView(APIView):
    permission_classes = [IsRole("learner")]

    def post(self, request, lesson_id):
        content = request.data.get("content")
        if not content:
            return Response({"error": "content is required"}, status=400)
        note = Note.objects.create(learner_id=request.user.id, lesson_id=lesson_id, content=content)
        return Response({"id": str(note.id), "content": note.content, "created_at": note.created_at}, status=201)

    def get(self, request, lesson_id):
        notes = Note.objects.filter(learner_id=request.user.id, lesson_id=lesson_id).order_by("-created_at")
        return Response([{"id": str(n.id), "content": n.content, "created_at": n.created_at} for n in notes])


class LessonBookmarkView(APIView):
    permission_classes = [IsRole("learner")]

    def post(self, request, lesson_id):
        Bookmark.objects.get_or_create(learner_id=request.user.id, lesson_id=lesson_id)
        return Response(status=204)

    def delete(self, request, lesson_id):
        Bookmark.objects.filter(learner_id=request.user.id, lesson_id=lesson_id).delete()
        return Response(status=204)


class MyCertificatesView(APIView):
    permission_classes = [IsRole("learner")]

    def get(self, request):
        certs = Certificate.objects.filter(learner_id=request.user.id).select_related("enrollment__course").order_by("-issued_at")
        results = []
        for c in certs:
            data = CertificateSerializer(c).data
            data["course_title"] = c.enrollment.course.title
            results.append(data)
        return Response(results)
