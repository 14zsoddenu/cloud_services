import datetime
from http import HTTPStatus

import pytest
from django.db.models import NOT_PROVIDED
from django.utils.duration import duration_iso_string

from api.models import Dish
from config import BASE_API_URL
from tests import client
from tests.conftest import create_test_dish
from tests.testing_utils import remove_Z_in_datetime_value
from utils.serialization import serialize_object

TEST_DISH_DATA = {
    "name": "test_dish",
    "description": "test_dish_description",
    "price": 99.75,
    "time_to_cook": duration_iso_string(datetime.timedelta(minutes=30)),
    "is_vegan": True,
}


@pytest.mark.django_db
def create_dish_test():
    response = client.post(f"/{BASE_API_URL}/dishes/", data=TEST_DISH_DATA, content_type="application/json")
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
def create_dish_missing_data_test(key_to_exclude):
    response = client.post(
        f"/{BASE_API_URL}/dishes/",
        data={key: value for key, value in TEST_DISH_DATA.items() if key != key_to_exclude},
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def exclude_time_values(d):
    if isinstance(d, dict):
        result = {}
        for key, value in d.items():
            if not "time" in key:
                result[key] = value
    else:
        return d
    return result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "key_to_exclude",
    [field.name for field in Dish._meta.fields if field.name != "id" and "time" not in field.name],
)
def update_dish_data_test(key_to_exclude):
    dish = create_test_dish()
    update_dict = {key: value for key, value in TEST_DISH_DATA.items() if key != key_to_exclude}
    response = client.put(f"/{BASE_API_URL}/dishes/{dish.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert exclude_time_values(remove_Z_in_datetime_value(response.json())) == exclude_time_values(
        {**serialize_object(dish), **update_dict}
    )
