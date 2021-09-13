from datetime import datetime

from django.db import models

from api.models.abc import AbstractDatetimeTrackable
from api.models.dishes import Dish


class Card(AbstractDatetimeTrackable):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    dishes = models.ManyToManyField(Dish, default=list)
