from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from book.models import Book
from borrowings.models import Borrowing


class BorrowingTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password",
            first_name="FirstName",
            last_name="LastName",
        )

        self.client.force_authenticate(user=user)

        self.book = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andrew Hunt and David Thomas",
            cover="hard",
            inventory=3,
            daily_fee=2.00,
        )

        self.borrowing_1 = Borrowing.objects.create(
            expected_return=timezone.now().date() + timedelta(days=2),
            book=self.book,
            user=user,
        )

    def test_borrowing_model(self):
        borrowings = Borrowing.objects.all()

        self.assertEqual(len(borrowings), 1)

    def test_borrowing_model_str(self):
        self.assertEqual(
            str(self.borrowing_1),
            f"{self.borrowing_1.user.full_name} borrowed {self.borrowing_1.book.title}.",
        )

    def test_money_to_pay_is_zero_when_returned_on_time(self):

        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.borrowing_1.user,
            expected_return=timezone.now().date() + timedelta(days=5),
            actual_return_date=timezone.now().date() + timedelta(days=3),
        )

        self.assertEqual(borrowing.money_to_pay, 0.00)

    def test_money_to_pay_calculates_correct_fine_when_overdue(self):
        self.book.daily_fee = 2.00
        self.book.save()

        today = timezone.now().date()
        expected_date = today - timedelta(days=5)

        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.borrowing_1.user,
            expected_return=expected_date,
            actual_return_date=today,
        )

        self.assertEqual(borrowing.money_to_pay, 30.00)
