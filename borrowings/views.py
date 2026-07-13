from rest_framework import viewsets
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create" or self.action == "update":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        return Borrowing.objects.select_related("book", "user").filter(
            user__id=self.request.user.pk
        )
