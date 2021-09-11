from typing import List

from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction, IntegrityError
from ninja import Router

from api.models.dishes import Dish
from api.schemas import DishSchemaOut, DishSchemaIn, DishUpdateSchemaIn
from api.views.views_utils import exclude_none_values

dishes_router = Router()


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
