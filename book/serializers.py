from rest_framework import serializers
from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    length_category = serializers.CharField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "image",
            "length_category",
        ]
