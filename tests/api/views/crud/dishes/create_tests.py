import datetime
from http import HTTPStatus

import pytest
from django.db.models import NOT_PROVIDED

from api.models import Dish
from config import BASE_API_URL
from tests.api.test_data import TEST_DISH_DATA


@pytest.mark.django_db
def create_dish_test(logged_client):
    response = logged_client.post(f"/{BASE_API_URL}/dishes/", data=TEST_DISH_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["id"] == 1
    for key, value in TEST_DISH_DATA.items():
        assert response_data[key] == value
    assert response_data["changed_datetime"] is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "key_to_exclude",
    [
        field.name
        for field in Dish._meta.fields
        if (not field.null and field.default == NOT_PROVIDED) and field.name != "id" and "time" not in field.name
    ],
)
def create_dish_missing_data_test(key_to_exclude, logged_client):
    response = logged_client.post(
        f"/{BASE_API_URL}/dishes/",
        data={key: value for key, value in TEST_DISH_DATA.items() if key != key_to_exclude},
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def create_dish_invalid_data_test(logged_client):
    create_dict = {key: None for key in TEST_DISH_DATA.keys()}
    response = logged_client.post(f"/{BASE_API_URL}/dishes/", data=create_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def create_dish_changed_after_created_data_test(logged_client):
    create_dict = {
        **TEST_DISH_DATA,
        **{
            "added_datetime": datetime.datetime(year=2020, month=9, day=12),
            "changed_datetime": datetime.datetime(year=2020, month=9, day=11),
        },
    }
    response = logged_client.post(f"/{BASE_API_URL}/dishes/", data=create_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
