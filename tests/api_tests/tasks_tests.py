import datetime
from contextlib import suppress
from time import sleep

import pytest
from django.contrib.auth.models import User
from huey.contrib.djhuey import HUEY

from api.models import Dish
from api.tasks import (
    debug_ping_task,
    debug_periodic_ping_task,
    send_email_task,
    send_email_about_new_and_modified_dishes_from_yesterday_to_all_users_task,
    send_email_about_modified_dishes_from_yesterday_to_all_users_task,
)
from rediska import redis_db

huey = HUEY


def no_value_with_redis_key(key, seconds=5):
    time_to_appear = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    while datetime.datetime.utcnow() < time_to_appear:
        try:
            redis_db[key]
            sleep(0.01)
        except (TypeError, KeyError):
            return True
    return False


def wait_for_value_in_redis_key(key, value=None, seconds=5):
    time_to_appear = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    while datetime.datetime.utcnow() < time_to_appear:
        try:
            if (value is not None and redis_db[key] == value) or redis_db[key] is not None:
                return True
            else:
                sleep(0.01)
        except (TypeError, KeyError):
            sleep(0.01)
    return False


def debug_ping_task_test(redis_container):
    assert huey.enqueue(debug_ping_task.s()).get() == "pong"


def debug_periodic_ping_task_test(redis_container):
    debug_periodic_ping_task.s()
    assert wait_for_value_in_redis_key("debug_ping_task", "pong")


@pytest.mark.django_db(transaction=True)
def send_email_periodic_task_test(redis_container):
    user = User.objects.create(username="abc", password="abc")
    send_email_about_new_and_modified_dishes_from_yesterday_to_all_users_task()()
    assert wait_for_value_in_redis_key(f"send_email_task:{user.id}:called")


@pytest.mark.django_db(transaction=True)
def send_email_task_test(redis_container):
    user = User.objects.create(username="abc", password="abc")
    send_email_task(user.id, "Dummy Subject", "Dummy Message")()
    assert wait_for_value_in_redis_key(f"send_email_task:{user.id}:called")


@pytest.mark.django_db(transaction=True)
def send_email_about_old_and_new_dishes_periodic_task_test(redis_container):
    user = User.objects.create(username="abc", password="abc")
    with suppress(KeyError):
        redis_db.pop(f"send_email_task:{user.id}:called")
    assert no_value_with_redis_key(f"send_email_task:{user.id}:called")
    for i in range(3):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
        )
    for i in range(3, 6):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
            changed_datetime=(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
        )
    for i in range(6, 9):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=datetime.datetime.utcnow(),
            changed_datetime=datetime.datetime.utcnow(),
        )
    for i in range(9, 12):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=datetime.datetime.utcnow(),
        )
    send_email_about_new_and_modified_dishes_from_yesterday_to_all_users_task()()
    assert wait_for_value_in_redis_key(f"send_email_task:{user.id}:called")


@pytest.mark.django_db(transaction=True)
def send_email_about_old_dishes_periodic_task_test(redis_container):
    user = User.objects.create(username="abc", password="abc")
    with suppress(KeyError):
        redis_db.pop(f"send_email_task:{user.id}:called")
    assert no_value_with_redis_key(f"send_email_task:{user.id}:called")
    for i in range(3):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
        )
    for i in range(3, 6):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
            changed_datetime=(datetime.datetime.utcnow() - datetime.timedelta(days=1)),
        )
    for i in range(6, 9):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=datetime.datetime.utcnow(),
            changed_datetime=datetime.datetime.utcnow(),
        )
    for i in range(9, 12):
        Dish.objects.create(
            name=f"Dish{i}",
            price=i * 10,
            time_to_cook=datetime.timedelta(minutes=i * 3),
            added_datetime=datetime.datetime.utcnow(),
        )
    send_email_about_modified_dishes_from_yesterday_to_all_users_task()()
    assert wait_for_value_in_redis_key(f"send_email_task:{user.id}:called")
