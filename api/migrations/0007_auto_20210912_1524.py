# Generated by Django 3.2.7 on 2021-09-12 13:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_dish_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='added_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='dish',
            name='added_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]