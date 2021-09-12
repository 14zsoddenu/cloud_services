# Register your models here.
from django.contrib import admin

from api.models.cards import Card
from api.models.dishes import Dish

classes_to_register = [Card, Dish]
for class_to_register in classes_to_register:
    admin.site.register(class_to_register)
