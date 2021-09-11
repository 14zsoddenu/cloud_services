from http import HTTPStatus

import pytest
from django.db.models import NOT_PROVIDED

from api.models.cards import Card
from config import BASE_API_URL
from tests import client
from tests.conftest import create_test_card
from tests.testing_utils import remove_Z_in_datetime_value
from utils.serialization import serialize_object

TEST_CARD_DATA = {
    "name": "test_card",
    "description": "test_card_description",
}


@pytest.mark.django_db
def create_card_test():
    response = client.post(f"/{BASE_API_URL}/cards/", data=TEST_CARD_DATA, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["id"] == 1
    for key, value in TEST_CARD_DATA.items():
        assert response_data[key] == value
    assert response_data["changed_datetime"] is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "key_to_exclude",
    [
        field.name
        for field in Card._meta.fields
        if (not field.null and field.default == NOT_PROVIDED) and field.name != "id" and "time" not in field.name
    ],
)
def create_card_missing_data_test(key_to_exclude):
    response = client.post(
        f"/{BASE_API_URL}/cards/",
        data={key: value for key, value in TEST_CARD_DATA.items() if key != key_to_exclude},
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
    [field.name for field in Card._meta.fields if field.name != "id" and "time" not in field.name],
)
def update_card_data_test(key_to_exclude):
    card = create_test_card()
    update_dict = {key: value for key, value in TEST_CARD_DATA.items() if key != key_to_exclude}
    response = client.put(f"/{BASE_API_URL}/cards/{card.id}", data=update_dict, content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert exclude_time_values(remove_Z_in_datetime_value(response.json())) == exclude_time_values(
        {**serialize_object(card), **update_dict}
    )
