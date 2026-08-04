from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
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

from payment.utils import create_stripe_session


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
                return queryset.filter(user__id__in=user_id)
            return queryset

        else:
            return queryset.filter(user__id=self.request.user.pk)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.STR,
                description="Search borrowings by user id",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True)
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"message": "You have already returned this book!"},
                status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            payment_url = None

            if borrowing.money_to_pay > 0:
                try:
                    payment_url = create_stripe_session(
                        borrowing=borrowing, request=request, payment_type="fine"
                    )
                except Exception as e:
                    return Response(
                        {"stripe_error": str(e)}, status=status.HTTP_400_BAD_REQUEST
                    )

        serializer = self.get_serializer(borrowing)
        response_data = dict(serializer.data)

        if payment_url:
            response_data["message"] = (
                "Book returned, but you have an overdue fine to pay!"
            )
            response_data["payment_url"] = payment_url
        else:
            response_data["message"] = "Book returned successfully on time!"

        return Response(response_data, status=status.HTTP_200_OK)
