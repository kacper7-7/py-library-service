from django.contrib.auth import get_user_model
from rest_framework import viewsets
from user.permissions import CreateUserOrAdminOnly
from user.serializers import UserSerializer, UserCreateSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [CreateUserOrAdminOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer
