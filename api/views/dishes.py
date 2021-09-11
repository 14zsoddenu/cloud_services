from typing import List

from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction, IntegrityError
from ninja import Router
from ninja.orm import create_schema

from api.models.dishes import Dish
from api.schemas import create_update_schema

dishes_router = Router()

DishSchemaOut = create_schema(Dish, name="DishSchemaOut")
DishSchemaIn = create_schema(Dish, name="DishSchemaIn", exclude=["id"])

DishUpdateSchemaIn = create_update_schema(Dish, name="DishUpdateSchemaIn", exclude=["id"])


@dishes_router.get("/", summary="Get all dishes", response=List[DishSchemaOut])
def create_dish(request: WSGIRequest):
    return Dish.objects.all()


@dishes_router.get("/{id}", summary="Get dish by ID", response=DishSchemaOut)
def get_dish_by_id(request: WSGIRequest, id: int):
    return Dish.objects.get(id=id)


@dishes_router.post("/", summary="Create dish", response=DishSchemaOut)
def create_dish(request: WSGIRequest, dish_data: DishSchemaIn):
    with transaction.atomic():
        return Dish.objects.create(**dish_data.dict())


def exclude_none_values(d):
    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            if value is not None:
                processed_value = exclude_none_values(value)
                if processed_value is not None:
                    result[key] = processed_value
    elif isinstance(d, list):
        result = []
        for item in d:
            processed_value = exclude_none_values(item)
            if processed_value is not None:
                result.append(processed_value)
    else:
        return d
    return result


@dishes_router.put("/{id}", summary="Update dish", response=DishSchemaOut)
def update_dish(request: WSGIRequest, id: int, dish_data: DishUpdateSchemaIn):
    with transaction.atomic():
        update_dict = exclude_none_values(dish_data.dict())
        Dish.objects.update(id=id, **update_dict)
        return Dish.objects.get(id=id)


@dishes_router.delete("/{id}", summary="Delete dish", response=bool)
def delete_dish(request: WSGIRequest, id: int):
    with transaction.atomic():
        dish = Dish.objects.get(id=id)
        try:
            dish.delete()
            return True
        except IntegrityError:
            return False
