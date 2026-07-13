import stripe
from rest_framework import viewsets, status
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


class PaymentViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = Payment.objects.select_related("borrowing").filter(
            borrowing__user__id=self.request.user.pk
        )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        amount_in_cents = int(payment.money_to_pay * 100)

        success_url = request.build_absolute_uri("/api/payments/success/")
        cancel_url = request.build_absolute_uri("/api/payments/cancel/")

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": amount_in_cents,
                            "product_data": {
                                "name": f"Payment for borrowing {payment.borrowing_id}",
                            },
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=cancel_url,
            )

            payment.session_url = checkout_session.url
            payment.session_id = checkout_session.id
            payment.save()

            return Response(
                {"message": "Payment initiated.", "payment_url": checkout_session.url},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            payment.delete()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
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

        session_id = session.get("id")

        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = "PAID"
            payment.save()
            print(f"Zaktualizowano płatność {payment.id} na OPŁACONA!")
        except Payment.DoesNotExist:
            print(f"Błąd: Nie znaleziono płatności dla sesji {session_id}")

    return HttpResponse(status=200)
