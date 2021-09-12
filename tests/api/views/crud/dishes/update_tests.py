import datetime
from http import HTTPStatus

import pytest
from django.utils.duration import duration_iso_string

from api.models import Dish
from config import BASE_API_URL
from tests.api.test_data import TEST_DISH_DATA
from tests.conftest import create_test_dish
from tests.testing_utils import exclude_time_values, remove_Z_in_datetime_value
from utils.serialization import serialize_object


@pytest.mark.django_db
def update_dish_data_test(logged_client):
    dish = create_test_dish()
    update_dict = {
        "name": "test_dish111",
        "description": "test_dish_description111",
        "price": 99111.75,
        "time_to_cook": duration_iso_string(datetime.timedelta(minutes=130)),
        "is_vegan": False,
    }
    response = logged_client.put(f"/{BASE_API_URL}/dishes/{dish.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert exclude_time_values(remove_Z_in_datetime_value(response.json())) == exclude_time_values(
        {**serialize_object(dish, exclude=["image"]), **update_dict}
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "key_to_exclude",
    [field.name for field in Dish._meta.fields if field.name != "id" and "time" not in field.name],
)
def update_dish_data_missing_data_test(key_to_exclude, logged_client):
    dish = create_test_dish()
    update_dict = {key: value for key, value in TEST_DISH_DATA.items() if key != key_to_exclude}
    response = logged_client.put(f"/{BASE_API_URL}/dishes/{dish.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert exclude_time_values(remove_Z_in_datetime_value(response.json())) == exclude_time_values(
        {**serialize_object(dish, exclude=["image"]), **update_dict}
    )


@pytest.mark.django_db
def update_dish_data_invalid_test(logged_client):
    dish = create_test_dish()
    update_dict = {key: None for key in TEST_DISH_DATA.keys()}
    response = logged_client.put(f"/{BASE_API_URL}/dishes/{dish.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def update_dish_changed_after_created_data_test(logged_client):
    dish = create_test_dish()
    create_dict = {
        "added_datetime": datetime.datetime(year=2020, month=9, day=12),
        "changed_datetime": datetime.datetime(year=2020, month=9, day=11),
    }
    response = logged_client.put(f"/{BASE_API_URL}/dishes/{dish.id}", data=create_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
