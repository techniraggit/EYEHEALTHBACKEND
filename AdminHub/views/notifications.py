from .base import AdminLoginView
from django.shortcuts import render
from api.models.notifications import PushNotification



class NotificationView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        notifications = PushNotification.objects.all()
        context = dict(
            notifications = notifications,
            is_notification = True,
        )
        return render(request, "notification/notifications.html", context)