from django.db import models
from django.conf import settings

class Book(models.Model):
    COVER_CHOICES = [
        ("soft", "Soft"),
        ("hard", "Hard")
    ]


    title = models.CharField(max_length=255)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)