import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField()
    instructor_id = models.UUIDField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100, default="general")
    status = models.CharField(
        max_length=20, choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="draft"
    )
    thumbnail_url = models.URLField(null=True, blank=True)
    search_vector = SearchVectorField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization_id"]),
            GinIndex(fields=["search_vector"]),
        ]


class Module(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    sort_order = models.IntegerField(default=0)


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content_type = models.CharField(
        max_length=20, choices=[("video", "Video"), ("text", "Text"), ("pdf", "PDF")], default="text"
    )
    content_url = models.URLField(null=True, blank=True)
    text_content = models.TextField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    sort_order = models.IntegerField(default=0)


class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    learner_id = models.UUIDField()
    organization_id = models.UUIDField()
    status = models.CharField(
        max_length=20, choices=[("active", "Active"), ("completed", "Completed"), ("dropped", "Dropped")], default="active"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("course", "learner_id")
        indexes = [models.Index(fields=["learner_id"])]


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("enrollment", "lesson")


class Certificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="certificates")
    course_id = models.UUIDField()
    learner_id = models.UUIDField()
    issued_at = models.DateTimeField(auto_now_add=True)


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    learner_id = models.UUIDField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="notes")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Bookmark(models.Model):
    learner_id = models.UUIDField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="bookmarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("learner_id", "lesson")
