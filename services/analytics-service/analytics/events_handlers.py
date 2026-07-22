from datetime import date as date_cls

from django.db.models import F

from .models import CourseMetric, DailyMetric

QUEUE_NAME = "analytics-service.events"


def _touch_daily(organization_id):
    row, _ = DailyMetric.objects.get_or_create(date=date_cls.today(), organization_id=organization_id)
    return row


def handle_user_registered(payload):
    if not payload.get("organizationId"):
        return  # platform_admin accounts aren't tenant-scoped
    row = _touch_daily(payload["organizationId"])
    DailyMetric.objects.filter(pk=row.pk).update(new_users=F("new_users") + 1)


def handle_enrollment_created(payload):
    row = _touch_daily(payload["organizationId"])
    DailyMetric.objects.filter(pk=row.pk).update(enrollments=F("enrollments") + 1)

    metric, created = CourseMetric.objects.get_or_create(
        course_id=payload["courseId"], defaults={"organization_id": payload["organizationId"], "enrollment_count": 1}
    )
    if not created:
        CourseMetric.objects.filter(course_id=payload["courseId"]).update(enrollment_count=F("enrollment_count") + 1)


def handle_assessment_completed(payload):
    """course_metrics rows are created by handle_enrollment_created (a
    learner must enroll before they can take a quiz) - if it isn't there
    yet, skip rather than guessing at organization_id."""
    CourseMetric.objects.filter(course_id=payload["courseId"]).update(
        score_sum=F("score_sum") + payload["score"], score_count=F("score_count") + 1
    )


def handle_certificate_issued(payload):
    try:
        metric = CourseMetric.objects.get(course_id=payload["courseId"])
    except CourseMetric.DoesNotExist:
        return
    row = _touch_daily(metric.organization_id)
    DailyMetric.objects.filter(pk=row.pk).update(certificates_issued=F("certificates_issued") + 1)
    CourseMetric.objects.filter(course_id=payload["courseId"]).update(completion_count=F("completion_count") + 1)


HANDLERS = {
    "UserRegistered": handle_user_registered,
    "EnrollmentCreated": handle_enrollment_created,
    "AssessmentCompleted": handle_assessment_completed,
    "CertificateIssued": handle_certificate_issued,
}
