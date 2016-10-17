from django.db import models

# Create your models here.
from django.db.models import FloatField, CharField
from django.utils import timezone


class TrafficModel(models.Model):
    avg_speed = FloatField()
    latitude = FloatField()
    longitude = FloatField()
    place_id = CharField(max_length=100)
    record_time = models.DateField(default=timezone.now)
