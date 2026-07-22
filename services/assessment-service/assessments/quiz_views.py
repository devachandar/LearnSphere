from django.db import transaction
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Question, Quiz, QuizAnswer, QuizSubmission
from .permissions import IsAuthenticatedStateless, IsRole
from .rabbitmq_bus import publish_event


class QuizCreateView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def post(self, request):
        course_id = request.data.get("courseId")
        title = request.data.get("title")
        if not course_id or not title:
            return Response({"error": "courseId and title are required"}, status=400)

        with transaction.atomic():
            quiz = Quiz.objects.create(
                course_id=course_id,
                organization_id=request.user.organization_id,
                created_by=request.user.id,
                title=title,
                passing_score=request.data.get("passingScore", 70),
            )
            for i, q in enumerate(request.data.get("questions", [])):
                Question.objects.create(
                    quiz=quiz,
                    question_text=q["questionText"],
                    question_type=q.get("questionType", "multiple_choice"),
                    options=q.get("options", []),
                    correct_answer=q["correctAnswer"],
                    points=q.get("points", 1),
                    sort_order=i,
                )
        return Response(
            {"id": str(quiz.id), "course_id": str(quiz.course_id), "title": quiz.title, "passing_score": quiz.passing_score},
            status=201,
        )


class QuizByCourseView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request, course_id):
        qs = Quiz.objects.filter(course_id=course_id).order_by("created_at")
        return Response(
            [{"id": str(q.id), "course_id": str(q.course_id), "title": q.title, "passing_score": q.passing_score} for q in qs]
        )


class QuizDetailView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request, pk):
        try:
            quiz = Quiz.objects.get(id=pk)
        except (Quiz.DoesNotExist, ValueError):
            return Response({"error": "Quiz not found"}, status=404)

        questions = Question.objects.filter(quiz=quiz).order_by("sort_order")
        is_learner = request.user.role == "learner"
        question_data = []
        for q in questions:
            item = {
                "id": str(q.id), "question_text": q.question_text, "question_type": q.question_type,
                "options": q.options, "points": q.points,
            }
            if not is_learner:
                item["correct_answer"] = q.correct_answer
            question_data.append(item)

        return Response(
            {
                "id": str(quiz.id), "course_id": str(quiz.course_id), "title": quiz.title,
                "passing_score": quiz.passing_score, "questions": question_data,
            }
        )


class QuizSubmitView(APIView):
    permission_classes = [IsRole("learner")]

    def post(self, request, pk):
        answers = request.data.get("answers")
        if not isinstance(answers, list):
            return Response({"error": "answers must be an array"}, status=400)

        try:
            quiz = Quiz.objects.get(id=pk)
        except (Quiz.DoesNotExist, ValueError):
            return Response({"error": "Quiz not found"}, status=404)

        questions = list(Question.objects.filter(quiz=quiz))
        total_points = sum(q.points for q in questions) or 1

        earned = 0
        graded = []
        for a in answers:
            question = next((q for q in questions if str(q.id) == str(a.get("questionId"))), None)
            is_correct = bool(question) and question.correct_answer.strip().lower() == str(a.get("answerText", "")).strip().lower()
            if is_correct and question:
                earned += question.points
            graded.append({"questionId": a.get("questionId"), "answerText": a.get("answerText"), "isCorrect": is_correct})

        score = round((earned / total_points) * 100)
        passed = score >= quiz.passing_score

        with transaction.atomic():
            submission, _ = QuizSubmission.objects.update_or_create(
                quiz=quiz, learner_id=request.user.id, defaults={"score": score, "passed": passed}
            )
            QuizAnswer.objects.filter(submission=submission).delete()
            for g in graded:
                QuizAnswer.objects.create(
                    submission=submission, question_id=g["questionId"], answer_text=g["answerText"], is_correct=g["isCorrect"]
                )

        publish_event(
            "AssessmentCompleted",
            {
                "type": "quiz", "quizId": str(quiz.id), "courseId": str(quiz.course_id),
                "learnerId": str(request.user.id), "score": score, "passed": passed,
            },
        )

        return Response({"id": str(submission.id), "score": score, "passed": passed, "totalQuestions": len(questions)})


class QuizSubmissionsView(APIView):
    permission_classes = [IsRole("instructor", "org_admin")]

    def get(self, request, pk):
        qs = QuizSubmission.objects.filter(quiz_id=pk).order_by("-submitted_at")
        return Response(
            [{"id": str(s.id), "learner_id": str(s.learner_id), "score": s.score, "passed": s.passed, "submitted_at": s.submitted_at} for s in qs]
        )
