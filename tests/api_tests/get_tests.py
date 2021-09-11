from http import HTTPStatus

import pytest
from django.http import JsonResponse

from config import BASE_API_URL
from tests import client
from tests.conftest import create_test_dish
from tests.testing_utils import empty_data_validation, remove_Z_in_datetime_value
from utils.serialization import serialize_object


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        "/dishes/99",
    ],
)
def object_not_found_test(url):
    empty_data_validation(
        url=f"/{BASE_API_URL}{url}",
        expected_result={"error": "Object not found"},
        status_code=HTTPStatus.NOT_FOUND,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        "/dishes/",
    ],
)
def empty_list_200_test(url):
    empty_data_validation(url=f"/{BASE_API_URL}{url}", expected_result=[], status_code=HTTPStatus.OK)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "object_name,create_func",
    [
        ("dishes", create_test_dish),
    ],
)
def get_endpoint_test(object_name, create_func):
    o = create_func()
    response: JsonResponse = client.get(f"/{BASE_API_URL}/{object_name}/{o.pk}")
    assert response.status_code == HTTPStatus.OK
    assert remove_Z_in_datetime_value(response.json()) == serialize_object(o)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "object_name,create_func",
    [
        ("dishes/", create_test_dish),
    ],
)
def get_list_endpoint_test(object_name, create_func):
    o_list = [create_func(i) for i in range(1, 3)]
    response: JsonResponse = client.get(f"/{BASE_API_URL}/{object_name}")
    assert response.status_code == HTTPStatus.OK
    assert remove_Z_in_datetime_value(response.json()) == [serialize_object(o) for o in o_list]
