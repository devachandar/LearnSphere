from django.urls import path

from . import assignment_views as av
from . import quiz_views as qv

urlpatterns = [
    path("quizzes", qv.QuizCreateView.as_view()),
    path("quizzes/course/<str:course_id>", qv.QuizByCourseView.as_view()),
    path("quizzes/<str:pk>", qv.QuizDetailView.as_view()),
    path("quizzes/<str:pk>/submit", qv.QuizSubmitView.as_view()),
    path("quizzes/<str:pk>/submissions", qv.QuizSubmissionsView.as_view()),
    path("assignments", av.AssignmentCreateView.as_view()),
    path("assignments/course/<str:course_id>", av.AssignmentByCourseView.as_view()),
    path("assignments/submissions/<str:pk>/grade", av.GradeSubmissionView.as_view()),
    path("assignments/<str:pk>/submit", av.AssignmentSubmitView.as_view()),
    path("assignments/<str:pk>/submissions", av.AssignmentSubmissionsView.as_view()),
]
