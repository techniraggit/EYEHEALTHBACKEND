from core.constants import ERROR_500_MSG
import os
from django.shortcuts import get_object_or_404
from utilities.utils import generate_pdf
from django.utils import timezone
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
                processed_data["user_id"] = request.user.id
                processed_data["report_id"] = json_data.get("report_id")

                if EyeFatigueReport.objects.filter(
                    report_id=processed_data["report_id"]
                ).exists():
                    return api_response(
                        False, 400, "Report already exists with this report id"
                    )
                try:
                    data = EyeFatigueReport.objects.create(**processed_data)
                    return api_response(
                        True,
                        200,
                        data=data.to_json(),
                        message="Report generated successfully.",
                    )
                except Exception as e:
                    return api_response(False, 400, message=str(e))
            except Exception as e:
                return api_response(False, 500, message=ERROR_500_MSG, error=str(e))
        except:
            return HttpResponse(response)


class EyeFatigueReportsView(UserMixin):
    fields = [
        "report_id",
        "user",
        "is_fatigue_right",
        "is_mild_tiredness_right",
        "is_fatigue_left",
        "is_mild_tiredness_left",
        "created_on",
        "suggestion",
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


class EyeFatigueGraph(UserMixin):
    def get(self, request):
        query_set = EyeFatigueReport.objects.filter(user=request.user)

        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        try:
            if from_date and not to_date:
                query_set = query_set.filter(created_on__date__gte=from_date)
            elif to_date and not from_date:
                query_set = query_set.filter(created_on__date__lte=to_date)
            elif from_date and to_date:
                query_set = query_set.filter(
                    created_on__date__range=[from_date, to_date]
                )
            else:
                query_set = query_set.filter(
                    created_on__date__gte=(timezone.now() - timezone.timedelta(days=7))
                )

            data = [
                {
                    "date": report.created_on,
                    "value": report.get_percent(),
                    "is_fatigue_right": report.is_fatigue_right,
                    "is_mild_tiredness_right": report.is_mild_tiredness_right,
                    "is_fatigue_left": report.is_fatigue_left,
                    "is_mild_tiredness_left": report.is_mild_tiredness_left,
                }
                for report in query_set
            ]
            return api_response(True, 200, data=data)
        except Exception as e:
            return api_response(False, 500, message=str(e))


class DownloadReportView(UserMixin):
    def get(self, request):
        report_id = request.GET.get("report_id")
        if not report_id:
            return api_response(False, 400, message="Report ID is required")

        try:
            report = get_object_or_404(EyeFatigueReport, report_id=report_id)
            context_data = EyeFatigueReportSerializer(report).data
            context = {
                "full_name": f"{context_data.get('user', {}).get('first_name', '')} {context_data.get('user', {}).get('last_name', '')}",
                "age": context_data.get("user", {}).get("age", ""),
                "suggestion": context_data.get("suggestion", ""),
                "is_fatigue_right": context_data.get("is_fatigue_right", False),
                "is_fatigue_left": context_data.get("is_fatigue_left", False),
                "logo_url": os.getenv("ZUKTI_LOGO"),
            }

            buffer = generate_pdf("reports/fatigue.html", context)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="fatigue_report_{report_id}.pdf"'
            )
            return response

        except EyeFatigueReport.DoesNotExist:
            return api_response(False, 404, message="Report not found")
