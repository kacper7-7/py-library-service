from django.urls import path, include

from book.views import BookView

app_name = "book"


urlpatterns = [
    path("", BookView.as_view(), name="book-list")
]
