import uuid

from django.db import models


class Quiz(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.UUIDField()
    organization_id = models.UUIDField()
    created_by = models.UUIDField()
    title = models.CharField(max_length=255)
    passing_score = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20, choices=[("multiple_choice", "Multiple choice"), ("true_false", "True/false")], default="multiple_choice"
    )
    options = models.JSONField(default=list, blank=True)
    correct_answer = models.CharField(max_length=255)
    points = models.IntegerField(default=1)
    sort_order = models.IntegerField(default=0)


class QuizSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="submissions")
    learner_id = models.UUIDField()
    score = models.IntegerField()
    passed = models.BooleanField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("quiz", "learner_id")


class QuizAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.UUIDField()
    organization_id = models.UUIDField()
    created_by = models.UUIDField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    due_date = models.DateTimeField(null=True, blank=True)
    max_points = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)


class AssignmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    learner_id = models.UUIDField()
    content_url = models.URLField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True)
    grade = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, default="")
    graded_by = models.UUIDField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assignment", "learner_id")
