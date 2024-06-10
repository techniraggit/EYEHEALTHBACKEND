from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View


# Create your views here.
class AdminLoginView(LoginRequiredMixin, View):
    pass
