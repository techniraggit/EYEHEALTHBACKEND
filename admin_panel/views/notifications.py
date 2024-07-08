from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import Workbook
import csv
from utilities.utils import time_localize
from django.http import HttpResponse
from django.db.models import Q
from .base import AdminLoginView
from django.shortcuts import render
from api.models.notifications import PushNotification, UserModel, UserPushNotification
from django.core.paginator import Paginator
from utilities.services.notification import create_notification
from django.http import JsonResponse
from datetime import datetime


from django.utils.timesince import timesince
from django.utils import timezone

class MyNotificationView(AdminLoginView):
    def get(self, request):
        try:
            notifications = UserPushNotification.objects.filter(user=request.user).order_by("-created_on")
            is_read_available = notifications.filter(is_read=False).exists()
            data = []
            for notification in notifications:
                data.append({
                    'id': str(notification.id),
                    'title': notification.notification.title,
                    'message': notification.notification.message,
                    'time_since_creation': timesince(notification.created_on, timezone.now()),
                    'created_on': time_localize(notification.created_on).strftime('%d %b, %I:%M %p'),
                    'is_read': notification.is_read,
                })
            return JsonResponse({
                "status": True,
                "data": data,
                "is_read_available": is_read_available,
            })
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e),
            })

class MarkThisRead(AdminLoginView):
    def post(self, request):
        id = request.POST.get("id")
        if not id:
            return JsonResponse({
                "status": False,
                "message": "Invalid notification id",
            })
        try:
            notification_obj = UserPushNotification.objects.get(id=id)
        except:
            return JsonResponse({
                "status": False,
                "message": "Notification does not exist",
            })
        notification_obj.is_read = True
        notification_obj.save()
        is_read_available = UserPushNotification.objects.filter(user=request.user, is_read=False).exists()
        return JsonResponse({
            "status": True,
            "is_read_available": is_read_available
        })

class NotificationView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        notification_qs = PushNotification.objects.all().order_by("-created_on")

        if search:
            notification_qs = notification_qs.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            notification_qs = notification_qs.filter(created_on__gte=start_date_filter)

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            notification_qs = notification_qs.filter(created_on__lte=end_date_filter)

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            notification_qs = notification_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )
        paginator = Paginator(notification_qs, 10)
        page_number = request.GET.get("page")
        paginated_notifications = paginator.get_page(page_number)
        context = dict(
            notifications=paginated_notifications,
            is_notification=True,
            search=search,
            start_date_filter=start_date_filter,
            end_date_filter=end_date_filter,
        )
        return render(request, "notification/notifications.html", context)


class NotificationDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            notification_obj = PushNotification.objects.get(pk=id)
        except:
            return JsonResponse(
                {"status": False, "message": "Notification does not exist"}
            )

        return JsonResponse(
            {
                "status": True,
                "notification": notification_obj.to_json(),
                "users": list(
                    notification_obj.users.all().values_list("email", flat=True)
                ),
                "users_count": notification_obj.users.all().count(),
            }
        )


class NewNotificationView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_notification=True, users=UserModel.objects.filter(is_superuser=False)
        )
        return render(request, "notification/add_notification.html", context)

    def post(self, request):
        users_ids = request.POST.getlist("users")
        title = request.POST.get("title")
        message = request.POST.get("message")

        if not users_ids:
            return JsonResponse(
                {
                    "status": False,
                    "message": "At least one user required",
                }
            )
        if not title or not message:
            return JsonResponse(
                {"status": False, "message": "Title and message are required"}
            )
        try:
            create_notification(
                user_ids=users_ids,
                title=title,
                message=message,
            )
            return JsonResponse(
                {"status": True, "message": "Notification sent successfully"}
            )
        except Exception as e:
            return JsonResponse({"status": False, "message": str(e)})


class UsersSearchListing(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "")
        users = (
            UserModel.objects.exclude(is_superuser=True)
            .filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone_number__icontains=search)
            )
            .values("email", "id")
            .distinct()
        )

        return JsonResponse({"status": True, "users": list(users)})


class NotificationExportView(AdminLoginView):
    def get(self, request, file_type):
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def get_file_name(self):
        current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
        return f"notifications-{current_timestamp}"

    def get_headers(self):
        return ["Notification ID", "Title", "Message", "Created On", "Users"]

    def get_queryset(self, request):
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        notification_qs = PushNotification.objects.all().order_by("-created_on")

        if search:
            notification_qs = notification_qs.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            notification_qs = notification_qs.filter(created_on__gte=start_date_filter)

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            notification_qs = notification_qs.filter(created_on__lte=end_date_filter)

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            notification_qs = notification_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )
        return notification_qs

    def get_data_row(self, object, request):
        return [
            str(object.pk),
            object.title,
            object.message,
            object.created_on.strftime("%Y-%m-%d"),
            ";".join(list(object.users.all().values_list("email", flat=True))),
        ]

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_file_name()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            writer.writerow(row)
        return response

    def excel_export(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_file_name()}.xlsx"
        )
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response
