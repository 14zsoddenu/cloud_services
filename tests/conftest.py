import datetime
import random

from api.models.dishes import Dish


def create_test_dish(number=1):
    return Dish.objects.get_or_create(
        name=f"Dish{number}",
        description=f"DishDescription{number}",
        price=random.randint(0, 100) + random.randint(0, 100) / 100,
        time_to_cook=datetime.timedelta(minutes=random.randint(0, 10) * number),
        is_vegan=number % 2 == 0,
    )[0]
