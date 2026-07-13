from django.core.mail import message
from django.db import transaction
from django.db.models import Model
from rest_framework import serializers, generics

from book.models import Book
from book.serializers import BookSerializer
from borrowings.models import Borrowing
from notification.models import Notification
from notification.tasks import send_notification
from payment.models import Payment
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
        ]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
            "money_to_pay",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return",
            "book",
        ]

    def create(self, validated_data):
        book = validated_data["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError(
                "This book is not available in inventory."
            )

        with transaction.atomic():
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(**validated_data)

            payment = Payment.objects.create(type="payment", borrowing=borrowing)

            notification = Notification.objects.create(
                user=borrowing.user,
                message=f"You have borrowed {borrowing.book.title}. Cost {payment.money_to_pay}$.",
            )
            send_notification.delay(notification.pk)

            return borrowing

    def update(self, instance, validated_data):
        if (
            "actual_return_date" in validated_data
            and instance.actual_return_date is None
        ):
            book = instance.book
            book.inventory += 1
            book.save()
        return super().update(instance, validated_data)
