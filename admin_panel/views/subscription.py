from .base import AdminLoginView
from django.shortcuts import render
from api.models.subscription import SubscriptionPlan, UserSubscription
from django.http import JsonResponse



class SubscriptionView(AdminLoginView):
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        context = dict(
            plans = plans,
            is_subscription = True,
        )
        return render(request, "subscription/subscription.html", context)

class SubscriptionPlanDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Subscription Plan does not exist"}
            )
        return JsonResponse(
            {
                "status": True,
                "plan": plan_obj.to_json(),
            }
        )

from admin_panel.forms.subscription import SubscriptionPlanForm
import json
class SubscriptionEditView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Plan does not exist"}
            )
        context = dict(
            plan_obj = plan_obj,
            is_subscription = True,
        )
        return render(request, "subscription/edit_subscription.html", context)

    def post(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Plan does not exist"}
            )
        plan_form = SubscriptionPlanForm(request.POST, request.FILES, instance=plan_obj)
        if plan_form.is_valid():
            plan_obj = plan_form.save(commit=False)
            # plan_obj.updated_by = request.user
            plan_obj.save()
            return JsonResponse({"status": True, "message": "Plan updated successfully"})
        errors = plan_form.errors.as_json()
        parsed_data = json.loads(errors)
        first_key = next(iter(parsed_data))
        first_object = parsed_data[first_key][0]
        message = (
            f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
        )
        return JsonResponse({
            "status": False,
            "message": message,
        })


class SubscriptionAddView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_subscription = True,
        )
        return render(request, "subscription/add_subscription.html", context)
    
    def post(self, request):
        plan_form = SubscriptionPlanForm(request.POST)
        if plan_form.is_valid():
            plan_form.save()
            return JsonResponse({"status": True, "message": "Plan added successfully"})
        errors = plan_form.errors.as_json()
        parsed_data = json.loads(errors)
        first_key = next(iter(parsed_data))
        first_object = parsed_data[first_key][0]
        message = (
            f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
        )
        return JsonResponse({
            "status": False,
            "message": message,
        })

class SubscriptionDeleteView(AdminLoginView):
    def get(self, request, id):
        try:
            plan_obj = SubscriptionPlan.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Plan does not exist"}
            )
        plan_obj.delete()
        return JsonResponse({"status": True, "message": "Plan deleted successfully"})
class UserSubscriptionView(AdminLoginView):
    def get(self, request):
        user_plans = UserSubscription.objects.all()
        context = dict(
            user_plans = user_plans,
            is_user_subscription = True,
        )
        return render(request, "subscription/user_subscription.html", context)

from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from datetime import datetime
from django.http import HttpResponse
import csv
from utilities.utils import time_localize

class SubscriptionExportView(AdminLoginView):
    def get(self, request, file_type):
        print("file_type: ", file_type)
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def get_file_name(self):
        current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
        return f"subscription_plans-{current_timestamp}"

    def get_headers(self):
        return [
            "Name",
            "Description",
            "Price",
            "Plan Type",
            "Is Active",
            "Duration (days)",
        ]

    def get_queryset(self):
        return SubscriptionPlan.objects.all()

    def get_data_row(self, object):
        return [
            object.name,
            object.description,
            object.price,
            object.plan_type.title(),
            "Yes" if object.is_active else "No",
            object.duration,
        ]

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{self.get_file_name()}.csv"'
        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for user in self.get_queryset():
            row = self.get_data_row(user)
            writer.writerow(row)
        return response

    def excel_export(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(self.get_headers())
        for user in self.get_queryset():
            row = self.get_data_row(user)
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = f"attachment; filename={self.get_file_name()}.xlsx"
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response