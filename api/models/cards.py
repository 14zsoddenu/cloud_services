from datetime import datetime

from django.db import models

from api.models.dishes import Dish


class Card(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    added_datetime = models.DateTimeField(default=datetime.utcnow)
    changed_datetime = models.DateTimeField(null=True, blank=True)
    dishes = models.ManyToManyField(Dish, default=list)
