import stripe
from rest_framework import viewsets

import payment
from .models import Payment
from .serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentSerializer,
)
from rest_framework.response import Response
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
    action,
)
from rest_framework.permissions import AllowAny

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing")

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(borrowing__user=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def success(self, request):
        session_id = request.query_params.get("session_id")
        return Response({"message": "Payment successful!", "session_id": session_id})

    # Otwieramy endpoint cancel:
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def cancel(self, request):

        return Response({"message": f"You can still pay in 24 hours."})


@csrf_exempt
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        session_id = session.id

        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = "paid"
            payment.save()
            print(f"Updated payment {payment.id} status to PAID!")
        except Payment.DoesNotExist:
            print(f"Error: Payment not found for session {session_id}")
        except Payment.MultipleObjectsReturned:
            print(
                f"Critical Error: Duplicate session found in database! Remove old payments."
            )
        except Exception as e:
            print(f"Database error in Python: {e}")

    return HttpResponse(status=200)
