from core.constants import ERROR_500_MSG
from utilities.utils import get_form_error_msg
from utilities.utils import dlt_value
from admin_panel.forms.accounts import UserCreationForm, AdminCreationForm
import json
from django.http import JsonResponse
from utilities.utils import time_localize
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from datetime import datetime
from django.http import HttpResponse
import csv
from api.serializers.accounts import UserSerializer
from django.urls import reverse
from .base import AdminLoginView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from api.models.accounts import UserModel, OTPLog
from django.core.paginator import Paginator

User = UserModel


class UserView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        if search:
            users = (
                User.objects.exclude(id=request.user.id)
                .filter(
                    Q(email__icontains=search)
                    | Q(first_name__icontains=search)
                    | Q(last_name__icontains=search)
                    | Q(phone_number__icontains=search)
                    | Q(referral_code__icontains=search)
                    | Q(points__icontains=search)
                )
                .order_by("-created_on")
            )
        else:
            users = User.objects.exclude(id=request.user.id).order_by("-created_on")
        paginator = Paginator(users, 10)
        page_number = request.GET.get("page")
        paginated_users = paginator.get_page(page_number)
        context = dict(
            users=paginated_users,
            is_user=True,
            search=search,
        )
        return render(request, "users/users.html", context)


class UserDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            user_obj = User.objects.get(id=id)
        except:
            messages.error(request, "User does not exist")
            return redirect("users_view")
        context = dict(
            user_obj=user_obj,
            is_user=True,
        )
        return render(request, "users/user_view.html", context)


class UserBulkDeleteView(AdminLoginView):
    def post(self, request):
        try:
            selected_ids = request.POST.getlist("selected_ids[]")
            users = User.objects.filter(id__in=selected_ids)
            count = users.count()
            if count < 1:
                return JsonResponse(
                    {"status": False, "message": "No selected users found"}
                )
            for user in users:
                user.delete()
            return JsonResponse(
                {"status": True, "message": f"Selected users deleted successfully"}
            )
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)})


class UserEditView(AdminLoginView):
    def get(self, request, id):
        try:
            user_obj = User.objects.get(id=id)
        except:
            messages.error(request, "User does not exist")
            return redirect(f"user_edit_view/{user_obj.id}")
        context = dict(
            user_obj=user_obj,
            is_user=True,
        )
        return render(request, "users/edit_user.html", context)

    def post(self, request, id):
        try:
            user_obj = User.objects.get(id=id)
        except:
            messages.error(request, "User does not exist")
            return redirect(f"user_edit_view/{user_obj.id}")

        user_form = UserCreationForm(data=request.POST, instance=user_obj)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, "User updated successfully")
            return redirect("users_view")

        messages.error(request, get_form_error_msg(user_form.errors.as_json()))
        return redirect(reverse("user_edit_view", kwargs={"id": user_obj.id}))


class AddUserView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_user=True,
        )
        return render(request, "users/add_user.html", context)

    def post(self, request):
        user_creation_form = UserCreationForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            return JsonResponse({"status": True, "message": "User added successfully"})
        errors = user_creation_form.errors.as_json()
        parsed_data = json.loads(errors)
        first_key = next(iter(parsed_data))
        first_object = parsed_data[first_key][0]
        message = f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
        return JsonResponse(
            {
                "status": False,
                "message": message,
            }
        )


class AddAdminView(AdminLoginView):
    def post(self, request):
        admin_creation_form = AdminCreationForm(data=request.POST)
        if admin_creation_form.is_valid():
            admin_creation_form.save()
            return JsonResponse({"status": True, "message": "Admin added successfully"})
        message = get_form_error_msg(admin_creation_form.errors.as_json())
        return JsonResponse(
            {
                "status": False,
                "message": message,
            }
        )


class UserDeleteView(AdminLoginView):
    def get(self, request, id):
        try:
            user_obj = User.objects.get(id=id)
        except:
            messages.error(request, "User does not exist")
            return redirect("users_view")
        usr_phone = user_obj.phone_number
        usr_email = user_obj.email
        user_obj.phone_number = usr_phone + dlt_value()
        user_obj.email = usr_email + dlt_value()
        user_obj.save()
        user_obj.delete()
        OTPLog.objects.filter(Q(username=usr_phone) | Q(username=usr_email)).delete()
        messages.success(request, "User deleted successfully")
        return redirect("users_view")


class ChangeUserStatusView(AdminLoginView):
    def get(self, request, id):
        try:
            user_obj = User.objects.get(id=id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "User does not exist",
                }
            )

        try:
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            message = "Activated" if user_obj.is_active else "Suspended"
            return JsonResponse(
                {
                    "status": True,
                    "user_current_status": user_obj.is_active,
                    "message": f"User {message} successfully",
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": False,
                    "message": ERROR_500_MSG,
                    "error": str(e),
                }
            )


class UserExportView(AdminLoginView):
    def get_queryset(self, request):
        selected_ids = request.POST.getlist("selected_ids[]")
        if selected_ids:
            users = User.objects.filter(id__in=selected_ids)
        else:
            users = User.objects.exclude(is_superuser=True)
        return users

    def post(self, request, file_type):
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def get_file_name(self):
        current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
        file_name = f"users-{current_timestamp}"
        return file_name

    def get_headers(self):
        return [
            "ID",
            "First Name",
            "Last Name",
            "Email",
            "Phone Number",
            "Referral Code",
            "Points",
        ]

    def get_row_data(self, object):
        return [
            str(object.id),
            object.first_name,
            object.last_name,
            object.email,
            object.phone_number,
            object.referral_code,
            object.points,
        ]

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_file_name()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for user in self.get_queryset(request):
            writer.writerow(self.get_row_data(user))
        return response

    def excel_export(self, request):
        workbook = Workbook()
        worksheet = workbook.active

        worksheet.append(self.get_headers())
        for user in self.get_queryset(request):
            worksheet.append(self.get_row_data(user))

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response = HttpResponse(content_type="application/octet-stream")
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_file_name()}.xlsx"
        )
        response.write(virtual_excel_file)
        return response
