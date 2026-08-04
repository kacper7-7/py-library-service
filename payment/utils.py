import stripe
from .models import Payment


def create_stripe_session(borrowing, request, payment_type="payment"):

    payment = Payment.objects.create(
        borrowing=borrowing, status="pending", type=payment_type
    )

    amount_in_cents = int(payment.money_to_pay * 100)

    success_url = request.build_absolute_uri("/api/payments/success/")
    cancel_url = request.build_absolute_uri("/api/payments/cancel/")

    if payment_type == "fine":
        product_name = f"Fine for overdue borrowing of '{borrowing.book.title}'"
    else:
        product_name = f"Payment for borrowing '{borrowing.book.title}'"

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": amount_in_cents,
                        "product_data": {
                            "name": product_name,
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

        return checkout_session.url

    except Exception as e:
        payment.delete()
        raise Exception(f"Stripe error: {str(e)}")
