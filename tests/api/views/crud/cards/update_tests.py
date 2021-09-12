import datetime
from http import HTTPStatus

import pytest

from api.models.cards import Card
from config import BASE_API_URL
from tests.api.test_data import TEST_CARD_DATA
from tests.conftest import create_test_card
from tests.testing_utils import exclude_time_values, remove_Z_in_datetime_value
from utils.serialization import serialize_object


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


@pytest.mark.django_db
def update_card_changed_after_created_data_test(logged_client):
    card = create_test_card()
    create_dict = {
        "added_datetime": datetime.datetime(year=2020, month=9, day=12),
        "changed_datetime": datetime.datetime(year=2020, month=9, day=11),
    }
    response = logged_client.put(f"/{BASE_API_URL}/cards/{card.id}", data=create_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
