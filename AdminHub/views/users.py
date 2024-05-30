from .base import AdminLoginView
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()


class UserView(AdminLoginView):
    def get(self, request):
        users = User.objects.exclude(id=request.user.id)
        return render(request, "users.html", {"users": users})
