from celery import shared_task
from django.db import close_old_connections
from django.utils import timezone
from borrowings.models import Borrowing
from .models import Notification
from .utils import send_telegram_message


@shared_task
def send_notification(notification_id):
    notification = Notification.objects.get(id=notification_id)

    return f"Celery sends {notification.message} to {notification.user.full_name}"


@shared_task
def send_telegram_task(message: str):
    return send_telegram_message(message)


@shared_task
def every_day_notification():
    close_old_connections()

    today = timezone.now().date()

    all_borrowings = Borrowing.objects.select_related("book", "user").filter(
        expected_return__lt=today, actual_return_date__isnull=True
    )

    if not all_borrowings.exists():
        send_telegram_message("No borrowings overdue today!")
        return "No borrowings overdue today!"

    count = 0

    for borrowing in all_borrowings:
        book = borrowing.book
        overdue_days = (today - borrowing.expected_return).days
        message = (
            f"<b>Overdue Book Alert!</b>\n\n"
            f"<b>User:</b> {borrowing.user.email}\n"
            f"<b>Book:</b> {book.title}\n"
            f"<b>Days Overdue:</b> {overdue_days} { 'day' if overdue_days == 1 else 'days' }\n"
            f"<b>Expected Return:</b> {borrowing.expected_return}\n\n"
            f"Please return this book to the library as soon as possible."
        )
        send_telegram_task.delay(message)
        count += 1

    return f"Sent {count} overdue notifications."
