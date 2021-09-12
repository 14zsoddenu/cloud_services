from typing import Any

from ninja import Schema
from ninja.orm import create_schema
from pydantic import root_validator

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
_CardSchemaIn = create_schema(Card, name="CardSchemaIn", exclude=["id", "dishes"])


class CardSchemaIn(_CardSchemaIn):
    @root_validator
    def validate_changed_after_added(cls, values) -> Any:
        added_datetime, changed_datetime = values["added_datetime"], values["changed_datetime"]
        if changed_datetime is not None and not changed_datetime > added_datetime:
            raise ValueError("Card could not change before it's creation")
        return values


_CardUpdateSchemaIn = create_update_schema(Card, name="CardUpdateSchemaIn", exclude=["id"])


class CardUpdateSchemaIn(_CardUpdateSchemaIn):
    @root_validator
    def validate_changed_after_added(cls, values) -> Any:
        added_datetime, changed_datetime = values["added_datetime"], values["changed_datetime"]
        if changed_datetime is not None and added_datetime is not None and not changed_datetime > added_datetime:
            raise ValueError("Card could not change before it's creation")
        return values


DishSchemaOut = create_schema(Dish, name="DishSchemaOut", exclude=["image"])
_DishSchemaIn = create_schema(Dish, name="DishSchemaIn", exclude=["id", "image"])


class DishSchemaIn(_DishSchemaIn):
    @root_validator
    def validate_changed_after_added(cls, values) -> Any:
        added_datetime, changed_datetime = values["added_datetime"], values["changed_datetime"]
        if changed_datetime is not None and not changed_datetime > added_datetime:
            raise ValueError("Card could not change before it's creation")
        return values


_DishUpdateSchemaIn = create_update_schema(Dish, name="DishUpdateSchemaIn", exclude=["id", "image"])


class DishUpdateSchemaIn(_DishUpdateSchemaIn):
    @root_validator
    def validate_changed_after_added(cls, values) -> Any:
        added_datetime, changed_datetime = values["added_datetime"], values["changed_datetime"]
        if changed_datetime is not None and added_datetime is not None and not changed_datetime > added_datetime:
            raise ValueError("Card could not change before it's creation")
        return values


CardPrettySchemaOut = create_schema(Card, name="CardPrettySchemaOut", depth=2)


class DishInCardSchema(Schema):
    card_id: int
    dish_id: int
