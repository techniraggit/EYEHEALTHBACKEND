import json
from django.http import HttpResponse
from django.conf import settings
import razorpay
from rest_framework.views import APIView
from core.logs import Logger
from api.models.subscription import UserModel, SubscriptionPlan, UserSubscription
from django.utils import timezone

logger = Logger("razor_pay.log")


class RazorPayWebHook(APIView):
    def post(self, request):
        try:
            body = request.body.decode("utf-8")
            data = json.loads(body)

            # Create Razorpay client
            client = razorpay.Client(
                auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET)
            )

            # Verify the webhook signature
            signature = request.headers.get("X-Razorpay-Signature")

            if not signature:
                logger.warning("No signature found in headers")
                return HttpResponse(status=400)
            logger.info(f"Signature: {signature}")

            verified = client.utility.verify_webhook_signature(
                body, signature, settings.RAZOR_PAY_WEBHOOK_SECRET
            )

            if verified:
                event = data.get("event")

                if event == "payment.authorized":
                    logger.info("Payment authorized")
                    logger.info(f"Data: {data}")

                    entity = data["payload"]["payment"]["entity"]
                    user_id = entity["notes"]["user_id"]
                    plan_id = entity["notes"]["plan_id"]
                    paid_amount = entity["amount"] / 100
                    payment_method = entity["method"]
                    payment_id = entity["id"]
                    payment_status = entity["payment_status"]

                    log_message = f"""
                    user_id = {user_id}
                    plan_id = {plan_id}
                    paid_amount = {paid_amount}
                    payment_method = {payment_method}
                    payment_id = {payment_id}
                    payment_status = {payment_status}
                    """

                    logger.info(log_message)

                    user_obj = UserModel.objects.get(id=user_id)
                    plan_obj = SubscriptionPlan.objects.get(id=plan_id)
                    end_date = timezone.now() + timezone.timedelta(days=plan_obj.duration)

                    UserSubscription.objects.create(
                        user=user_obj,
                        plan=plan_obj,
                        end_date=end_date,
                        is_active=True,
                        payment_method=payment_method,
                        paid_amount=paid_amount,
                        payment_id = payment_id,
                        payment_status=payment_status,
                    )
                return HttpResponse(status=200)

            else:
                logger.warning("Signature verification failed")
                return HttpResponse(status=400)

        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {str(e)}")
            return HttpResponse(status=400)

        except Exception as e:
            raise e
            logger.error(f"Exception: {str(e)}")
            return HttpResponse(status=400)
