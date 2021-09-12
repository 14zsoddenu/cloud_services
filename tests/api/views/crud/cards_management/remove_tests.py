from http import HTTPStatus

import pytest

from api.schemas import DishInCardSchema
from config import BASE_API_URL
from tests.conftest import create_test_dish, create_test_card


@pytest.mark.django_db
def remove_dish_from_card_test(logged_client):
    dish = create_test_dish()
    card = create_test_card()
    request_data = {"dish_id": dish.id, "card_id": card.id}
    response = logged_client.post(f"/{BASE_API_URL}/manage/remove", data=request_data, content_type="application/json")
    assert response.status_code == HTTPStatus.OK

    card.refresh_from_db()
    assert dish not in card.dishes.all()


@pytest.mark.django_db
def remove_non_existing_dish_from_card_test(logged_client):
    card = create_test_card()
    request_data = {"dish_id": 99, "card_id": card.id}
    response = logged_client.post(f"/{BASE_API_URL}/manage/remove", data=request_data, content_type="application/json")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def remove_dish_from_non_existing_card_test(logged_client):
    dish = create_test_dish()
    request_data = {"dish_id": dish.id, "card_id": 99}
    response = logged_client.post(f"/{BASE_API_URL}/manage/remove", data=request_data, content_type="application/json")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def remove_non_existing_dish_from_non_existing_card_test(logged_client):
    request_data = {"dish_id": 99, "card_id": 99}
    response = logged_client.post(f"/{BASE_API_URL}/manage/remove", data=request_data, content_type="application/json")
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def remove_dish_from_card_invalid_data_test(logged_client):
    request_data = {"dish_id": "abc", "card_id": "qwe"}
    response = logged_client.post(f"/{BASE_API_URL}/manage/remove", data=request_data, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing_field",
    DishInCardSchema.__fields__,
)
def remove_dish_from_card_missing_data_test(missing_field, logged_client):
    dish = create_test_dish()
    card = create_test_card()
    raw_request_data = {"dish_id": dish.id, "card_id": card.id}
    request_data = {key: value for key, value in raw_request_data.items() if key != missing_field}
    response = logged_client.post(f"/{BASE_API_URL}/manage/remove", data=request_data, content_type="application/json")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
