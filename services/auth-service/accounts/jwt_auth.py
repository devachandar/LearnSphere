"""
Stateless JWT authentication shared across every LearnSphere service.

Auth Service is the only service with a real Postgres `users` table and
the only one that issues tokens. Every other service verifies the
signature with the shared HS256 secret and trusts the claims inside -
`userId`, `email`, `role`, `organizationId`, `fullName` - matching the
original Node token shape exactly, so the React frontend needed zero
changes when the backend moved to Django.
"""
import jwt
from django.conf import settings
from rest_framework import authentication, exceptions


class LearnSphereUser:
    """A non-persisted stand-in for django.contrib.auth.User, built entirely
    from JWT claims."""

    is_authenticated = True

    def __init__(self, claims):
        self.id = claims.get("userId")
        self.email = claims.get("email")
        self.role = claims.get("role")
        self.organization_id = claims.get("organizationId")
        self.full_name = claims.get("fullName")

    def __str__(self):
        return self.email or str(self.id)


class StatelessJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None

        token = header.split(" ", 1)[1]
        try:
            claims = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Access token has expired")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid access token")

        return (LearnSphereUser(claims), None)
