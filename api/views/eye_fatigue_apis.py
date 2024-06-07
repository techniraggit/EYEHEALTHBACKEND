from django.db.models import Avg
from datetime import datetime, time, timedelta
from api.models.rewards import GlobalPointsModel
from api.models.eye_health import EyeTestReport
from core.logs import Logger
from api.models.accounts import UserPoints
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
from core.logs import Logger

logger = Logger("eye_fatigue.logs")

logger = Logger("fatigue.logs")


END_POINTS = {
    "add_customer": f"{settings.FATIGUE_BASE_URL}/add-customer/",
    "calculate_blink_rate": f"{settings.FATIGUE_BASE_URL}/calculate-blink-rate/",
    "blinks_report_details": f"{settings.FATIGUE_BASE_URL}/blinks-report-details/",
    "take_user_selfie": f"{settings.FATIGUE_BASE_URL}/take-user-selfie/",
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


def take_user_selfie(token, data):
    headers = dict(Authorization=f"Bearer {token}")
    data["source_type"] = "app"
    response = requests.post(
        END_POINTS.get("take_user_selfie"), json=data, headers=headers
    )
    return response


class TakeUserSelfie(UserMixin):
    def post(self, request):
        response = take_user_selfie(
            request.headers.get("Customer-Access-Token"), request.data
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


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
                    points = GlobalPointsModel.objects.get(
                        event_type="fatigue_test"
                    ).value
                    usr_pnt = UserPoints.objects.create(
                        user=request.user,
                        event_type="fatigue_test",
                    )
                    usr_pnt.increase_points(points)
                    usr_pnt.save()
                except Exception as e:
                    logger.error(str(e))

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
        "percentage",
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


def get_user_fatigue_data(user):
    today = timezone.now().date()
    first_report_date = (
        EyeFatigueReport.objects.filter(user=user)
        .earliest("created_on")
        .created_on.date()
    )

    def get_average_values(start_time, end_time):
        start_datetime = datetime.combine(today, start_time)
        end_datetime = datetime.combine(today, end_time)
        reports = EyeFatigueReport.objects.filter(
            user=user, created_on__gte=start_datetime, created_on__lt=end_datetime
        )
        if not reports.exists():
            return 0
        total_score = sum(report.get_percent() for report in reports)
        return total_score / reports.count()

    time_intervals = [
        (time(6, 0), time(9, 0)),
        (time(9, 0), time(12, 0)),
        (time(12, 0), time(15, 0)),
        (time(15, 0), time(18, 0)),
    ]

    first_day_data = {"date": first_report_date, "value": []}
    current_day_data = {"date": today, "value": []}

    for start_time, end_time in time_intervals:
        first_day_avg_value = get_average_values(start_time, end_time)
        current_day_avg_value = get_average_values(start_time, end_time)
        first_day_data["value"].append(first_day_avg_value)
        current_day_data["value"].append(current_day_avg_value)

    return first_day_data, current_day_data


class EyeFatigueGraph(UserMixin):
    def get(self, request):
        try:
            user = request.user
            first_day_data, current_day_data = get_user_fatigue_data(user)

            eye_fatigue_count = EyeFatigueReport.objects.filter(
                user=request.user
            ).count()

            eye_test_count = EyeTestReport.objects.filter(
                user_profile__user=request.user
            ).count()

            eye_health_score = EyeTestReport.objects.filter(
                user_profile__user=request.user,
                user_profile__full_name=request.user.get_full_name(),
                user_profile__age=request.user.age(),
            )

            eye_health_score = (
                eye_health_score.first().health_score if eye_health_score.first() else 0
            )

            return api_response(
                True,
                200,
                first_day_data=first_day_data,
                current_day_data=current_day_data,
                no_of_eye_test=eye_test_count,
                name=request.user.get_full_name(),
                no_of_fatigue_test=eye_fatigue_count,
                eye_health_score=eye_health_score,
            )
        except Exception as e:
            return api_response(False, 500, message=str(e))


class DownloadReportView(UserMixin):
    def get(self, request):
        report_id = request.GET.get("report_id")
        if not report_id:
            return api_response(False, 400, message="Report ID is required")

        try:
            report = get_object_or_404(EyeFatigueReport, report_id=report_id)
            context = {
                "name": report.user.get_full_name(),
                "age": report.user.age(),
                "suggestions": str(report.get_suggestions()).split("\n"),
                "is_fatigue_right": report.is_fatigue_right,
                "is_fatigue_left": report.is_fatigue_left,
            }

            buffer = generate_pdf("reports/fatigue.html", context)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="fatigue_report_{report_id}.pdf"'
            )
            return response

        except EyeFatigueReport.DoesNotExist:
            return api_response(False, 404, message="Report not found")
