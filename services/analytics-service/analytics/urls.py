from django.urls import path

from . import views

urlpatterns = [
    path("organization", views.OrganizationAnalyticsView.as_view()),
    path("platform", views.PlatformAnalyticsView.as_view()),
    path("courses/<str:pk>", views.CourseMetricsView.as_view()),
]
