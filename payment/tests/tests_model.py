from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from book.models import Book
from borrowings.models import Borrowing
from payment.models import Payment


class PaymentModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password",
        )
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert C. Martin",
            cover="hard",
            inventory=5,
            daily_fee=10.00,
        )

        today = timezone.now().date()
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=today,
            expected_return=today + timedelta(days=3),
        )

    def test_payment_automatic_money_calculation(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            type="payment",
        )

        self.assertEqual(payment.money_to_pay, 30.00)

    def test_payment_str(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="pending",
        )
        expected_str = (
            f"Payment {payment.id} for borrowing {self.borrowing.id} - pending"
        )
        self.assertEqual(str(payment), expected_str)
