from django.test import TestCase

from book.models import Book
from book.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def setUp(self):
        self.book_attributes = {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "cover": "hard",
            "inventory": 5,
            "daily_fee": 3.50,
        }

        self.book = Book.objects.create(**self.book_attributes)
        self.serializer = BookSerializer(instance=self.book)

    def test_contains_expected_fields(self):
        expected_fields = {
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
            "image",
        }

        data = self.serializer.data

        self.assertEqual(set(data.keys()), expected_fields)

    def test_field_content(self):
        data = self.serializer.data

        self.assertEqual(data["title"], self.book_attributes["title"])
        self.assertEqual(data["author"], self.book_attributes["author"])
        self.assertEqual(float(data["daily_fee"]), self.book_attributes["daily_fee"])

    def test_serializer_with_valid_data(self):
        serializer = BookSerializer(data=self.book_attributes)
        self.assertTrue(serializer.is_valid())

    def test_serializer_with_invalid_data(self):

        invalid_data = self.book_attributes.copy()
        invalid_data["title"] = ""

        serializer = BookSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        print(serializer.errors)
        self.assertIn("title", serializer.errors)
