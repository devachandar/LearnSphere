import uuid

from django.db import models


class MediaFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploader_id = models.UUIDField()
    organization_id = models.UUIDField(null=True, blank=True)
    url = models.URLField(max_length=500)
    content_type = models.CharField(max_length=100)
    original_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
