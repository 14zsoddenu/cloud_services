import json
import traceback
from http import HTTPStatus
from typing import Any, Type, Mapping

from django.db import IntegrityError
from django.http.response import HttpResponseBase, JsonResponse, HttpResponse
from loguru import logger
from ninja import NinjaAPI
from ninja.renderers import BaseRenderer
from ninja.responses import NinjaJSONEncoder
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError

from api.models import Dish
from api.models.cards import Card
from api.schemas import ErrorSchema
from api.views.cards_management import cards_management_router
from api.views.crud.cards import cards_router
from api.views.crud.dishes import dishes_router
from api.views.public.menu import menu_router
from config import DEBUG_MODE
from utils.serialization import serialize_object, serialize_objects


class JsonRenderer(BaseRenderer):
    media_type = "application/json"
    encoder_class: Type[json.JSONEncoder] = NinjaJSONEncoder
    json_dumps_params: Mapping[str, Any] = {}

    def _render(self, request, data, *, response_status):
        if isinstance(data, HttpResponseBase):
            return data
        try:
            return JsonResponse(serialize_object(data), safe=False, status=HTTPStatus.OK)
        except:
            try:
                return JsonResponse(serialize_objects(data), safe=False, status=HTTPStatus.OK)
            except:
                try:
                    return JsonResponse(data.dict(), safe=False, status=HTTPStatus.OK)
                except:
                    try:
                        return JsonResponse(data, safe=False, status=HTTPStatus.OK)
                    except:
                        try:
                            return HttpResponse(content=data, status=HTTPStatus.OK)
                        except:
                            logger.error(traceback.format_exc())
                            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

    def get_origin_host(self, origin: str):
        return origin.replace("https://", "").replace("http://", "")

    def render(self, *args, **kwargs):
        response = self._render(*args, **kwargs)
        return response


api = NinjaAPI(title="Cloud Services", renderer=JsonRenderer())
api.add_router("/dishes/", dishes_router)
api.add_router("/cards/", cards_router)
api.add_router("/manage/", cards_management_router)
api.add_router("/menu/", menu_router)


def object_not_found(request, exc):
    try:
        raise exc
    except Exception:
        return api.create_response(request, ErrorSchema(error="Object not found"), status=HTTPStatus.NOT_FOUND)


def multiple_objects(request, exc):
    try:
        raise exc
    except Exception:
        return api.create_response(
            request, ErrorSchema(error=traceback.format_exc()).dict(), status=HTTPStatus.MULTIPLE_CHOICES
        )


def internal_error_handler(request, exc):
    try:
        raise exc
    except Exception:
        logger.error(traceback.format_exc())
        return api.create_response(
            request, ErrorSchema(error=traceback.format_exc()).dict(), status=HTTPStatus.INTERNAL_SERVER_ERROR
        )


def integrity_error_handler(request, exc):
    try:
        raise exc
    except IntegrityError as e:
        logger.warning(traceback.format_exc())
        return HttpResponse(content=str(e), status=HTTPStatus.BAD_REQUEST)


def invalid_token_handler(request, exc):
    return api.create_response(request, ErrorSchema(error="Invalid token", status=HTTPStatus.UNAUTHORIZED))


def token_error_handler(request, exc):
    return api.create_response(request, ErrorSchema(error="Token error", status=HTTPStatus.UNAUTHORIZED))


def authentication_failed_handler(request, exc):
    return api.create_response(request, ErrorSchema(error="Authentication failed", status=HTTPStatus.UNAUTHORIZED))


# TODO
for model_class in [Dish, Card]:
    api.add_exception_handler(model_class.DoesNotExist, object_not_found)
    api.add_exception_handler(model_class.MultipleObjectsReturned, multiple_objects)

api.add_exception_handler(IntegrityError, integrity_error_handler)

api.add_exception_handler(AuthenticationFailed, authentication_failed_handler)
api.add_exception_handler(InvalidToken, invalid_token_handler)
api.add_exception_handler(TokenError, token_error_handler)

if DEBUG_MODE:
    api.add_exception_handler(Exception, internal_error_handler)
