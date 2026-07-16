from rest_framework import viewsets
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingAdminSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action in ["create", "update"]:
            return BorrowingCreateSerializer
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
