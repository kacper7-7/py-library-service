from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny

from user.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
