from http import HTTPStatus
from typing import List

from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction, IntegrityError
from django.http import HttpResponse
from ninja import Router, UploadedFile, File

from api.api_auth import JWTAuth
from api.models.dishes import Dish
from api.schemas import DishSchemaOut, DishSchemaIn, DishUpdateSchemaIn
from api.views.views_utils import exclude_none_values

dishes_router = Router(auth=JWTAuth())


@dishes_router.get("/", summary="Get all dishes", response=List[DishSchemaOut])
def get_all_dishes(request: WSGIRequest):
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


@dishes_router.get("/{id}/image.jpg", summary="Get dish image by ID")
def get_dish_image_by_id(request: WSGIRequest, id: int):
    image = Dish.objects.get(id=id).image
    if image is None:
        return HttpResponse(status=HTTPStatus.NOT_FOUND)

    return HttpResponse(image, status=HTTPStatus.OK, content_type="image/jpeg")


@dishes_router.post("/{id}/image.jpg", summary="Post image to dish by ID")
def post_image_to_dish_by_id(request: WSGIRequest, id: int, file: UploadedFile = File(...)):
    dish = Dish.objects.get(id=id)
    dish.image = file.read()
    dish.save()
    return HttpResponse(status=HTTPStatus.OK)
