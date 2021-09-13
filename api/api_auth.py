from abc import ABC
from typing import Optional, Any

from django.http import HttpRequest
from ninja.compatibility import get_headers
from ninja.security.http import HttpAuthBase
from rest_framework_simplejwt.authentication import JWTAuthentication

from config import DISABLE_AUTH


class JWTAuth(HttpAuthBase, ABC):  # TODO: maybe HttpBasicAuthBase
    openapi_scheme = "jwt"
    header = "Authorization"

    def __call__(self, request: HttpRequest) -> Optional[Any]:
        if DISABLE_AUTH:
            return True
        headers = get_headers(request)
        auth_value = headers.get(self.header)
        if not auth_value:
            return None

        return self.authenticate(request)

    def authenticate(self, request: HttpRequest) -> Optional[Any]:
        jwt_auth = JWTAuthentication()
        user, validated_token = jwt_auth.authenticate(request)
        request.user = user
        return user
