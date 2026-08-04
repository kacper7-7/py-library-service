from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from notification.models import Notification


class NotificationViewSetTestCase(TestCase):
    def setUp(self):
        self.user_1 = get_user_model().objects.create_user(
            email="user1@example.com",
            password="password",
        )
        self.client_1 = APIClient()
        self.client_1.force_authenticate(user=self.user_1)

        self.user_2 = get_user_model().objects.create_user(
            email="user2@example.com",
            password="password",
        )
        self.client_2 = APIClient()
        self.client_2.force_authenticate(user=self.user_2)

        self.anon_client = APIClient()

        self.notification_1 = Notification.objects.create(
            user=self.user_1, message="Message for user 1"
        )
        self.notification_2 = Notification.objects.create(
            user=self.user_2, message="Message for user 2"
        )

        self.list_url = reverse("notification:notification-list")
        self.detail_url = reverse(
            "notification:notification-detail", kwargs={"pk": self.notification_1.pk}
        )

    def test_anonymous_user_cannot_access_notifications(self):
        response = self.anon_client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_list_only_own_notifications(self):
        response = self.client_1.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], self.notification_1.message)

    def test_user_cannot_retrieve_other_user_notification(self):
        other_detail_url = reverse(
            "notification:notification-detail", kwargs={"pk": self.notification_2.pk}
        )
        response = self.client_1.get(other_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_notification_is_not_allowed(self):
        payload = {"message": "Trying to create a notification"}
        response = self.client_1.post(self.list_url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_notification_is_not_allowed(self):
        response = self.client_1.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
