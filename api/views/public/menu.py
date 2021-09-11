import datetime
from typing import List, Any

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from loguru import logger
from ninja import Router, Schema, Query
from pydantic import validator

from api.models.cards import Card
from api.schemas import CardSchemaOut, CardPrettySchemaOut

menu_router = Router()

all_non_empty_cards_query_sorting_options = ("name", "-name", "dishes_count", "-dishes_count")


class AllNonEmptyCardsQuerySchema(Schema):
    name_contains: str = None
    added_datetime_from: datetime.datetime = None
    added_datetime_to: datetime.datetime = None
    changed_datetime_from: datetime.datetime = None
    changed_datetime_to: datetime.datetime = None

    sort_by: str = None

    @validator("sort_by", pre=True)
    def validate_sort_by(cls, value: Any) -> Any:
        if value in all_non_empty_cards_query_sorting_options:
            return value
        raise ValueError(f"sort_by fields can be any of {all_non_empty_cards_query_sorting_options}, not {value}")

    def filter_dict(self):
        result = {}
        for field_name in self.__fields__:
            if field_name == "sort_by":
                continue
            field_value = getattr(self, field_name)
            if field_value is not None:
                if "datetime_from" in field_name:
                    result[f"{field_name.replace('datetime_from', 'datetime')}__gte"] = field_value
                elif "datetime_to" in field_name:
                    result[f"{field_name.replace('datetime_to', 'datetime')}__lte"] = field_value
                elif "contains" in field_name:
                    result[f"{field_name.replace('_contains', '')}__contains"] = field_value
                else:
                    result[field_name] = field_value
        return result


@menu_router.get("/cards", summary="Get all cards that have dishes", response=List[CardSchemaOut])
def get_all_non_empty_cards(request: WSGIRequest, query_schema: AllNonEmptyCardsQuerySchema = Query(...)):
    result = Card.objects.annotate(dishes_count=Count("dishes")).filter(dishes_count__gt=0)
    filter_dict = query_schema.filter_dict()
    logger.debug(filter_dict)
    if len(filter_dict) > 0:
        result = result.filter(**filter_dict)
    if query_schema.sort_by is not None:
        result = result.order_by(query_schema.sort_by)

    result = result.distinct()
    logger.debug(sorted([c.id for c in result]))
    return result


@menu_router.get("/cards/{id}", summary="Get card details (including dishes)", response=CardPrettySchemaOut)
def get_pretty_card_by_id(request: WSGIRequest, id: int):
    return Card.objects.get(id=id)
