from .base import AdminLoginView
from django.shortcuts import render
from api.models.notifications import PushNotification
from django.core.paginator import Paginator



class NotificationView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        notifications = PushNotification.objects.all()
        paginator = Paginator(notifications, 10)
        page_number = request.GET.get("page")
        paginated_notifications = paginator.get_page(page_number)
        context = dict(
            notifications = paginated_notifications,
            is_notification = True,
        )
        return render(request, "notification/notifications.html", context)