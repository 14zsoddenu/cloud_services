from http import HTTPStatus

import pytest

from api.models.cards import Card
from config import BASE_API_URL
from tests.conftest import create_test_card


@pytest.mark.django_db
def delete_card_test(logged_client):
    card = create_test_card()
    assert Card.objects.count() == 1
    response = logged_client.delete(f"/{BASE_API_URL}/cards/{card.id}", content_type="application/json")
    assert response.status_code == HTTPStatus.OK
    assert Card.objects.count() == 0


@pytest.mark.django_db
def delete_non_existing_card_test(logged_client):
    response = logged_client.delete(f"/{BASE_API_URL}/cards/99", content_type="application/json")
    assert response.status_code == HTTPStatus.NOT_FOUND
