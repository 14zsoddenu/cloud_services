import datetime
import itertools
import json
import random
from http import HTTPStatus

import pytest
from django.db import transaction
from django.http import JsonResponse
from ninja.responses import NinjaJSONEncoder

from api.models import Dish
from api.models.cards import Card
from api.schemas import CardSchemaIn, CardPrettySchemaOut
from config import BASE_API_URL
from tests.conftest import create_test_card
from tests.testing_utils import remove_Z_in_datetime_value
from utils.serialization import serialize_object


@pytest.mark.django_db
def get_all_non_empty_cards_test(anon_client):
    card = create_test_card()
    response: JsonResponse = anon_client.get(f"/{BASE_API_URL}/menu/cards")
    assert response.status_code == HTTPStatus.OK
    assert remove_Z_in_datetime_value(response.json()) == [remove_Z_in_datetime_value(serialize_object(card))]


@pytest.mark.django_db
def get_all_non_empty_cards_empty_test(anon_client):
    card = create_test_card()
    for dish in card.dishes.all():
        card.dishes.remove(dish)
    response: JsonResponse = anon_client.get(f"/{BASE_API_URL}/menu/cards")
    assert response.status_code == HTTPStatus.OK
    assert remove_Z_in_datetime_value(response.json()) == []


@pytest.mark.django_db
@pytest.mark.parametrize(
    "sort_by,sort_func,reverse",
    [
        ("name", lambda c: c["name"], False),
        ("-name", lambda c: c["name"], True),
        ("dishes_count", lambda c: len(c["dishes"]), False),
        ("-dishes_count", lambda c: len(c["dishes"]), True),
    ],
)
def get_all_non_empty_cards_sort_by_name_test(sort_by, sort_func, reverse, anon_client):
    cards = []
    for i in range(3, 0, -1):
        cards.append(create_test_card(number=i))

    response: JsonResponse = anon_client.get(f"/{BASE_API_URL}/menu/cards?sort_by={sort_by}")
    assert response.status_code == HTTPStatus.OK
    assert json.dumps(remove_Z_in_datetime_value(response.json()), sort_keys=True) == json.dumps(
        sorted([remove_Z_in_datetime_value(serialize_object(card)) for card in cards], key=sort_func, reverse=reverse),
        sort_keys=True,
    )


def card_passes_filter(card: Card, filter_dict: dict):
    for filter_name, filter_value in filter_dict.items():
        if "_contains" in filter_name and filter_value in getattr(card, filter_name.replace("_contains", "")):
            continue
        elif "datetime_from" in filter_name and filter_value <= getattr(
            card, filter_name.replace("datetime_from", "datetime")
        ):
            continue
        elif "datetime_to" in filter_name and filter_value >= getattr(
            card, filter_name.replace("datetime_to", "datetime")
        ):
            continue
        else:
            return False
    return True


cards_count = 30
possible_added_datetimes = [datetime.datetime(year=2021, month=9, day=number) for number in range(1, cards_count)]
possible_changed_datetimes = [datetime.datetime(year=2021, month=10, day=number) for number in range(1, cards_count)]
possible_names = [f"Card{number}" for number in range(1, cards_count)]

FILTERING_TEST_CARDS_SCHEMAS_LIST = [
    CardSchemaIn(name=possible_name, added_datetime=possible_added_datetime, changed_datetime=possible_changed_datetime)
    for possible_name, (possible_added_datetime, possible_changed_datetime) in zip(
        possible_names, zip(possible_added_datetimes, possible_changed_datetimes)
    )
    if possible_changed_datetime > possible_added_datetime
]

CARDS_FILTERING_FIELDS = [
    "name_contains",
    "added_datetime_from",
    "added_datetime_to",
    "changed_datetime_from",
    "changed_datetime_to",
]
CARDS_FILTERING_NAME_VALUES_MAP = {
    field_name: list(
        set(
            getattr(card_schema, field_name.replace("_from", "").replace("_to", "").replace("_contains", ""))
            if not isinstance(
                getattr(card_schema, field_name.replace("_from", "").replace("_to", "").replace("_contains", "")), str
            )
            else getattr(
                card_schema, field_name.replace("_from", "").replace("_to", "").replace("_contains", "")
            ).replace("Card", "")
            for card_schema in FILTERING_TEST_CARDS_SCHEMAS_LIST
        )
    )
    for field_name in list(set(CARDS_FILTERING_FIELDS))
}

CARDS_FILTERING_POSSIBLE_FIELDS_COMBOS = list(
    itertools.chain(
        *[
            list(itertools.combinations(CARDS_FILTERING_NAME_VALUES_MAP.keys(), fields_count_in_combo))
            for fields_count_in_combo in range(0, len(CARDS_FILTERING_NAME_VALUES_MAP.keys()) + 1)
        ]
    )
)
all_possible_combinations = list(
    itertools.chain(
        *[
            tuple(
                (tuple(fields_combo), tuple(values_combo))
                for fields_combo in CARDS_FILTERING_POSSIBLE_FIELDS_COMBOS
                for values_combo in list(
                    itertools.product(
                        *[sorted(CARDS_FILTERING_NAME_VALUES_MAP[field_name])[:1] for field_name in fields_combo]
                    )
                )
            )
        ]
    )
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "filters_names,filters_values",
    sorted(all_possible_combinations, key=lambda pc: str(pc[0])),
    ids=[f"{pc[0]} {pc[1]}" for pc in sorted(all_possible_combinations, key=lambda pc: str(pc[0]))],
)
def get_all_non_empty_cards_filtering_test(filters_names, filters_values, anon_client):
    with transaction.atomic():
        cards = [Card.objects.create(**card_schema.dict()) for card_schema in FILTERING_TEST_CARDS_SCHEMAS_LIST]
        counter = 0
        for card_number, card in enumerate(cards):
            dishes = [
                Dish.objects.create(
                    name=f"Dish{counter}",
                    price=round(counter * random.randint(0, 100) * 0.75, 2),
                    time_to_cook=datetime.timedelta(minutes=counter),
                )
                for _ in range(card_number * 3)
            ]
        Card.dishes.through.objects.bulk_create(
            [Card.dishes.through(card_id=card.id, dish_id=dish.id) for dish in dishes]
        )

    filter_dict = {}
    for filter_name, filter_value in zip(filters_names, filters_values):
        filter_dict[filter_name] = filter_value

    expected_result_cards = [card for card in cards if card_passes_filter(card, filter_dict) if card.dishes.count() > 0]
    query_string = "&".join([f"{filter_name}={filter_value}" for filter_name, filter_value in filter_dict.items()])
    response: JsonResponse = anon_client.get(f"/{BASE_API_URL}/menu/cards?{query_string}")
    assert response.status_code == HTTPStatus.OK
    assert json.dumps(remove_Z_in_datetime_value(response.json()), sort_keys=True) == json.dumps(
        [serialize_object(card) for card in expected_result_cards], sort_keys=True
    )


@pytest.mark.django_db
def get_pretty_card_by_id_test(anon_client):
    card = create_test_card()
    response: JsonResponse = anon_client.get(f"/{BASE_API_URL}/menu/cards/{card.id}")
    assert response.status_code == HTTPStatus.OK
    assert remove_Z_in_datetime_value(response.json()) == remove_Z_in_datetime_value(
        json.loads(json.dumps((CardPrettySchemaOut.from_orm(card).dict()), sort_keys=True, cls=NinjaJSONEncoder))
    )
