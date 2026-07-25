from django.contrib.auth import get_user_model
from django.test import TestCase
from notification.models import Notification
from notification.serializers import NotificationSerializer


class NotificationSerializerTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="password123",
        )
        self.notification = Notification.objects.create(
            user=self.user,
            message="Test serialization message",
            is_read=True,
        )
        self.serializer = NotificationSerializer(instance=self.notification)

    def test_contains_expected_fields(self):
        expected_fields = {"id", "message", "is_read", "created_at"}
        data = self.serializer.data
        self.assertEqual(set(data.keys()), expected_fields)

    def test_field_content(self):
        data = self.serializer.data
        self.assertEqual(data["message"], self.notification.message)
        self.assertTrue(data["is_read"])
