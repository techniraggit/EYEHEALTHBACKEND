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
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q

User = get_user_model()


class UserView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        if search:
            users = User.objects.exclude(id=request.user.id).filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone_number__icontains=search)
                | Q(referral_code__icontains=search)
                | Q(points__icontains=search)
            )
        else:
            users = User.objects.exclude(id=request.user.id)
        context = dict(
            users=users,
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
        serialized_data = UserSerializer(data=request.POST, instance=user_obj)
        if serialized_data.is_valid():
            serialized_data.save()
            messages.success(request, "User updated successfully")
            return redirect(reverse("user_edit_view", kwargs={"id": user_obj.id}))
        messages.error(request, serialized_data.errors)
        return redirect(reverse("user_edit_view", kwargs={"id": user_obj.id}))


class UserDeleteView(AdminLoginView):
    def get(self, request, id):
        try:
            user_obj = User.objects.get(id=id)
        except:
            messages.error(request, "User does not exist")
            return redirect("users_view")
        # user_obj.delete()
        messages.success(request, "User deleted successfully")
        return redirect("users_view")


class UserExportView(AdminLoginView):
    current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
    file_name = f"users-{current_timestamp}"

    def get_queryset(self):
        return User.objects.exclude(is_superuser=True)

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
                "id",
                "first_name",
                "last_name",
                "email",
                "phone_number",
                "referral_code",
                "points",
            ]
        )
        for user in self.get_queryset():
            writer.writerow(
                [
                    (user.id),
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.phone_number,
                    user.referral_code,
                    user.points,
                ]
            )
        return response

    def excel_export(self, request):
        headers = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "referral_code",
            "points",
        ]
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(headers)
        for user in self.get_queryset():
            row = [
                str(user.id),
                user.first_name,
                user.last_name,
                user.email,
                user.phone_number,
                user.referral_code,
                user.points,
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
