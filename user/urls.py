from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user.views import UserViewSet, UserCreateView

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    path("", include(router.urls)),
]


app_name = "user"
