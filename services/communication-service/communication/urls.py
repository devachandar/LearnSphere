from django.urls import path

from . import discussion_views as dv
from . import notification_views as nv

urlpatterns = [
    path("announcements", dv.AnnouncementCreateView.as_view()),
    path("announcements/course/<str:course_id>", dv.AnnouncementByCourseView.as_view()),
    path("discussions", dv.DiscussionThreadCreateView.as_view()),
    path("discussions/course/<str:course_id>", dv.DiscussionThreadsByCourseView.as_view()),
    path("discussions/<str:thread_id>/posts", dv.DiscussionPostsView.as_view()),
    path("notifications/mine", nv.MyNotificationsView.as_view()),
    path("notifications/<str:pk>/read", nv.MarkNotificationReadView.as_view()),
]
