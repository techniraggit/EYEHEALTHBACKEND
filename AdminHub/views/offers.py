from .base import AdminLoginView
from django.shortcuts import render
from api.models.rewards import Offers



class OffersView(AdminLoginView):
    records_per_page = 10
    def get(self, request):
        offers = Offers.objects.all()
        context = dict(
            offers = offers,
            is_offer = True,
        )
        return render(request, "offers/offers.html", context)