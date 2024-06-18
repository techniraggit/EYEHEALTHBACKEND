from .base import AdminLoginView
from django.shortcuts import render, redirect
from api.models.notifications import PushNotification, UserModel
from django.core.paginator import Paginator
from django.contrib import messages
from utilities.services.notification import create_notification 
from django.http import JsonResponse



class NotificationView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        notifications = PushNotification.objects.all().order_by("-created_on")
        paginator = Paginator(notifications, 10)
        page_number = request.GET.get("page")
        paginated_notifications = paginator.get_page(page_number)
        context = dict(
            notifications = paginated_notifications,
            is_notification = True,
        )
        return render(request, "notification/notifications.html", context)

class NewNotificationView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_notification = True,
            users = UserModel.objects.filter(is_superuser=False)
        )
        return render(request, "notification/add_notification.html", context)
    
    def post(self, request):
        users_ids = request.POST.getlist('users')
        title = request.POST.get('title')
        message = request.POST.get('message')
        print("users_ids === ", users_ids, type(users_ids))
        print("title === ", title, type(title))
        print("message === ", message, type(message))
        if not users_ids:
            return JsonResponse({
                "status": False,
                "message": "At least one user required",
            })
        if not title or not message:
            return JsonResponse({
                "status": False,
                "message": "Title and message are required"
            })
        try:
            create_notification(
                user_ids=users_ids,
                title=title,
                message=message,
            )
            return JsonResponse({
                "status": True,
                "message": "Notification sent successfully"
            })
        except Exception as e:
            return JsonResponse({
                "status": False,
                "message": str(e)
            })