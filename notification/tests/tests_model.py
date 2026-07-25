from django.contrib.auth import get_user_model
from django.test import TestCase
from notification.models import Notification


class NotificationModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com",
            password="password",
            first_name="John",
            last_name="Doe",
        )
        self.notification = Notification.objects.create(
            user=self.user, message="This is a test notification."
        )

    def test_notification_str(self):
        expected_str = (
            f"Notification for {self.user.email}: {self.notification.message}"
        )
        self.assertEqual(str(self.notification), expected_str)

    def test_notification_default_is_read_value(self):
        self.assertFalse(self.notification.is_read)
