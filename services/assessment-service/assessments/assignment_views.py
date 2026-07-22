from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Assignment, AssignmentSubmission
from .permissions import IsRole
from .rabbitmq_bus import publish_event


class AssignmentCreateView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def post(self, request):
        course_id = request.data.get("courseId")
        title = request.data.get("title")
        if not course_id or not title:
            return Response({"error": "courseId and title are required"}, status=400)
        assignment = Assignment.objects.create(
            course_id=course_id,
            organization_id=request.user.organization_id,
            created_by=request.user.id,
            title=title,
            description=request.data.get("description", ""),
            due_date=request.data.get("dueDate"),
            max_points=request.data.get("maxPoints", 100),
        )
        return Response(
            {"id": str(assignment.id), "course_id": str(assignment.course_id), "title": assignment.title, "max_points": assignment.max_points},
            status=201,
        )


class AssignmentByCourseView(APIView):
    def get(self, request, course_id):
        qs = Assignment.objects.filter(course_id=course_id).order_by("created_at")
        return Response(
            [
                {
                    "id": str(a.id), "course_id": str(a.course_id), "title": a.title,
                    "description": a.description, "due_date": a.due_date, "max_points": a.max_points,
                }
                for a in qs
            ]
        )


class AssignmentSubmitView(APIView):
    permission_classes = [IsRole("learner")]

    def post(self, request, pk):
        content_url = request.data.get("contentUrl")
        text_content = request.data.get("textContent")
        if not content_url and not text_content:
            return Response({"error": "contentUrl or textContent is required"}, status=400)

        submission, _ = AssignmentSubmission.objects.update_or_create(
            assignment_id=pk, learner_id=request.user.id, defaults={"content_url": content_url, "text_content": text_content}
        )
        return Response({"id": str(submission.id), "submitted_at": submission.submitted_at}, status=201)


class AssignmentSubmissionsView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def get(self, request, pk):
        qs = AssignmentSubmission.objects.filter(assignment_id=pk).order_by("-submitted_at")
        return Response(
            [
                {"id": str(s.id), "learner_id": str(s.learner_id), "grade": s.grade, "feedback": s.feedback, "submitted_at": s.submitted_at}
                for s in qs
            ]
        )


class GradeSubmissionView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def patch(self, request, pk):
        grade = request.data.get("grade")
        if not isinstance(grade, (int, float)):
            return Response({"error": "grade must be a number"}, status=400)

        from django.utils import timezone

        try:
            submission = AssignmentSubmission.objects.get(id=pk)
        except (AssignmentSubmission.DoesNotExist, ValueError):
            return Response({"error": "Submission not found"}, status=404)

        submission.grade = grade
        submission.feedback = request.data.get("feedback", "")
        submission.graded_by = request.user.id
        submission.graded_at = timezone.now()
        submission.save()

        assignment = submission.assignment
        publish_event(
            "AssessmentCompleted",
            {
                "type": "assignment",
                "assignmentId": str(assignment.id),
                "courseId": str(assignment.course_id),
                "learnerId": str(submission.learner_id),
                "score": round((grade / assignment.max_points) * 100),
                "passed": grade >= assignment.max_points * 0.6,
            },
        )
        return Response({"id": str(submission.id), "grade": submission.grade, "feedback": submission.feedback})
