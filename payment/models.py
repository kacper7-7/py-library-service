from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = [("pending", "PENDING"), ("paid", "PAID")]

    TYPE_CHOICES = [("payment", "PAYMENT"), ("fine", "FINE")]

    status = models.CharField(max_length=7, choices=STATUS_CHOICES)
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=500, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    money_to_pay = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"Payment {self.id} for borrowing {self.borrowing.id} - {self.status}"
