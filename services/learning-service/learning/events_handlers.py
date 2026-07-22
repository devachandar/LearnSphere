from django.utils import timezone

from .models import Enrollment

QUEUE_NAME = "learning-service.events"


def handle_assessment_completed(payload):
    """Assessment Service owns quizzes/grades entirely - this just keeps
    the enrollment's "last activity" accurate on days where the learner
    only took a quiz and didn't open a lesson."""
    Enrollment.objects.filter(course_id=payload["courseId"], learner_id=payload["learnerId"]).update(
        updated_at=timezone.now()
    )


HANDLERS = {
    "AssessmentCompleted": handle_assessment_completed,
}
