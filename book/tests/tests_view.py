from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from book.models import Book


class BookTestCase(TestCase):
    def setUp(self):

        self.admin_user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="password",
            is_staff=True,
        )
        self.admin_client = APIClient()
        self.admin_client.force_authenticate(user=self.admin_user)

        self.regular_user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password",
            is_staff=False,
        )
        self.user_client = APIClient()
        self.user_client.force_authenticate(user=self.regular_user)

        self.anon_client = APIClient()

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

        self.book_list_url = reverse("book:book-list")
        self.book_detail_url = reverse(
            "book:book-detail", kwargs={"pk": self.book_1.pk}
        )

    def test_book_list(self):
        response = self.admin_client.get(self.book_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_book_detail(self):

        response = self.admin_client.get(self.book_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.book_1.title)
        self.assertEqual(response.data["author"], self.book_1.author)

    def test_create_book_as_admin_allowed(self):
        payload = {
            "title": "Clean Code",
            "author": "Author",
            "cover": "soft",
            "inventory": 4,
            "daily_fee": 4.00,
        }

        response = self.admin_client.post(self.book_list_url, data=payload)
        books = Book.objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(books), 3)
        self.assertEqual(response.data["title"], "Clean Code")

    def test_create_book_as_regular_user_forbidden(self):
        payload = {
            "title": "New Book",
            "author": "Author",
            "cover": "hard",
            "inventory": 1,
            "daily_fee": 1.0,
        }
        response = self.user_client.post(self.book_list_url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book(self):
        response = self.admin_client.get(self.book_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response_delete = self.admin_client.delete(self.book_detail_url)

        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

        response = self.admin_client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_partially_update_book(self):
        payload = {"title": "Updated Title Only"}

        response = self.admin_client.patch(self.book_detail_url, data=payload)
        self.book_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book_1.title, "Updated Title Only")

        self.assertEqual(self.book_1.inventory, 3)

    def test_update_book(self):
        payload = {
            "title": "Completely New Title",
            "author": "New Author",
            "cover": "soft",
            "inventory": 20,
            "daily_fee": 5.00,
        }

        response = self.admin_client.put(self.book_detail_url, data=payload)
        self.book_1.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book_1.title, "Completely New Title")
        self.assertEqual(self.book_1.inventory, 20)
