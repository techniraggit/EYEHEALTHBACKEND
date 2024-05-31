from .base import AdminLoginView
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

User = get_user_model()


class UserView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        page_number = request.GET.get('page')
        users = User.objects.exclude(id=request.user.id)
        paginator = Paginator(users, self.records_per_page)
        paginated_users = paginator.get_page(page_number)
        return render(request, "users/users.html", {"users": paginated_users, "is_user": True})

class UserDetailView(AdminLoginView):
    def get(self, request):
        return render(request, "users/edit_user.html",  {"is_user": True})