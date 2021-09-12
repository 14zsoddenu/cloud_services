from http import HTTPStatus

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from loguru import logger
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def index(request: WSGIRequest):
    logger.info(str(request))
    logger.info(str(request.user))
    logger.info(str(request.user.username))
    return JsonResponse(
        f"Hello, {request.user.username if request.user.username else 'Anon'}! Cloud Services Backend is online!",
        safe=False,
        status=HTTPStatus.OK,
    )
