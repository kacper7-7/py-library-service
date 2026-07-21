from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from book.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from borrowings.serializers import BorrowingCreateSerializer


class BorrowingSerializerTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andrew Hunt and David Thomas",
            cover="hard",
            inventory=3,
            daily_fee=2.00,
        )

        user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password",
            first_name="FirstName",
            last_name="LastName",
        )

        self.borrowing_attributes = {
            "expected_return": timezone.now().date() + timedelta(days=2),
            "book": self.book,
            "user": user,
        }

        self.borrowing = Borrowing.objects.create(**self.borrowing_attributes)
        self.serializer = BorrowingSerializer(instance=self.borrowing)

    def test_contains_expected_fields(self):
        expected_fields = {
            "id",
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
            "payments",
            "is_active",
        }

        data = self.serializer.data

        self.assertEqual(set(data.keys()), expected_fields)

    def test_field_content(self):
        data = self.serializer.data

        date_borrowing_attribute = self.borrowing_attributes[
            "expected_return"
        ].strftime("%Y-%m-%d")

        self.assertEqual(data["expected_return"], date_borrowing_attribute)
        self.assertEqual(data["book"], self.book.pk)

    def test_serializer_with_valid_data(self):
        valid_data = {
            "expected_return": (timezone.now().date() + timedelta(days=2)).isoformat(),
            "book": self.book.id,
        }

        serializer = BorrowingSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_invalid_data(self):

        invalid_data = {"expected_return": "", "book": self.book.id}

        serializer = BorrowingSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("expected_return", serializer.errors)

    def test_borrowing_create_serializer_return_before_borrow_invalid(self):

        today = timezone.now().date()
        invalid_data = {
            "borrow_date": today.isoformat(),
            "expected_return": (today - timedelta(days=2)).isoformat(),
            "book": self.book.id,
        }

        serializer = BorrowingCreateSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("expected_return", serializer.errors)
        self.assertEqual(
            str(serializer.errors["expected_return"][0]),
            "Expected return data must be later than borrow date!",
        )
