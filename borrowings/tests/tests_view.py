from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from book.models import Book
from borrowings.models import Borrowing


class BorrowingsTestCase(TestCase):
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

        self.borrowing_1 = Borrowing.objects.create(
            book=self.book_1,
            expected_return=timezone.now().date() + timedelta(days=2),
            user=self.regular_user,
        )
        self.book_1.inventory -= 1

        self.borrowing_2 = Borrowing.objects.create(
            book=self.book_2,
            expected_return=timezone.now().date() + timedelta(days=1),
            user=self.admin_user,
        )

        self.borrowings_list_url = reverse("borrowing:borrowing-list")
        self.borrowing_detail_url = reverse(
            "borrowing:borrowing-detail", kwargs={"pk": self.borrowing_1.pk}
        )

    def test_admin_user_borrowings_list(self):
        response = self.admin_client.get(self.borrowings_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_regular_user_borrowings_list(self):
        response = self.user_client.get(self.borrowings_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_borrowings_detail(self):

        response = self.admin_client.get(self.borrowing_detail_url)

        expected_return_date = self.borrowing_1.expected_return.strftime("%Y-%m-%d")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["expected_return"], expected_return_date)

    def test_create_borrowings(self):
        payload = {
            "expected_return": (timezone.now().date() + timedelta(days=4)).isoformat(),
            "book": self.book_2.pk,
        }

        response = self.admin_client.post(self.borrowings_list_url, data=payload)
        borrowings = Borrowing.objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(borrowings), 3)

    def test_delete_borrowings(self):
        response = self.user_client.get(self.borrowings_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_delete = self.user_client.delete(self.borrowing_detail_url)

        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)

        response = self.user_client.get(self.borrowings_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_cannot_delete_other_user_borrowing(self):
        response = self.admin_client.get(self.borrowings_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        borrowing_detail_url = reverse(
            "borrowing:borrowing-detail", kwargs={"pk": self.borrowing_2.pk}
        )

        response_delete = self.user_client.delete(borrowing_detail_url)

        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response_delete.data)

        response = self.admin_client.get(self.borrowings_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_borrow_when_book_inventory_is_zero(self):
        book = Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            cover="soft",
            inventory=1,
            daily_fee=1.00,
        )

        borrowing_payload = {
            "expected_return": (timezone.now().date() + timedelta(days=3)).isoformat(),
            "book": book.pk,
        }

        response_post = self.admin_client.post(
            self.borrowings_list_url, data=borrowing_payload
        )
        book.refresh_from_db()
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment_url", response_post.data)

        response_post = self.user_client.post(
            self.borrowings_list_url, data=borrowing_payload
        )
        book.refresh_from_db()
        self.assertEqual(response_post.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(book.inventory, 0)
        error_messages = str(response_post.data)
        self.assertIn("This book is not available in inventory.", error_messages)

        response_get = self.admin_client.get(self.borrowings_list_url)

        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_get.data), 3)

    def test_return_book(self):
        book = Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            cover="soft",
            inventory=1,
            daily_fee=1.00,
        )

        borrowing_payload = {
            "expected_return": (timezone.now().date() + timedelta(days=3)).isoformat(),
            "book": book.pk,
        }

        response_post = self.admin_client.post(
            self.borrowings_list_url, data=borrowing_payload
        )
        self.book_1.refresh_from_db()
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment_url", response_post.data)

        self.assertEqual(book.inventory, 1)

        borrowing = Borrowing.objects.get(book=book.pk)
        return_book_url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": borrowing.pk}
        )
        response = self.admin_client.post(return_book_url)
        book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, 1)

    def test_filter_borrowings_by_user_id(self):
        response = self.admin_client.get(
            f"{self.borrowings_list_url}?user_id={self.regular_user.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["user_id"], self.regular_user.id)
        self.assertEqual(len(response.data), 1)

    def test_return_book_twice(self):

        borrowing_payload = {
            "expected_return": (timezone.now().date() + timedelta(days=3)).isoformat(),
            "book": self.book_2.pk,
        }
        self.user_client.post(self.borrowings_list_url, data=borrowing_payload)

        #
        borrowing = Borrowing.objects.get(
            book=self.book_2.pk,
            actual_return_date__isnull=True,
            expected_return=borrowing_payload["expected_return"],
        )
        return_book_url = reverse(
            "borrowing:borrowing-return-book", kwargs={"pk": borrowing.pk}
        )

        self.book_2.refresh_from_db()
        initial_inventory = self.book_2.inventory

        response_first = self.user_client.post(return_book_url)
        self.book_2.refresh_from_db()

        self.assertEqual(response_first.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book_2.inventory, initial_inventory + 1)

        response_second = self.user_client.post(return_book_url)
        self.book_2.refresh_from_db()

        self.assertEqual(response_second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response_second.data["message"], "You have already returned this book!"
        )
        self.assertEqual(self.book_2.inventory, initial_inventory + 1)

    def test_anonymous_user_cannot_access_borrowings(self):

        response = self.anon_client.get(self.borrowings_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
