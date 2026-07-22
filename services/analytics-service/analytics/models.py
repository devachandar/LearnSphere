from django.db import models


class DailyMetric(models.Model):
    date = models.DateField()
    organization_id = models.UUIDField()
    new_users = models.IntegerField(default=0)
    enrollments = models.IntegerField(default=0)
    certificates_issued = models.IntegerField(default=0)

    class Meta:
        unique_together = ("date", "organization_id")


class CourseMetric(models.Model):
    course_id = models.UUIDField(primary_key=True)
    organization_id = models.UUIDField()
    enrollment_count = models.IntegerField(default=0)
    completion_count = models.IntegerField(default=0)
    score_sum = models.IntegerField(default=0)
    score_count = models.IntegerField(default=0)
