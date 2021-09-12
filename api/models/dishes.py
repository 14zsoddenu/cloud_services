from django.db import models

from api.models.abc import AbstractDatetimeTrackable
from api.models.custom_fields import ISODurationString, ImageStringField


class Dish(AbstractDatetimeTrackable):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    time_to_cook = ISODurationString()
    is_vegan = models.BooleanField(default=False)
    image = ImageStringField(null=True, blank=True)
