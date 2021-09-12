import io
from http import HTTPStatus

import pytest
from django.http import HttpResponse

from config import BASE_API_URL
from tests import CAT_IMAGE_PATH
from tests.conftest import create_test_dish


@pytest.mark.django_db
def get_dish_image_by_id_test(logged_client):
    dish = create_test_dish()
    with open(CAT_IMAGE_PATH, "rb") as cat_file:
        binary_cat = cat_file.read()
        dish.image = binary_cat
    dish.save()

    response: HttpResponse = logged_client.get(f"/{BASE_API_URL}/dishes/{dish.id}/image.jpg")
    assert response.status_code == HTTPStatus.OK
    assert response.content == binary_cat


@pytest.mark.django_db
def try_get_dish_non_existing_image_test(logged_client):
    dish = create_test_dish()

    response: HttpResponse = logged_client.get(f"/{BASE_API_URL}/dishes/{dish.id}/image.jpg")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def try_get_non_existing_dish_image_test(logged_client):
    response: HttpResponse = logged_client.get(f"/{BASE_API_URL}/dishes/99/image.jpg")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def post_dish_image_by_id_test(logged_client):
    dish = create_test_dish()

    with open(CAT_IMAGE_PATH, "rb") as cat_file:
        binary_cat = cat_file.read()

    response: HttpResponse = logged_client.post(
        f"/{BASE_API_URL}/dishes/{dish.id}/image.jpg",
        data={"file": (io.BytesIO(binary_cat), f"{dish.id}.jpg")},
    )
    assert response.status_code == HTTPStatus.OK
    dish.refresh_from_db()
    assert dish.image == binary_cat


@pytest.mark.django_db
def try_post_dish_non_existing_image_test(logged_client):
    dish = create_test_dish()

    response: HttpResponse = logged_client.post(
        f"/{BASE_API_URL}/dishes/{dish.id}/image.jpg", data={"file": (None, f"{dish.id}.jpg")}
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def try_post_non_existing_dish_image_test(logged_client):
    with open(CAT_IMAGE_PATH, "rb") as cat_file:
        binary_cat = cat_file.read()

    response: HttpResponse = logged_client.post(
        f"/{BASE_API_URL}/dishes/99/image.jpg",
        data={"file": (io.BytesIO(binary_cat), f"99.jpg")},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
