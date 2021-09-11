from typing import List

from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction, IntegrityError
from ninja import Router

from api.api_auth import JWTAuth
from api.models.cards import Card
from api.schemas import CardSchemaOut, CardSchemaIn, CardUpdateSchemaIn
from api.views.views_utils import exclude_none_values

cards_router = Router(auth=JWTAuth())


@cards_router.get("/", summary="Get all cards", response=List[CardSchemaOut])
def get_all_cards(request: WSGIRequest):
    return Card.objects.all()


@cards_router.get("/{id}", summary="Get card by ID", response=CardSchemaOut)
def get_card_by_id(request: WSGIRequest, id: int):
    return Card.objects.get(id=id)


@cards_router.post("/", summary="Create card", response=CardSchemaOut)
def create_card(request: WSGIRequest, card_data: CardSchemaIn):
    with transaction.atomic():
        return Card.objects.create(**card_data.dict())


@cards_router.put("/{id}", summary="Update card", response=CardSchemaOut)
def update_card(request: WSGIRequest, id: int, card_data: CardUpdateSchemaIn):
    with transaction.atomic():
        update_dict = exclude_none_values(card_data.dict())
        Card.objects.update(id=id, **update_dict)
        return Card.objects.get(id=id)


@cards_router.delete("/{id}", summary="Delete card", response=bool)
def delete_card(request: WSGIRequest, id: int):
    with transaction.atomic():
        card = Card.objects.get(id=id)
        try:
            card.delete()
            return True
        except IntegrityError:
            return False
