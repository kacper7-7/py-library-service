from rest_framework import serializers, generics

from book.serializers import BookSerializer
from borrowings.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
            "user",
        ]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    user = UserSerializer()

    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return",
            "actual_return_date",
            "book",
            "user",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "borrow_date",
            "expected_return",
            "book",
            "user",
        ]
