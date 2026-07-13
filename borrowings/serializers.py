from django.db import transaction
from rest_framework import serializers, generics, status
from book.serializers import BookSerializer
from borrowings.models import Borrowing
from notification.models import Notification
from notification.tasks import send_notification
from payment.models import Payment
from payment.utils import create_stripe_session


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
    payment_url = serializers.URLField(read_only=True)

    class Meta:
        model = Borrowing
        fields = ["borrow_date", "expected_return", "book", "payment_url"]

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

            request = self.context.get("request")

            try:
                payment_url = create_stripe_session(
                    borrowing=borrowing, request=request
                )
                borrowing.payment_url = payment_url

            except Exception as e:
                raise serializers.ValidationError({"stripe_error": str(e)})
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
