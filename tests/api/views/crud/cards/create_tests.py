import datetime
from http import HTTPStatus

import pytest
from django.db.models import NOT_PROVIDED

from api.models.cards import Card
from config import BASE_API_URL
from tests.api.test_data import TEST_CARD_DATA
from utils.serialization import serialize_object


@pytest.mark.django_db
def create_card_test(logged_client):
    response = logged_client.post(f"/{BASE_API_URL}/cards/", data=TEST_CARD_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["id"] == 1
    for key, value in TEST_CARD_DATA.items():
        assert response_data[key] == value
    assert response_data["changed_datetime"] is None


@pytest.mark.django_db
def create_card_with_same_name_test(logged_client):
    response = logged_client.post(f"/{BASE_API_URL}/cards/", data=TEST_CARD_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    response = logged_client.post(f"/{BASE_API_URL}/cards/", data=TEST_CARD_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize(
    "key_to_exclude",
    [
        field.name
        for field in Card._meta.fields
        if (not field.null and field.default == NOT_PROVIDED) and field.name != "id" and "time" not in field.name
    ],
)
def create_card_missing_data_test(key_to_exclude, logged_client):
    response = logged_client.post(
        f"/{BASE_API_URL}/cards/",
        data={key: value for key, value in TEST_CARD_DATA.items() if key != key_to_exclude},
        content_type="application/json",
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def create_card_invalid_data_test(logged_client):
    create_dict = {"name": None, "description": None}
    response = logged_client.post(f"/{BASE_API_URL}/cards/", data=create_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def create_card_changed_after_created_data_test(logged_client):
    create_dict = {
        **TEST_CARD_DATA,
        **{
            "added_datetime": datetime.datetime(year=2020, month=9, day=12),
            "changed_datetime": datetime.datetime(year=2020, month=9, day=11),
        },
    }
    response = logged_client.post(f"/{BASE_API_URL}/cards/", data=create_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
