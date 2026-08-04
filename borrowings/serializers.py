from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from book.models import Book
from book.serializers import BookSerializer
from borrowings.models import Borrowing
from notification.tasks import send_telegram_task
from payment.serializers import PaymentSerializer
from payment.utils import create_stripe_session


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
            "payments",
            "is_active",
        ]

    def get_is_active(self, obj):
        if not obj.actual_return_date:
            return True
        return False


class BorrowingAdminSerializer(BorrowingSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta(BorrowingSerializer.Meta):
        fields = BorrowingSerializer.Meta.fields + ["user_id"]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
            "money_to_pay",
            "payments",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    payment_url = serializers.URLField(read_only=True)

    class Meta:
        model = Borrowing
        fields = ["borrow_date", "expected_return", "book", "payment_url"]

    def create(self, validated_data):
        book = validated_data["book"]

        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=book.pk)
            if book.inventory <= 0:
                raise serializers.ValidationError(
                    "This book is not available in inventory."
                )
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

            user = borrowing.user
            message = (
                f"<b>New borrowing!</b>\n\n"
                f"<b>User:</b> {user.email}\n"
                f"<b>Book:</b> {book.title}\n"
                f"<b>Date of borrow:</b> {borrowing.borrow_date}\n"
                f"<b>Estimated return:</b> {borrowing.expected_return}\n"
            )

            transaction.on_commit(lambda: send_telegram_task.delay(message))

        return borrowing

    def validate(self, attrs):
        today = timezone.now().date()
        borrow_date = attrs.get("borrow_date", today)
        expected_return = attrs.get("expected_return")

        if expected_return and borrow_date and expected_return < borrow_date:
            raise serializers.ValidationError(
                {
                    "expected_return": "Expected return data must be later than borrow date!"
                }
            )

        return attrs


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["actual_return_date"]
        read_only_fields = ["actual_return_date"]
