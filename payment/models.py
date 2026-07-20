from django.db import models

from book.models import Book
from borrowings.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = [("pending", "PENDING"), ("paid", "PAID")]

    TYPE_CHOICES = [("payment", "PAYMENT"), ("fine", "FINE")]

    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default="pending")
    type = models.CharField(max_length=7, choices=TYPE_CHOICES, default="payment")
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=500, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    money_to_pay = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    def __str__(self):
        return f"Payment {self.id} for borrowing {self.borrowing.id} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.money_to_pay:
            book_fee = self.borrowing.book.daily_fee
            expected_borrow_days = (
                self.borrowing.expected_return - self.borrowing.borrow_date
            ).days

            if expected_borrow_days <= 0:
                expected_borrow_days = 1

            self.money_to_pay = book_fee * expected_borrow_days

            if (
                self.borrowing.actual_return_date
                and self.borrowing.actual_return_date > self.borrowing.expected_return
            ):
                overdue_days = (
                    self.borrowing.actual_return_date - self.borrowing.expected_return
                ).days
                FINE_MULTIPLIER = 2
                fine = overdue_days * book_fee * FINE_MULTIPLIER
                self.money_to_pay += fine

        super().save(*args, **kwargs)
