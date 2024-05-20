from rest_framework.views import APIView
import stripe
from django.conf import settings
from rest_framework import serializers
from core.utils import api_response
from .base import UserMixin


class CheckoutSessionSerializer(serializers.Serializer):
    price = serializers.IntegerField(required=True)
    product_name = serializers.CharField(required=True, max_length=50)
    product_id = serializers.UUIDField(required=True)


class CreateCheckoutSession(UserMixin):
    def post(self, request):
        print("request.user.customer_id == ", request.user.customer_id)
        serialized_data = CheckoutSessionSerializer(data=request.data)
        if serialized_data.is_valid():
            price = serialized_data.data.get("price")
            product_name = serialized_data.data.get("product_name")
            product_id = serialized_data.data.get("product_id")
            email = request.user.email
            user_id = request.user.id

            try:
                stripe.api_key = settings.STRIP_SECRETS_KEY
                checkout_session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            "price_data": {
                                "currency": "inr",
                                "product_data": {
                                    "name": product_name,
                                },
                                "unit_amount": price * 100,
                            },
                            "quantity": 1,
                        }
                    ],
                    customer=request.user.customer_id,
                    mode="payment",
                    metadata={
                        "product_id": product_id,
                        "user_id": user_id,
                    },
                    success_url=settings.STRIP_PAYMENT_SUCCESS_URL,
                    cancel_url=settings.STRIP_PAYMENT_CANCEL_URL,
                )
                return api_response(
                    True, 303, checkout_session_url=checkout_session.url
                )
            except Exception as e:
                print(e)
                return e
        return api_response(False, 400, serialized_data.errors)


from rest_framework.response import Response


class WebHook(APIView):
    def post(self, request):
        event = None
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as err:
            raise err
        except stripe.error.SignatureVerificationError as err:
            raise err

        if event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            print("succeeded ============= \n\n", payment_intent)
        elif event.type == "payment_method.attached":
            payment_method = event.data.object
            print("attached ============= \n\n", payment_method)

        else:
            print("Unhandled event type ============= \n\n{}".format(event.type))

        return Response({"success": True})


def CreateCustomer(name, email, address, postal_code, city, state, country="India"):
    stripe.api_key = settings.STRIP_SECRETS_KEY

    customer = stripe.Customer.create(
        email=email,
        name=name,
        description="",
        address={
            "line1": address,
            "city": city,
            "state": state,
            "country": "US",
            "postal_code": postal_code,
        },
        shipping={
            "name": name,
            "address": {
                "line1": address,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code,
            },
        },
    )
    return customer.id


class CreateCustomerView(APIView):
    def post(self, request):
        id = CreateCustomer(
            name="Jenny Rosen",
            email="test@gmail.com",
            line1="510 Twonder St",
            postal_code="247342",
            city="San Francisco",
            state="CA",
            country="india",
        )
        return api_response(True, 201, "Customer created", customer_id=id)
