from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from book.models import Book
import tempfile
import shutil
from io import BytesIO
from PIL import Image


class BookTestCase(TestCase):
    def setUp(self):

        self.book_1 = Book.objects.create(
            title="The Pragmatic Programmer",
            author="Andrew Hunt and David Thomas",
            cover="hard",
            inventory=3,
            daily_fee=2.00,
        )

    def test_book_model(self):
        books = Book.objects.all()

        self.assertEqual(len(books), 1)

    def test_book_model_str(self):
        self.assertEqual(str(self.book_1), self.book_1.title)


MEDIA_ROOT_TEST = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT_TEST)
class BookImageTestCase(TestCase):

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT_TEST, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):

        image = Image.new("RGB", (100, 100), color=(255, 0, 0))
        image_io = BytesIO()
        image.save(image_io, format="JPEG")

        self.mock_image = SimpleUploadedFile(
            name="test_cover.jpg",
            content=image_io.getvalue(),
            content_type="image/jpeg",
        )

    def test_book_image_upload_and_custom_name(self):

        book = Book.objects.create(
            title="Test title",
            author="test_author",
            cover="soft",
            inventory=10,
            daily_fee=2.50,
            image=self.mock_image,
        )

        self.assertTrue(book.image)
        self.assertTrue(book.image.name.startswith("books/test-title-"))
        self.assertTrue(book.image.name.endswith(".jpg"))
        self.assertTrue(len(book.image.name) > 30)
