import datetime
import random

import pytest
from django.contrib.auth.models import User
from django.test import Client
from rest_framework_simplejwt.tokens import RefreshToken

from api.models.cards import Card
from api.models.dishes import Dish
from config import DEV_REDIS
from constants import REDIS_CONTAINER_CONFIG
from utils.containers import wait_for_redis_startup, run_container_from_config


def create_test_dish(number=1):
    return Dish.objects.get_or_create(
        name=f"Dish{number}",
        description=f"DishDescription{number}",
        price=random.randint(0, 100) + random.randint(0, 100) / 100,
        time_to_cook=datetime.timedelta(minutes=random.randint(0, 10) * number),
        is_vegan=number % 2 == 0,
    )[0]


def create_test_card(number=1):
    dishes = [create_test_dish(i) for i in range(number * 3)]
    card = Card.objects.get_or_create(name=f"Card{number}", description=f"CardDescription{number}")[0]
    for dish in dishes:
        card.dishes.add(dish)
    card.save()
    return card


@pytest.fixture
def logged_client(db):
    user = User.objects.create_user(username="john", email="js@js.com", password="js.sj")
    refresh = RefreshToken.for_user(user)
    client = Client(HTTP_AUTHORIZATION=f"JWT {refresh.access_token}")
    return client


@pytest.fixture(scope="session")
def anon_client():
    client = Client()
    return client


def redis_container_base():
    if DEV_REDIS:
        with run_container_from_config(REDIS_CONTAINER_CONFIG, wait_for_redis_startup) as c:
            yield c
    else:
        yield


redis_container = pytest.fixture(scope="session")(redis_container_base)
redis_container_fast = pytest.fixture(scope="function")(redis_container_base)
