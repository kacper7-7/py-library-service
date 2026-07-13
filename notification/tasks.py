from celery import shared_task
from .models import Notification


@shared_task
def send_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)

    return f"Celery sends {notification.message} to {notification.user.full_name}"
