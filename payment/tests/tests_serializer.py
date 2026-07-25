from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from book.models import Book
from borrowings.models import Borrowing
from payment.serializers import Payment, PaymentSerializer


class PaymentSerializerTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password123",
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

        self.payment = Payment.objects.create(borrowing=self.borrowing)

        self.serializer = PaymentSerializer(instance=self.payment)

    def test_contains_expected_fields(self):
        expected_fields = {"id", "status", "type", "borrowing"}
        data = self.serializer.data
        self.assertEqual(set(data.keys()), expected_fields)

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["type"], "payment")
