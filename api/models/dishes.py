from datetime import datetime

from django.db import models

from api.models.custom_fields import ISODurationString


class Dish(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    time_to_cook = ISODurationString()
    added_datetime = models.DateTimeField(default=datetime.utcnow)
    changed_datetime = models.DateTimeField(default=None, null=True, blank=True)
    is_vegan = models.BooleanField(default=False)
