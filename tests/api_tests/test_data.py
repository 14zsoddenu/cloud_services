import datetime

from django.utils.duration import duration_iso_string

TEST_CARD_DATA = {
    "name": "test_card",
    "description": "test_card_description",
}
TEST_DISH_DATA = {
    "name": "test_dish",
    "description": "test_dish_description",
    "price": 99.75,
    "time_to_cook": duration_iso_string(datetime.timedelta(minutes=30)),
    "is_vegan": True,
}
