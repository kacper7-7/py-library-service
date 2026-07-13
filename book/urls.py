from django.urls import path, include
from rest_framework.routers import DefaultRouter

from book.views import BookView

router = DefaultRouter()
router.register("books", BookView, basename="book")

urlpatterns = [path("", include(router.urls))]


app_name = "book"
