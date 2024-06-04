from .base import AdminLoginView
from django.shortcuts import render, redirect
from api.models.rewards import Offers, UserRedeemedOffers
from AdminHub.forms.offers import OffersForm
from django.contrib import messages


class OffersView(AdminLoginView):
    def get(self, request):
        offers = Offers.objects.all().order_by("-created_on")
        context = dict(
            offers=offers,
            is_offer=True,
        )
        return render(request, "offers/offers.html", context)

from django.http import JsonResponse
from django.urls import reverse
class AddOffersView(AdminLoginView):
    def get(self, request):
        offer_form = OffersForm()
        context = dict(
            offer_form=offer_form,
            is_offer=True,
        )
        return render(request, "offers/add_offer.html", context)

    def post(self, request):
        try:
            print("here>>>>>>>>>>>>>>>>>>>>>>>>")
            offer_form = OffersForm(request.POST, request.FILES)
            if offer_form.is_valid():
                offer_obj = offer_form.save(commit=False)
                offer_obj.created_by = request.user
                offer_obj.updated_by = request.user
                offer_obj.save()
                # messages.success(request, "Offer added successfully")
                response = {
                    "success": True,
                    "message": "Offer added successfully",
                    "redirect_url": reverse("offers_view"),
                }
                return JsonResponse(response, status=200)

            errors = offer_form.errors.as_json()
            response = {
                "success": False,
                "errors": errors,
                "redirect_url": reverse("add_offer_view"),
            }
            return JsonResponse(response, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "message":str(e)}, status=400)


class EditOfferView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except:
            messages.error(request, "Offer does not exist")
            return redirect("offers_view")
        context = dict(
            offer_obj=offer_obj,
            is_offer=True,
        )
        return render(request, "offers/edit_offer.html", context)

    def post(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except:
            messages.error(request, "Offer does not exist")
            return redirect("offers_view")
        offer_form = OffersForm(request.POST, request.FILES, instance=offer_obj)
        if offer_form.is_valid():
            offer_obj = offer_form.save(commit=False)
            offer_obj.updated_by = request.user
            offer_obj.save()
            messages.success(request, "Offer has been updated successfully")
        else:
            messages.error(request, offer_form.errors)
        context = dict(
            offer_obj=offer_obj,
            is_offer=True,
        )
        return render(request, "offers/edit_offer.html", context)


class RedeemedOffersView(AdminLoginView):
    def get(self, request):
        redeemed_offers = UserRedeemedOffers.objects.all().order_by("-created_on")
        context = dict(
            redeemed_offers=redeemed_offers,
            is_redeemed_offers=True,
        )
        return render(request, "offers/redeemed_offers.html", context)
