from rest_framework import serializers

from .models import User


class UserPublicSerializer(serializers.ModelSerializer):
    """Matches the original Node service's publicUser() helper - used
    consistently for register/login/me/internal responses."""

    fullName = serializers.CharField(source="full_name")
    organizationId = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "fullName", "role", "organizationId"]

    def get_organizationId(self, obj):
        return str(obj.organization_id) if obj.organization_id else None


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    fullName = serializers.CharField(max_length=150, source="full_name")
    role = serializers.ChoiceField(choices=["org_admin", "instructor", "learner"])
    organizationName = serializers.CharField(required=False, allow_blank=True)
    inviteCode = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
