import requests
from django.conf import settings
from django.utils import timezone as djtz
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RefreshToken, User
from .permissions import IsAuthenticatedStateless, IsRole
from .rabbitmq_bus import publish_event
from .serializers import LoginSerializer, RegisterSerializer, UserPublicSerializer
from .tokens import generate_refresh_token, hash_token, issue_access_token

ADMIN_SERVICE_URL = settings.INTERNAL_SERVICE_URLS["admin"]


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role = data["role"]

        if role == "org_admin":
            organization_name = data.get("organizationName")
            if not organization_name:
                return Response({"error": "organizationName is required to create an organization"}, status=400)
            try:
                org_res = requests.post(
                    f"{ADMIN_SERVICE_URL}/internal/organizations", json={"name": organization_name}, timeout=5
                )
            except requests.RequestException:
                return Response({"error": "Could not create your organization right now"}, status=502)
            if org_res.status_code != 201:
                return Response({"error": "Could not create your organization right now"}, status=502)
            organization_id = org_res.json()["id"]
        else:
            invite_code = data.get("inviteCode")
            if not invite_code:
                return Response({"error": "inviteCode is required to join an organization"}, status=400)
            try:
                org_res = requests.get(f"{ADMIN_SERVICE_URL}/internal/organizations/resolve-invite/{invite_code}", timeout=5)
            except requests.RequestException:
                return Response({"error": "That invite code isn't valid"}, status=400)
            if org_res.status_code != 200:
                return Response({"error": "That invite code isn't valid"}, status=400)
            organization_id = org_res.json()["id"]

        user = User(email=data["email"], full_name=data["full_name"], role=role, organization_id=organization_id)
        user.set_password(serializer.initial_data["password"])
        user.save()

        publish_event(
            "UserRegistered",
            {
                "userId": str(user.id),
                "email": user.email,
                "fullName": user.full_name,
                "role": user.role,
                "organizationId": str(user.organization_id),
            },
        )

        access_token = issue_access_token(user)
        raw_refresh, hashed, expires_at = generate_refresh_token()
        RefreshToken.objects.create(user=user, token_hash=hashed, expires_at=expires_at)

        return Response(
            {"user": UserPublicSerializer(user).data, "accessToken": access_token, "refreshToken": raw_refresh},
            status=201,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=401)

        if user.status == "suspended":
            return Response({"error": "This account has been suspended"}, status=403)
        if not user.check_password(password):
            return Response({"error": "Invalid email or password"}, status=401)

        access_token = issue_access_token(user)
        raw_refresh, hashed, expires_at = generate_refresh_token()
        RefreshToken.objects.create(user=user, token_hash=hashed, expires_at=expires_at)

        return Response(
            {"user": UserPublicSerializer(user).data, "accessToken": access_token, "refreshToken": raw_refresh}
        )


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw_refresh = request.data.get("refreshToken")
        if not raw_refresh:
            return Response({"error": "refreshToken is required"}, status=400)

        record = (
            RefreshToken.objects.select_related("user")
            .filter(token_hash=hash_token(raw_refresh), revoked=False, expires_at__gt=djtz.now())
            .first()
        )
        if not record:
            return Response({"error": "Refresh token is invalid or expired"}, status=401)

        return Response({"accessToken": issue_access_token(record.user)})


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw_refresh = request.data.get("refreshToken")
        if raw_refresh:
            RefreshToken.objects.filter(token_hash=hash_token(raw_refresh)).update(revoked=True)
        return Response(status=204)


class MeView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        return Response(UserPublicSerializer(user).data)


class InternalUserDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "User not found"}, status=404)
        return Response(UserPublicSerializer(user).data)


class OrganizationMembersView(APIView):
    permission_classes = [IsRole("org_admin")]

    def get(self, request):
        qs = User.objects.filter(organization_id=request.user.organization_id).order_by("-created_at")
        return Response(UserPublicSerializer(qs, many=True).data)


class OrganizationMemberStatusView(APIView):
    permission_classes = [IsRole("org_admin")]

    def patch(self, request, user_id):
        new_status = request.data.get("status")
        if new_status not in ("active", "suspended"):
            return Response({"error": "status must be 'active' or 'suspended'"}, status=400)
        result = User.objects.filter(id=user_id, organization_id=request.user.organization_id)
        if not result.exists():
            return Response({"error": "User not found in your organization"}, status=404)
        result.update(status=new_status)
        return Response(UserPublicSerializer(result.first()).data)


class AdminUserListView(APIView):
    permission_classes = [IsRole("platform_admin")]

    def get(self, request):
        qs = User.objects.order_by("-created_at")[:300]
        return Response(UserPublicSerializer(qs, many=True).data)
