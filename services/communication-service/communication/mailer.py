from django.conf import settings
from django.core.mail import send_mail

TEMPLATES = {
    "welcome": lambda ctx: ("Welcome to LearnSphere", f"Hi {ctx['fullName']}, your account is ready."),
    "enrollment": lambda ctx: (
        f"You're enrolled in {ctx['courseTitle']}",
        f"You've successfully enrolled in \"{ctx['courseTitle']}\". Jump back in any time to keep learning.",
    ),
    "new_enrollment_instructor": lambda ctx: (
        f"New enrollment in {ctx['courseTitle']}",
        f"A learner just enrolled in \"{ctx['courseTitle']}\".",
    ),
    "assessment_passed": lambda ctx: (
        "Nice work!",
        f"You scored {ctx['score']}% on the {ctx['label']} for \"{ctx['courseTitle']}\" - keep it up.",
    ),
    "certificate": lambda ctx: (
        "Certificate earned!",
        f"Congratulations - you completed \"{ctx['courseTitle']}\" and earned a certificate.",
    ),
}


def send(template_name, to_email, context):
    if not to_email:
        return {"delivered": False, "reason": "no recipient email"}
    build = TEMPLATES.get(template_name)
    if not build:
        raise ValueError(f"Unknown notification template: {template_name}")
    subject, body = build(context)

    if not settings.EMAIL_BACKEND_CONFIGURED:
        import logging

        logging.getLogger(__name__).info("(console fallback) -> %s | Subject: %s | %s", to_email, subject, body)
        return {"delivered": False, "reason": "SMTP not configured, logged only"}

    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to_email])
    return {"delivered": True}
