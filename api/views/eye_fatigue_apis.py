from api.models.eye_health import EyeFatigueReport
from core.utils import api_response, custom_404
from api.serializers.eye_health import EyeFatigueReportSerializer
from .base import UserMixin, SecureHeadersMixin
import requests
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings


END_POINTS = {
    "add_customer": f"{settings.FATIGUE_BASE_URL}/add-customer/",
    "calculate_blink_rate": f"{settings.FATIGUE_BASE_URL}/calculate-blink-rate/",
    "blinks_report_details": f"{settings.FATIGUE_BASE_URL}/blinks-report-details/",
}


def add_customer(data):
    response = requests.post(END_POINTS.get("add_customer"), json=data)
    return response


def calculate_blink_rate(token, video):
    headers = dict(Authorization=f"Bearer {token}")

    response = requests.post(
        END_POINTS.get("calculate_blink_rate"), files=video, headers=headers
    )
    return response


def blinks_report_details(token, data):
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.get(
        END_POINTS.get("blinks_report_details"), params=data, headers=headers
    )
    return response


class AddCustomer(UserMixin):
    def post(self, request):
        request_user = request.user
        data = dict(
            email=request_user.email,
            name=request_user.get_full_name(),
            domain_url=settings.FATIGUE_DOMAIN_URL,
            age=request_user.age(),
            mobile_no=request_user.phone_number,
        )
        response = add_customer(data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class CalculateBlinkRate(SecureHeadersMixin):
    def post(self, request):
        response = calculate_blink_rate(
            request.headers.get("Customer-Access-Token"), request.FILES
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


def convert_fatigue_data(data) -> dict:
    data.pop("blink_status", None)
    data.pop("full_name", None)
    data.pop("age", None)

    converted_bool_data = {
        key: (str(value).lower == "yes") for key, value in data.items()
    }
    return converted_bool_data


class BlinkReportDetails(SecureHeadersMixin):
    def get(self, request):
        response = blinks_report_details(
            request.headers.get("Customer-Access-Token"), request.GET
        )
        try:
            try:
                json_data = response.json()["data"]
                processed_data = convert_fatigue_data(json_data)
                processed_data["user"] = request.user.id
                processed_data["report_id"] = json_data.get("report_id")
                serializer = EyeFatigueReportSerializer(data=processed_data)
                if serializer.is_valid():
                    serializer.save()
                    return api_response(
                        True,
                        200,
                        data=serializer.data,
                        message="Report generated successfully.",
                    )
                return api_response(False, 400, message=serializer.errors)
            except:
                return Response(response.json(), response.status_code)
        except Exception as e:
            print(e)
            return HttpResponse(response)


class EyeFatigueReportsView(UserMixin):
    fields = [
        "report_id",
        "is_fatigue_right",
        "is_mild_tiredness_right",
        "is_fatigue_left",
        "is_mild_tiredness_left",
    ]

    def get_object(self, pk):
        try:
            return EyeFatigueReport.objects.get(report_id=pk)
        except EyeFatigueReport.DoesNotExist:
            raise custom_404("The fatigue report does not exist.")

    def get(self, request):
        report_id = request.GET.get("report_id")
        if report_id:
            data = self.get_object(report_id)
            serializer = EyeFatigueReportSerializer(data, fields=self.fields)
            return api_response(True, 200, data=serializer.data)
        reports = EyeFatigueReport.objects.filter(user=request.user)
        serializer = EyeFatigueReportSerializer(reports, many=True, fields=self.fields)
        return api_response(True, 200, data=serializer.data)