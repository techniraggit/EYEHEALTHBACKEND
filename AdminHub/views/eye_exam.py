
from .base import AdminLoginView
from django.shortcuts import render
from api.models.eye_health import EyeTestReport, EyeFatigueReport
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from utilities.utils import generate_pdf
from django.shortcuts import get_object_or_404


class EyeTestView(AdminLoginView):
    def get(self, request):
        eye_test_reports = EyeTestReport.objects.all().order_by("-created_on")
        context = dict(
            eye_test_reports=eye_test_reports,
            is_eye_exam=True,
        )
        return render(request, "eye_exam/eye_test.html", context)

class EyeTestDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            eye_test_report_obj = EyeTestReport.objects.get(pk=id)
        except:
            return JsonResponse({
                "status": False,
                "message": "Eye test report does not exist"
            })
        
        return JsonResponse({
            "status": True,
            "eye_test_report": eye_test_report_obj.report(),
        })

from utilities.utils import time_localize
from django.utils import timezone
import csv
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook

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
            "Health Score"
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
            "Health Score"
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

            buffer = generate_pdf("reports/prescription.html", report.report())
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="prescription_{report_id}.pdf"'
            )
            return response

        except EyeTestReport.DoesNotExist:
            return JsonResponse({
                "status": False,
                "message": "Report not found"
            })


class EyeFatigueView(AdminLoginView):
    def get(self, request):
        eye_fatigue_reports = EyeFatigueReport.objects.all().order_by("-created_on")
        context = dict(
            eye_fatigue_reports=eye_fatigue_reports,
            is_eye_fatigue=True,
        )
        return render(request, "eye_exam/eye_fatigue.html", context)