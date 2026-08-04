from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from book.models import Book
from borrowings.models import Borrowing
from payment.models import Payment


class PaymentViewSetTestCase(TestCase):
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

        self.book = Book.objects.create(
            title="Refactoring",
            author="Martin Fowler",
            cover="soft",
            inventory=2,
            daily_fee=5.00,
        )

        self.borrowing_user = Borrowing.objects.create(
            user=self.regular_user,
            book=self.book,
            expected_return=timezone.now().date() + timedelta(days=2),
        )
        self.borrowing_admin = Borrowing.objects.create(
            user=self.admin_user,
            book=self.book,
            expected_return=timezone.now().date() + timedelta(days=2),
        )

        self.payment_user = Payment.objects.create(
            borrowing=self.borrowing_user,
            money_to_pay=10.00,
        )
        self.payment_admin = Payment.objects.create(
            borrowing=self.borrowing_admin,
            money_to_pay=15.00,
        )

        self.payments_list_url = reverse("payment:payment-list")
        self.success_url = reverse("payment:payment-success")
        self.cancel_url = reverse("payment:payment-cancel")

    def test_admin_can_see_all_payments(self):
        response = self.admin_client.get(self.payments_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_regular_user_can_see_only_own_payments(self):
        response = self.user_client.get(self.payments_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.payment_user.id)

    def test_success_payment_endpoint(self):
        response = self.user_client.get(
            f"{self.success_url}?session_id=test_session_123"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Payment successful!")
        self.assertEqual(response.data["session_id"], "test_session_123")

    def test_cancel_payment_endpoint(self):
        response = self.user_client.get(self.cancel_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("You can still pay in 24 hours", response.data["message"])
