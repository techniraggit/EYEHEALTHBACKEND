from django.db.models import Q
from .base import AdminLoginView
from django.shortcuts import render
from api.models.notifications import PushNotification, UserModel
from django.core.paginator import Paginator
from utilities.services.notification import create_notification
from django.http import JsonResponse


class NotificationView(AdminLoginView):
    def get(self, request):
        notifications = PushNotification.objects.all().order_by("-created_on")
        paginator = Paginator(notifications, 10)
        page_number = request.GET.get("page")
        paginated_notifications = paginator.get_page(page_number)
        context = dict(
            notifications=paginated_notifications,
            is_notification=True,
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
