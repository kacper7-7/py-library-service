from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from book.models import Book

BOOK_LIST_URL = reverse("book:book-list")


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

        self.book_2 = Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            cover="soft",
            inventory=10,
            daily_fee=1.00,
        )

    def test_book_list(self):
        response = self.client.get(BOOK_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_book_detail(self):
        book_detail_url = reverse("book:book-detail", kwargs={"pk": self.book_1.pk})

        response = self.client.get(book_detail_url, kwargs={"pk": self.book_1.pk})
        print(response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book_1.title)
        self.assertEqual(response.data["author"], self.book_1.author)
