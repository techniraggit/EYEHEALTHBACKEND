from django.utils import timezone
from api.models.subscription import SubscriptionPlan, UserSubscription, UserModel
from rest_framework.views import APIView
import stripe
from django.conf import settings
from rest_framework import serializers
from core.utils import api_response
from .base import UserMixin
from django.http import HttpResponse
from core.logs import Logger

logger = Logger("stripe.logs")


class CheckoutSessionSerializer(serializers.Serializer):
    price = serializers.IntegerField(required=True)
    product_name = serializers.CharField(required=True, max_length=50)
    customer_id = serializers.CharField(required=True, max_length=250)
    product_id = serializers.UUIDField(required=True)


class CreateCheckoutSession(UserMixin):
    def post(self, request):
        serialized_data = CheckoutSessionSerializer(data=request.data)
        if serialized_data.is_valid():
            price = serialized_data.data.get("price")
            product_name = serialized_data.data.get("product_name")
            customer_id = serialized_data.data.get("customer_id")
            product_id = serialized_data.data.get("product_id")
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
                    customer=customer_id,
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
            except Exception:
                return Exception
        return api_response(False, 400, serialized_data.errors)

STRIPE_WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
class WebHook(APIView):
    def post(self, request):
        event = None
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        logger.info("STRIPE_WEBHOOK_SECRET == ", STRIPE_WEBHOOK_SECRET)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(str(e))
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(str(e))
            return HttpResponse(status=400)

        logger.info(event.get("type"))

        payment_status_map = dict(
            requires_payment_method="pending", succeeded="success"
        )

        if event["type"] == "payment_intent.succeeded":
            session = event["data"]["object"]
            user = UserModel.objects.get(id=session["metadata"]["user_id"])
            plan = SubscriptionPlan.objects.get(id=session["metadata"]["plan_id"])
            end_date = timezone.now() + timezone.timedelta(days=plan.duration)
            payment_method = session["payment_method_types"][0]
            paid_amount = session["amount"] / 100
            UserSubscription.objects.create(
                user=user,
                plan=plan,
                end_date=end_date,
                is_active=True,
                payment_method=payment_method,
                paid_amount=paid_amount,
                payment_status=payment_status_map.get(session["status"], "failed"),
            )
        elif event["type"] == "payment_intent.created":
            pass

        return HttpResponse(status=200)


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
        id = CreateCustomer(**request.data)
        return api_response(True, 201, "Customer created", customer_id=id)
