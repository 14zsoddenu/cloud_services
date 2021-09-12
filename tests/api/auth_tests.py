from http import HTTPStatus

import pytest

from config import BASE_API_URL


@pytest.mark.parametrize(
    "url,method",
    [
        ("cards/", "get"),
        ("cards/1", "get"),
        ("cards/", "post"),
        ("cards/1", "put"),
        ("cards/1", "delete"),
        ("dishes/", "get"),
        ("dishes/", "post"),
        ("dishes/1", "get"),
        ("dishes/1", "put"),
        ("dishes/1", "delete"),
        ("manage/add", "post"),
        ("manage/remove", "post"),
    ],
)
def unathorized_access_to_private_api_test(url, method, anon_client):
    requests_methods_map = {
        "get": anon_client.get,
        "post": anon_client.post,
        "put": anon_client.put,
        "delete": anon_client.delete,
    }
    full_url = f"/{BASE_API_URL}/{url}"
    request_func = requests_methods_map[method]
    response = request_func(full_url, content_type="application/json")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,method",
    [
        ("menu/cards", "get"),
        ("menu/cards/1", "get"),
    ],
)
def free_access_to_public_api_test(url, method, anon_client):
    requests_methods_map = {
        "get": anon_client.get,
        "post": anon_client.post,
        "put": anon_client.put,
        "delete": anon_client.delete,
    }
    full_url = f"/{BASE_API_URL}/{url}"
    request_func = requests_methods_map[method]
    response = request_func(full_url, content_type="application/json")
    assert response.status_code != HTTPStatus.UNAUTHORIZED
