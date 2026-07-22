from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CourseMetric, DailyMetric
from .permissions import IsRole


class OrganizationAnalyticsView(APIView):
    permission_classes = [IsRole("org_admin")]

    def get(self, request):
        since = timezone.now().date() - timedelta(days=30)
        rows = DailyMetric.objects.filter(organization_id=request.user.organization_id, date__gte=since).order_by("date")
        totals = rows.aggregate(
            new_users=Sum("new_users"), enrollments=Sum("enrollments"), certificates_issued=Sum("certificates_issued")
        )
        return Response(
            {
                "totals": {
                    "newUsers": totals["new_users"] or 0,
                    "enrollments": totals["enrollments"] or 0,
                    "certificatesIssued": totals["certificates_issued"] or 0,
                },
                "daily": [
                    {
                        "date": r.date.isoformat(), "new_users": r.new_users,
                        "enrollments": r.enrollments, "certificates_issued": r.certificates_issued,
                    }
                    for r in rows
                ],
            }
        )


class PlatformAnalyticsView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def get(self, request):
        since = timezone.now().date() - timedelta(days=30)
        rows = (
            DailyMetric.objects.filter(date__gte=since)
            .values("date")
            .annotate(new_users=Sum("new_users"), enrollments=Sum("enrollments"), certificates_issued=Sum("certificates_issued"))
            .order_by("date")
        )
        active_orgs = DailyMetric.objects.values("organization_id").distinct().count()
        return Response(
            {
                "activeOrganizations": active_orgs,
                "daily": [
                    {
                        "date": r["date"].isoformat(), "new_users": r["new_users"],
                        "enrollments": r["enrollments"], "certificates_issued": r["certificates_issued"],
                    }
                    for r in rows
                ],
            }
        )


class CourseMetricsView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def get(self, request, pk):
        try:
            row = CourseMetric.objects.get(course_id=pk)
        except (CourseMetric.DoesNotExist, ValueError):
            return Response({"courseId": pk, "enrollmentCount": 0, "completionCount": 0, "averageScore": None})
        return Response(
            {
                "courseId": str(row.course_id),
                "enrollmentCount": row.enrollment_count,
                "completionCount": row.completion_count,
                "averageScore": round(row.score_sum / row.score_count) if row.score_count else None,
            }
        )
