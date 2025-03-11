from datetime import datetime, time, timezone
from collections import defaultdict
import pytz
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

logger = Logger("eye_fatigue.log")


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
        data = request.data.copy()
        response = take_user_selfie(request.headers.get("Customer-Access-Token"), data)
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


def convert_to_bool(value):
    return value.lower() == "yes"


class BlinkReportDetails(SecureHeadersMixin):
    def get(self, request):
        response = blinks_report_details(
            request.headers.get("Customer-Access-Token"), request.GET
        )
        try:
            try:
                processed_data = {
                    "user_id": request.user.id,
                    **response.json()["data"],
                }

                blink_status = processed_data.pop("blink_status", None)
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
        reports = EyeFatigueReport.objects.filter(user=request.user).order_by(
            "-created_on"
        )
        serializer = EyeFatigueReportSerializer(reports, many=True, fields=self.fields)
        return api_response(True, 200, data=serializer.data)


GRAPH_TIME_INTERVALS = [
    ((time(0, 0), time(6, 0)), time(3, 0)),
    ((time(6, 0), time(9, 0)), time(7, 30)),
    ((time(9, 0), time(12, 0)), time(10, 30)),
    ((time(12, 0), time(15, 0)), time(13, 30)),
    ((time(15, 0), time(18, 0)), time(16, 30)),
    ((time(18, 0), time(21, 0)), time(19, 30)),
    ((time(21, 0), time(23, 59)), time(22, 30)),
]


def get_average_values(reports, start_time, end_time, user_tz):
    avg_values = defaultdict(list)

    for report in reports:
        report_datetime = report.created_on.astimezone(user_tz)
        report_time = report_datetime.time()

        if start_time <= report_time < end_time:
            date_key = report_datetime.date()
            avg_values[date_key].append(report.get_percent())

    return {
        date: sum(values) / len(values) if values else 0
        for date, values in avg_values.items()
    }


def get_day_data(user, user_tz, day_date):
    day_data = {"date": day_date, "value": []}
    reports = EyeFatigueReport.objects.filter(user=user, created_on__date=day_date)
    values_list = list(reports.values_list("health_score", flat=True))
    logger.info(str(values_list))
    avg_value = 0.0
    try:
        avg_value = round(sum(values_list) / len(values_list), 2)
    except Exception as e:
        logger.error(str(e))
        # raise e
        avg_value = 0.0
    return avg_value

    for (start_time, end_time), point_time in GRAPH_TIME_INTERVALS:
        average_values = get_average_values(reports, start_time, end_time, user_tz)
        day_data["value"].append(average_values.get(day_date, 0))

    return day_data


def current_day_user_graph(user, user_timezone):
    user_tz = pytz.timezone(user_timezone)
    current_day_date = datetime.now(tz=user_tz).date()
    return get_day_data(user, user_tz, current_day_date)


def first_day_user_graph(user, user_timezone):
    user_tz = pytz.timezone(user_timezone)
    try:
        first_report = EyeFatigueReport.objects.filter(user=user).earliest("created_on")
        first_day_date = first_report.created_on.astimezone(user_tz).date()
        return get_day_data(user, user_tz, first_day_date)
    except EyeFatigueReport.DoesNotExist:
        return 0.0


def get_percentile_graph(user_timezone):
    values = [7.0, 6.0, 5.0, 4.0, 3.0, 4.0, 5.0]
    average = sum(values) / len(values)
    rounded_average = round(average, 2)
    return rounded_average


def get_ideal_graph(user_timezone):
    values = [10.0, 9.0, 8.0, 8.0, 7.0, 8.0, 8.0]
    average = sum(values) / len(values)
    rounded_average = round(average, 2)
    return rounded_average


def get_user_real_graph(user_timezone, user):
    user_tz = pytz.timezone(user_timezone)
    reports = EyeFatigueReport.objects.filter(user=user).order_by("created_on")

    # Group reports by date
    grouped_reports = defaultdict(list)
    for report in reports:
        report_date = report.created_on.astimezone(user_tz).date()
        grouped_reports[report_date].append(report)

    graph_data = []
    for day_date, day_reports in grouped_reports.items():
        day_data = {"date": day_date, "value": []}
        for (start_time, end_time), point_time in GRAPH_TIME_INTERVALS:
            average_values = get_average_values(
                day_reports, start_time, end_time, user_tz
            )
            day_data["value"].append(
                (point_time.strftime("%H:%M"), average_values.get(day_date, 0))
            )
        graph_data.append(day_data)

    return graph_data


class EyeFatigueGraph(UserMixin):
    def get(self, request):
        user_timezone = request.GET.get("user_timezone")

        if not user_timezone:
            return api_response(False, 400, message="user_timezone is required")

        try:
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
                no_of_eye_test=eye_test_count,
                name=request.user.get_full_name(),
                no_of_fatigue_test=eye_fatigue_count,
                eye_health_score=eye_health_score,
                first_day_data=first_day_user_graph(request.user, user_timezone),
                current_day_data=current_day_user_graph(request.user, user_timezone),
                get_percentile_graph=get_percentile_graph(user_timezone),
                get_ideal_graph=get_ideal_graph(user_timezone),
                # get_user_real_graph=get_user_real_graph(user_timezone, request.user),
            )
        except Exception as e:
            logger.error(str(e))
            return api_response(False, 500, message=str(e))


class DownloadReportView(UserMixin):
    def get(self, request):
        report_id = request.GET.get("report_id")
        if not report_id:
            return api_response(False, 400, message="Report ID is required")

        try:
            report = get_object_or_404(EyeFatigueReport, report_id=report_id)
            context = {
                "name": report.full_name,
                "age": report.age,
                "suggestions": str(report.get_suggestions()).split("\n"),
                "is_fatigue_right": report.is_fatigue_right,
                "is_fatigue_left": report.is_fatigue_left,
            }

            buffer = generate_pdf("reports/fatigue_test_report.html", context)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="fatigue_report_{report_id}.pdf"'
            )
            return response

        except EyeFatigueReport.DoesNotExist:
            return api_response(False, 404, message="Report not found")
