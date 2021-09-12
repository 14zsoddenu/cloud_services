from http import HTTPStatus

import pytest

from api.models import Dish
from config import BASE_API_URL
from tests.conftest import create_test_dish


@pytest.mark.django_db
def delete_dish_test(logged_client):
    dish = create_test_dish()
    assert Dish.objects.count() == 1
    response = logged_client.delete(f"/{BASE_API_URL}/dishes/{dish.id}", content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert Dish.objects.count() == 0


@pytest.mark.django_db
def delete_non_existing_dish_test(logged_client):
    response = logged_client.delete(f"/{BASE_API_URL}/dishes/99", content_type="application/json")
    assert response.status_code == HTTPStatus.NOT_FOUND
