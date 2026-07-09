from rest_framework import viewsets
from .models import Payment
from .serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        return Payment.objects.select_related("borrowing").filter(
            borrowing__user__id=self.request.user.pk
        )
