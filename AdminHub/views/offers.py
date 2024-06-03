from .base import AdminLoginView
from django.shortcuts import render
from api.models.rewards import Offers, UserRedeemedOffers


class OffersView(AdminLoginView):
    def get(self, request):
        offers = Offers.objects.all()
        context = dict(
            offers=offers,
            is_offer=True,
        )
        return render(request, "offers/offers.html", context)


class RedeemedOffersView(AdminLoginView):
    def get(self, request):
        redeemed_offers = UserRedeemedOffers.objects.all()
        context = dict(
            redeemed_offers=redeemed_offers,
            is_redeemed_offers=True,
        )
        return render(request, "offers/redeemed_offers.html", context)
