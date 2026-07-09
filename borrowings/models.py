from datetime import date

from django.db import models
from book.models import Book
from django.conf import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.full_name} borrowed {self.book.title}."

    @property
    def money_to_pay(self):

        if self.actual_return_date:
            fine_payment = self.payments.filter(type="fine").first()
            if fine_payment:
                return fine_payment.money_to_pay

        end_date = self.actual_return_date or date.today()

        if end_date > self.expected_return:
            overdue_days = (end_date - self.expected_return).days
            FINE_MULTIPLIER = 3.00
            return FINE_MULTIPLIER * overdue_days * self.book.daily_fee

        return 0.00
