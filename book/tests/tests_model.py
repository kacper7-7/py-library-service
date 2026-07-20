from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from book.models import Book


class BookTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )

        self.client.force_authenticate(user=user)

        self.book_1 = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andrew Hunt and David Thomas",
            cover="hard",
            inventory=3,
            daily_fee=2.00,
        )

    def test_book_model(self):
        books = Book.objects.all()

        self.assertEqual(len(books), 1)

    def test_book_model_str(self):
        self.assertEqual(str(self.book_1), self.book_1.title)
