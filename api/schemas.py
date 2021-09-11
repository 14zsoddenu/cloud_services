from ninja import Schema
from ninja.orm import create_schema

from api.models import Dish
from api.models.cards import Card


class ErrorSchema(Schema):
    error: str


def create_update_schema(*args, **kwargs):
    result = create_schema(*args, **kwargs)
    for field_name, field in result.__fields__.items():
        field.required = False
    return result


CardSchemaOut = create_schema(Card, name="CardSchemaOut")
CardSchemaIn = create_schema(Card, name="CardSchemaIn", exclude=["id", "dishes"])
CardUpdateSchemaIn = create_update_schema(Card, name="CardUpdateSchemaIn", exclude=["id"])
DishSchemaOut = create_schema(Dish, name="DishSchemaOut")
DishSchemaIn = create_schema(Dish, name="DishSchemaIn", exclude=["id"])
DishUpdateSchemaIn = create_update_schema(Dish, name="DishUpdateSchemaIn", exclude=["id"])

CardPrettySchemaOut = create_schema(Card, name="CardPrettySchemaOut", depth=2)


class DishInCardSchema(Schema):
    card_id: int
    dish_id: int
