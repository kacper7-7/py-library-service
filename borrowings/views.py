from django.db import transaction
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingAdminSerializer,
    BorrowingReturnSerializer,
)
from django.utils import timezone


class BorrowingViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action in ["create", "update"]:
            return BorrowingCreateSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        if self.request.user.is_staff:
            return BorrowingAdminSerializer
        return BorrowingSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.select_related("book").prefetch_related("payments")
        if self.request.user.is_staff:
            queryset = queryset.select_related("user")

            user_id = self.request.query_params.get("user_id")

            if user_id:
                user_id = user_id.split(",")
                return queryset.filter(user__id_in=user_id)
            return queryset

        else:
            return queryset.filter(user__id=self.request.user.pk)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True)
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        with transaction.atomic():
            if borrowing.actual_return_date is None:
                borrowing.book.inventory += 1
                borrowing.book.save()
                borrowing.actual_return_date = timezone.now().date()
                borrowing.save()

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)
