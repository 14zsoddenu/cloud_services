# demo.py
import datetime

from django.contrib.auth.models import User
from huey import crontab
from huey.contrib.djhuey import HUEY
from loguru import logger

from api.models import Dish
from api.schemas import DishSchemaOut
from config import TEST_MODE
from rediska import redis_db

huey = HUEY


def format_dish_for_email(dish: Dish):
    # dummy
    return DishSchemaOut.from_orm(dish).json()


def send_email(user: User, *args, **kwargs):
    logger.info(f"Sending email to {user.username} ({user.email})")
    user.email_user(*args, **kwargs)


@huey.task(expires=60 * 60 * 24)
def send_email_task(user_id, subject, message, *args, **kwargs):
    logger.debug(f"Trying to send email to user {user_id}")
    try:
        user = User.objects.get(id=user_id)
        if not TEST_MODE:
            return send_email(user, subject, message, *args, **kwargs)
        else:
            logger.debug(f"To: {user.username}\n{subject}\n{message}")
    except User.DoesNotExist:
        logger.error(f"There is no user with id {user_id}")
    finally:
        redis_db[f"send_email_task:{user_id}:called"] = f"{subject} -> {datetime.datetime.utcnow()}"


@huey.periodic_task(crontab(hour=10))
def send_email_about_modified_dishes_from_yesterday_to_all_users_task(*args, **kwargs):
    users = User.objects.all()

    yesterday_modified_dishes = Dish.objects.filter(
        changed_datetime__gte=(datetime.datetime.utcnow().date() - datetime.timedelta(days=1)),
        changed_datetime__lt=(datetime.datetime.utcnow().date()),
    )
    subject = """Check out old but gold deals!"""
    message = "Modified recipies dishes:\n" + "\n".join(
        format_dish_for_email(dish=dish) for dish in yesterday_modified_dishes
    )

    for user in users:
        send_email_task(user.id, subject, message, *args, **kwargs)


@huey.periodic_task(crontab(hour=10))
def send_email_about_new_and_modified_dishes_from_yesterday_to_all_users_task(*args, **kwargs):
    users = User.objects.all()

    yesterday_added_dishes = Dish.objects.filter(
        added_datetime__gte=(datetime.datetime.utcnow().date() - datetime.timedelta(days=1)),
        added_datetime__lt=(datetime.datetime.utcnow().date()),
    )
    yesterday_modified_dishes = Dish.objects.filter(
        changed_datetime__gte=(datetime.datetime.utcnow().date() - datetime.timedelta(days=1)),
        changed_datetime__lt=(datetime.datetime.utcnow().date()),
    )
    subject = """Check out new deals!"""
    message = (
        "New dishes:\n"
        + "\n".join(format_dish_for_email(dish=dish) for dish in yesterday_added_dishes)
        + "\nModified recipies dishes:\n"
        + "\n".join(format_dish_for_email(dish=dish) for dish in yesterday_modified_dishes)
    )

    for user in users:
        send_email_task(user.id, subject, message, *args, **kwargs)


@huey.task()
def debug_ping_task():
    redis_db["debug_ping_task"] = "pong"
    return "pong"


@huey.periodic_task(crontab(minute=1))
def debug_periodic_ping_task():
    debug_ping_task()
