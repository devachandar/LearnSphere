from rest_framework import serializers

from .models import Certificate, Course, Enrollment, Lesson, Module


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "content_type", "content_url", "text_content", "duration_minutes", "sort_order"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "sort_order", "lessons"]


class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "organization_id", "instructor_id", "title", "description", "category",
            "status", "thumbnail_url", "modules", "created_at", "updated_at",
        ]


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id", "organization_id", "instructor_id", "title", "description", "category",
            "status", "thumbnail_url", "created_at", "updated_at",
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["id", "course_id", "learner_id", "organization_id", "status", "enrolled_at", "completed_at", "updated_at"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["id", "enrollment_id", "course_id", "learner_id", "issued_at"]
