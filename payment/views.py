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
        queryset = Payment.objects.select_related("borrowing").filter(
            borrowing__user__id=self.request.user.pk
        )

        return queryset

    # Otwieramy endpoint success dla przeglądarki bez tokena JWT:
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def success(self, request):
        session_id = request.query_params.get("session_id")
        return Response(
            {"message": "Płatność zakończona sukcesem!", "session_id": session_id}
        )

    # Otwieramy endpoint cancel:
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def cancel(self, request):
        return Response({"message": "Płatność została anulowana (zwrócono na stronę)."})


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
            payment.status = "PAID"
            payment.save()
            print(f"Zaktualizowano płatność {payment.id} na OPŁACONA!")
        except Payment.DoesNotExist:
            print(f"Błąd: Nie znaleziono płatności dla sesji {session_id}")
        except Payment.MultipleObjectsReturned:
            print(
                f"Błąd krytyczny: Znaleziono DUPLIKAT sesji w bazie! Usuń stare płatności."
            )
        except Exception as e:
            print(f"Inny błąd bazy danych w Pythona: {e}")

    return HttpResponse(status=200)
