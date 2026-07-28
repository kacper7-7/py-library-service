import uuid
from pathlib import Path
from django.db import models


def upload_image_to(instance, file):
    suffix = Path(file).suffix
    file_name = instance.title
    random_signs = uuid.uuid4()

    return f"books/{file_name}-{random_signs}{suffix}"


class Book(models.Model):
    COVER_CHOICES = [("soft", "Soft"), ("hard", "Hard")]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=COVER_CHOICES)
    image = models.ImageField(blank=True, null=True, upload_to=upload_image_to)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.title
