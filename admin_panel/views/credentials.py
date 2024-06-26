from .base import AdminLoginView
from django.shortcuts import render
from django.http import JsonResponse
from admin_panel.models import Credentials


class CredentialsView(AdminLoginView):
    def get(self, request):
        credentials_qs = Credentials.objects.all()

        context = dict(
            is_credentials=True,
            credentials_qs=credentials_qs,
        )
        return render(request, "credentials/credentials.html", context)
