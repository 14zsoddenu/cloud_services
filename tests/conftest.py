import datetime
import random

from api.models.cards import Card
from api.models.dishes import Dish


def create_test_dish(number=1):
    return Dish.objects.get_or_create(
        name=f"Dish{number}",
        description=f"DishDescription{number}",
        price=random.randint(0, 100) + random.randint(0, 100) / 100,
        time_to_cook=datetime.timedelta(minutes=random.randint(0, 10) * number),
        is_vegan=number % 2 == 0,
    )[0]


def create_test_card(number=1):
    dishes = [create_test_dish(i) for i in range(3)]
    card = Card.objects.get_or_create(name=f"Card{number}", description=f"CardDescription{number}")[0]
    for dish in dishes:
        card.dishes.add(dish)
    card.save()
    return card
