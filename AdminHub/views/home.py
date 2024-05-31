from .base import AdminLoginView
from django.shortcuts import render


class HomeView(AdminLoginView):
    def get(self, request):
        context = dict(
            is_home=True,
        )
        return render(request, "home/home.html", context)
