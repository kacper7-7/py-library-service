from rest_framework import viewsets

from notification.models import Notification
from notification.serializers import NotificationSerializer


class NotificationView(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user__id=self.request.user.pk)
