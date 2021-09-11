from http import HTTPStatus

from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.http import HttpResponse
from ninja import Router

from api.api_auth import JWTAuth
from api.models import Dish
from api.models.cards import Card
from api.schemas import DishInCardSchema

cards_management_router = Router(auth=JWTAuth())


@cards_management_router.post("/add", summary="Add dish to card")
def add_dish_to_card(request: WSGIRequest, dish_in_card_data: DishInCardSchema):
    with transaction.atomic():
        card = Card.objects.get(id=dish_in_card_data.card_id)
        dish = Dish.objects.get(id=dish_in_card_data.dish_id)
        card.dishes.add(dish)
        card.save()
        return HttpResponse(status=HTTPStatus.OK)


@cards_management_router.post("/remove", summary="Remove dish to card")
def remove_dish_from_card(request: WSGIRequest, dish_in_card_data: DishInCardSchema):
    with transaction.atomic():
        card = Card.objects.get(id=dish_in_card_data.card_id)
        dish = Dish.objects.get(id=dish_in_card_data.dish_id)
        card.dishes.remove(dish)
        card.save()
        return HttpResponse(status=HTTPStatus.OK)
