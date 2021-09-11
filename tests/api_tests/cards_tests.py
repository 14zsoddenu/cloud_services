from http import HTTPStatus

import pytest
from django.db.models import NOT_PROVIDED

from api.models.cards import Card
from config import BASE_API_URL
from tests.api_tests.test_data import TEST_CARD_DATA
from tests.conftest import create_test_card
from tests.testing_utils import remove_Z_in_datetime_value, exclude_time_values
from utils.serialization import serialize_object


def unauthorized_create_card_test(anon_client):
    response = anon_client.post(f"/{BASE_API_URL}/cards/", data=TEST_CARD_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


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


def unauthorized_update_card_test(anon_client):
    response = anon_client.put(f"/{BASE_API_URL}/cards/{1}", data=TEST_CARD_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "key_to_exclude",
    [field.name for field in Card._meta.fields if field.name != "id" and "time" not in field.name],
)
def update_card_data_test(key_to_exclude, logged_client):
    card = create_test_card()
    update_dict = {key: value for key, value in TEST_CARD_DATA.items() if key != key_to_exclude}
    response = logged_client.put(f"/{BASE_API_URL}/cards/{card.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert exclude_time_values(remove_Z_in_datetime_value(response.json())) == exclude_time_values(
        {**serialize_object(card), **update_dict}
    )


@pytest.mark.django_db
def update_non_existing_card_data_test(logged_client):
    update_dict = {}
    response = logged_client.put(f"/{BASE_API_URL}/cards/99", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def update_card_invalid_data_test(logged_client):
    card = create_test_card()
    update_dict = {"name": None, "description": None}
    response = logged_client.put(f"/{BASE_API_URL}/cards/{card.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
def update_card_data_not_available_name_test(logged_client):
    pre_card = create_test_card()
    card = create_test_card(2)
    update_dict = {"name": pre_card.name}
    response = logged_client.put(f"/{BASE_API_URL}/cards/{card.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.BAD_REQUEST
