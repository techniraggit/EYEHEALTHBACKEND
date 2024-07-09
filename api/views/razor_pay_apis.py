import json
from django.http import HttpResponse
from django.conf import settings
import razorpay
from rest_framework.views import APIView
from core.logs import Logger

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
                # Process the webhook payload
                event = data.get("event")
                logger.info(f"Event: {event}")

                if event == "payment.captured":
                    # Handle the payment captured event
                    print("Payment Captured")
                    logger.info("Payment Captured")
                    # Add your logic here

                # Handle other events if necessary
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
