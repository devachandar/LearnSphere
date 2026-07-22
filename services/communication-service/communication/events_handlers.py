import requests
from django.conf import settings

from . import mailer
from .models import Notification

QUEUE_NAME = "communication-service.events"

AUTH_SERVICE_URL = settings.INTERNAL_SERVICE_URLS["auth"]
LEARNING_SERVICE_URL = settings.INTERNAL_SERVICE_URLS["learning"]


def _resolve_user(user_id):
    try:
        res = requests.get(f"{AUTH_SERVICE_URL}/internal/users/{user_id}", timeout=5)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return None


def _resolve_course(course_id):
    try:
        res = requests.get(f"{LEARNING_SERVICE_URL}/courses/{course_id}", timeout=5)
        if res.status_code == 200:
            return res.json()
    except requests.RequestException:
        pass
    return None


def _notify(user_id, notif_type, title, body):
    Notification.objects.create(user_id=user_id, type=notif_type, title=title, body=body)


def handle_user_registered(payload):
    _notify(payload["userId"], "welcome", "Welcome to LearnSphere", f"Hi {payload['fullName']}, your account is ready.")
    mailer.send("welcome", payload["email"], {"fullName": payload["fullName"]})


def handle_enrollment_created(payload):
    learner = _resolve_user(payload["learnerId"])
    title = f"You're enrolled in {payload['courseTitle']}"
    body = f"You've successfully enrolled in \"{payload['courseTitle']}\". Jump back in any time to keep learning."
    _notify(payload["learnerId"], "enrollment", title, body)
    if learner:
        mailer.send("enrollment", learner["email"], {"courseTitle": payload["courseTitle"]})

    course = _resolve_course(payload["courseId"])
    if course and course.get("instructor_id"):
        instructor_title = f"New enrollment in {payload['courseTitle']}"
        instructor_body = f"A learner just enrolled in \"{payload['courseTitle']}\"."
        _notify(course["instructor_id"], "enrollment", instructor_title, instructor_body)


def handle_assessment_completed(payload):
    if not payload.get("passed"):
        return
    learner = _resolve_user(payload["learnerId"])
    course = _resolve_course(payload["courseId"])
    label = "quiz" if payload.get("type") == "quiz" else "assignment"
    course_title = course["title"] if course else "your course"
    title = "Nice work!"
    body = f"You scored {payload['score']}% on the {label} for \"{course_title}\" - keep it up."
    _notify(payload["learnerId"], "assessment", title, body)
    if learner:
        mailer.send("assessment_passed", learner["email"], {"score": payload["score"], "label": label, "courseTitle": course_title})


def handle_certificate_issued(payload):
    learner = _resolve_user(payload["learnerId"])
    course = _resolve_course(payload["courseId"])
    course_title = course["title"] if course else "your course"
    title = "Certificate earned!"
    body = f"Congratulations - you completed \"{course_title}\" and earned a certificate."
    _notify(payload["learnerId"], "certificate", title, body)
    if learner:
        mailer.send("certificate", learner["email"], {"courseTitle": course_title})


HANDLERS = {
    "UserRegistered": handle_user_registered,
    "EnrollmentCreated": handle_enrollment_created,
    "AssessmentCompleted": handle_assessment_completed,
    "CertificateIssued": handle_certificate_issued,
}
