from .base import AdminLoginView
from django.shortcuts import render, redirect


class DashboardView(AdminLoginView):
    def get(self, request):
        return render(request, "dashboard.html")
