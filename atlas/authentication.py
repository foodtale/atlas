from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from atlas.models.user import UserSession


class SessionTokenAuthentication(BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        authorization = request.headers.get("Authorization")

        if not authorization:
            return None

        try:
            keyword, session_token = authorization.split(" ", 1)
        except ValueError:
            raise AuthenticationFailed(
                {
                    "code": "INVALID_AUTHORIZATION_HEADER",
                    "message": "Invalid authorization header.",
                }
            )

        if keyword != self.keyword:
            raise AuthenticationFailed(
                {
                    "code": "INVALID_AUTHORIZATION_HEADER",
                    "message": "Invalid authorization header.",
                }
            )

        session = (
            UserSession.objects.select_related("user")
            .filter(session_token=session_token)
            .first()
        )

        if not session:
            raise AuthenticationFailed(
                {
                    "code": "INVALID_SESSION",
                    "message": "Invalid session.",
                }
            )

        if session.is_revoked:
            raise AuthenticationFailed(
                {
                    "code": "SESSION_REVOKED",
                    "message": "Session revoked.",
                }
            )

        if session.is_expired:
            raise AuthenticationFailed(
                {
                    "code": "SESSION_EXPIRED",
                    "message": "Session expired.",
                }
            )

        if session.user.is_blocked:
            raise PermissionDenied(
                {
                    "code": "USER_BLOCKED",
                    "message": "User account is blocked.",
                }
            )

        return (session.user, session)
