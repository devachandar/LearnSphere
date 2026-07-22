from django.urls import path

from . import course_views as cv
from . import enrollment_views as ev

urlpatterns = [
    # ---- courses ----
    path("courses", cv.CourseCreateListView.as_view()),
    path("courses/search", cv.CourseSearchView.as_view()),
    path("courses/mine", cv.MyCoursesView.as_view()),
    path("courses/modules/<str:module_id>/lessons", cv.LessonCreateView.as_view()),
    path("courses/<str:pk>", cv.CourseDetailView.as_view()),
    path("courses/<str:pk>/publish", cv.PublishCourseView.as_view()),
    path("courses/<str:pk>/modules", cv.ModuleCreateView.as_view()),
    # ---- enrollments ----
    path("enrollments/mine", ev.MyEnrollmentsView.as_view()),
    path("enrollments/certificates/mine", ev.MyCertificatesView.as_view()),
    path("enrollments/course/<str:course_id>", ev.CourseEnrollmentsView.as_view()),
    path("enrollments/lessons/<str:lesson_id>/complete", ev.CompleteLessonView.as_view()),
    path("enrollments/lessons/<str:lesson_id>/notes", ev.LessonNotesView.as_view()),
    path("enrollments/lessons/<str:lesson_id>/bookmark", ev.LessonBookmarkView.as_view()),
    path("enrollments/<str:course_id>", ev.EnrollView.as_view()),
]
