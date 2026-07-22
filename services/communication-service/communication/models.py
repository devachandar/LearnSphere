import uuid

from django.db import models


class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.UUIDField()
    organization_id = models.UUIDField()
    author_id = models.UUIDField()
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class DiscussionThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.UUIDField()
    author_id = models.UUIDField()
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class DiscussionPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(DiscussionThread, on_delete=models.CASCADE, related_name="posts")
    author_id = models.UUIDField()
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    type = models.CharField(max_length=50)
    title = models.CharField(max_length=255)
    body = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user_id"])]
