from rest_framework import viewsets
from book.models import Book
from book.serializers import BookSerializer


class BookView(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.select_related("author")
