from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
import csv
from django.utils import timezone
from utilities.utils import time_localize
from .base import AdminLoginView
from django.shortcuts import render
from api.models.eye_health import EyeTestReport, EyeFatigueReport
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from utilities.utils import generate_pdf
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime


class EyeTestView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search")
        start_date_str = request.GET.get("start_date_filter")
        end_date_str = request.GET.get("end_date_filter")
        health_score_str = request.GET.get("health_score_filter")

        # Filter base query
        eye_test_reports = EyeTestReport.objects.all().select_related(
            "user_profile", "user_profile__user"
        )

        # Apply search filter
        if search:
            search_filter = (
                Q(report_id=search)
                | Q(user_profile__full_name__icontains=search)
                | Q(user_profile__user__email__icontains=search)
                | Q(user_profile__user__phone_number__icontains=search)
            )
            eye_test_reports = eye_test_reports.filter(search_filter)

        # Convert date filters
        start_date_filter = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if start_date_str
            else None
        )
        end_date_filter = (
            datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
        )

        # Apply date filters
        if start_date_filter and end_date_filter:
            eye_test_reports = eye_test_reports.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )
        elif start_date_filter:
            eye_test_reports = eye_test_reports.filter(
                created_on__date__gte=start_date_filter
            )
        elif end_date_filter:
            eye_test_reports = eye_test_reports.filter(
                created_on__date__lte=end_date_filter
            )

        # Apply health score filter
        try:
            health_score_filter = float(health_score_str)
            eye_test_reports = eye_test_reports.filter(health_score=health_score_filter)
        except (ValueError, TypeError):
            health_score_filter = 0.0

        # Order and paginate the results
        eye_test_reports = eye_test_reports.order_by("-created_on").distinct()
        paginator = Paginator(eye_test_reports, 10)
        page_number = request.GET.get("page")
        paginated_eye_test_reports = paginator.get_page(page_number)

        context = {
            "eye_test_reports": paginated_eye_test_reports,
            "is_eye_exam": True,
            "search": search,
            "start_date_filter": start_date_str,
            "end_date_filter": end_date_str,
            "health_score_filter": health_score_filter,
        }
        return render(request, "eye_exam/eye_test.html", context)


class EyeTestDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            eye_test_report_obj = EyeTestReport.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Eye test report does not exist"}
            )

        return JsonResponse(
            {
                "status": True,
                "eye_test_report": eye_test_report_obj.report(),
            }
        )


class EyeTestExportView(AdminLoginView):
    current_timestamp = time_localize(timezone.datetime.now()).strftime("%Y%m%d%H%M%S")
    file_name = f"eye-test-reports-{current_timestamp}"

    def get_queryset(self):
        return EyeTestReport.objects.all()

    def get(self, request, file_type):
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.file_name}.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Report ID",
                "User",
                "Right SPH",
                "Right CYL",
                "Right AXIS",
                "Right ADD",
                "Left SPH",
                "Left CYL",
                "Left AXIS",
                "Left ADD",
                "Health Score",
            ]
        )
        for report in self.get_queryset():
            left_eye = report.left_eye_obj()
            right_eye = report.right_eye_obj()
            writer.writerow(
                [
                    str(report.report_id),
                    report.user_profile.user.get_full_name(),
                    right_eye.get("sph"),
                    right_eye.get("cyl"),
                    right_eye.get("axis"),
                    right_eye.get("add"),
                    left_eye.get("sph"),
                    left_eye.get("cyl"),
                    left_eye.get("axis"),
                    left_eye.get("add"),
                    report.health_score,
                ]
            )
        return response

    def excel_export(self, request):
        headers = [
            "Report ID",
            "User",
            "Right SPH",
            "Right CYL",
            "Right AXIS",
            "Right ADD",
            "Left SPH",
            "Left CYL",
            "Left AXIS",
            "Left ADD",
            "Health Score",
        ]
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(headers)
        for report in self.get_queryset():
            left_eye = report.left_eye_obj()
            right_eye = report.right_eye_obj()
            row = [
                str(report.report_id),
                report.user_profile.user.get_full_name(),
                right_eye.get("sph"),
                right_eye.get("cyl"),
                right_eye.get("axis"),
                right_eye.get("add"),
                left_eye.get("sph"),
                left_eye.get("cyl"),
                left_eye.get("axis"),
                left_eye.get("add"),
                report.health_score,
            ]
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = f"attachment; filename={self.file_name}.xlsx"
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response


class DownloadEyeTestReportView(AdminLoginView):
    def get(self, request, report_id):
        try:
            report = get_object_or_404(EyeTestReport, report_id=report_id)

            buffer = generate_pdf("reports/eye_test_report.html", report.report())
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="prescription_{report_id}.pdf"'
            )
            return response

        except EyeTestReport.DoesNotExist:
            return JsonResponse({"status": False, "message": "Report not found"})


class EyeFatigueView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search")
        start_date_str = request.GET.get("start_date_filter")
        end_date_str = request.GET.get("end_date_filter")
        health_score_str = request.GET.get("health_score_filter", 0)
        is_fatigue_left_str = request.GET.get("is_fatigue_left_filter")
        is_fatigue_right_str = request.GET.get("is_fatigue_right_filter")

        # Convert boolean filters
        is_fatigue_left = (
            is_fatigue_left_str.lower() == "yes" if is_fatigue_left_str else None
        )
        is_fatigue_right = (
            is_fatigue_right_str.lower() == "yes" if is_fatigue_right_str else None
        )

        # Convert health score filter
        try:
            health_score_filter = int(health_score_str)
        except ValueError:
            health_score_filter = 0

        # Filter base query
        eye_fatigue_reports = EyeFatigueReport.objects.all().select_related("user")

        # Apply search filter
        if search:
            search_filter = (
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(user__phone_number__icontains=search)
                | Q(report_id__icontains=search)
            )
            eye_fatigue_reports = eye_fatigue_reports.filter(search_filter)

        # Apply date filters
        if start_date_str:
            start_date_filter = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            eye_fatigue_reports = eye_fatigue_reports.filter(
                created_on__date__gte=start_date_filter
            )
        if end_date_str:
            end_date_filter = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            eye_fatigue_reports = eye_fatigue_reports.filter(
                created_on__date__lte=end_date_filter
            )
        if start_date_str and end_date_str:
            eye_fatigue_reports = eye_fatigue_reports.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )

        # Apply health score filter
        if health_score_filter:
            eye_fatigue_reports = eye_fatigue_reports.filter(
                health_score=health_score_filter
            )

        # Apply fatigue filters
        if is_fatigue_left is not None:
            eye_fatigue_reports = eye_fatigue_reports.filter(
                is_fatigue_left=is_fatigue_left
            )
        if is_fatigue_right is not None:
            eye_fatigue_reports = eye_fatigue_reports.filter(
                is_fatigue_right=is_fatigue_right
            )

        # Order and paginate the results
        eye_fatigue_reports = eye_fatigue_reports.order_by("-created_on").distinct()
        paginator = Paginator(eye_fatigue_reports, 10)
        page_number = request.GET.get("page")
        paginated_eye_fatigue_reports = paginator.get_page(page_number)

        context = {
            "eye_fatigue_reports": paginated_eye_fatigue_reports,
            "is_eye_fatigue": True,
            "search": search,
            "start_date_filter": start_date_str,
            "end_date_filter": end_date_str,
            "health_score_filter": health_score_filter,
            "is_fatigue_left_filter": is_fatigue_left_str,
            "is_fatigue_right_filter": is_fatigue_right_str,
        }
        return render(request, "eye_exam/eye_fatigue.html", context)


class EyeFatigueDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            eye_fatigue_report_obj = EyeFatigueReport.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Eye fatigue report does not exist"}
            )

        return JsonResponse(
            {
                "status": True,
                "eye_fatigue_report": eye_fatigue_report_obj.to_json(),
            }
        )


class EyeFatigueExportView(AdminLoginView):
    current_timestamp = time_localize(timezone.datetime.now()).strftime("%Y%m%d%H%M%S")
    file_name = f"eye-fatigue-reports-{current_timestamp}"

    def get_queryset(self):
        return EyeFatigueReport.objects.all()

    def get(self, request, file_type):
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.file_name}.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Report ID",
                "User",
                "Fatigue Right",
                "Mild Tiredness Right",
                "Fatigue_Left",
                "Mild Tiredness Left",
            ]
        )
        for report in self.get_queryset():
            writer.writerow(
                [
                    str(report.report_id),
                    report.user.get_full_name(),
                    "Yes" if report.is_fatigue_right else "No",
                    "Yes" if report.is_mild_tiredness_right else "No",
                    "Yes" if report.is_fatigue_left else "No",
                    "Yes" if report.is_mild_tiredness_left else "No",
                ]
            )
        return response

    def excel_export(self, request):
        headers = [
            "Report ID",
            "User",
            "Fatigue Right",
            "Mild Tiredness Right",
            "Fatigue_Left",
            "Mild Tiredness Left",
        ]
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(headers)
        for report in self.get_queryset():
            row = [
                str(report.report_id),
                report.user.get_full_name(),
                "Yes" if report.is_fatigue_right else "No",
                "Yes" if report.is_mild_tiredness_right else "No",
                "Yes" if report.is_fatigue_left else "No",
                "Yes" if report.is_mild_tiredness_left else "No",
            ]
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = f"attachment; filename={self.file_name}.xlsx"
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response
