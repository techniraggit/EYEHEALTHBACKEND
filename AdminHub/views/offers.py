from django.http import JsonResponse
import json
from django.urls import reverse
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
            offer_form = OffersForm(request.POST, request.FILES)
            if offer_form.is_valid():
                offer_obj = offer_form.save(commit=False)
                offer_obj.created_by = request.user
                offer_obj.updated_by = request.user
                offer_obj.save()
                response = {
                    "status": True,
                    "message": "Offer added successfully",
                    "redirect_url": reverse("offers_view"),
                }
                return JsonResponse(response, status=200)
            else:
                errors = offer_form.errors.as_json()
                parsed_data = json.loads(errors)
                first_key = next(iter(parsed_data))
                first_object = parsed_data[first_key][0]
                message = (
                    f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
                )
                response = {
                    "status": False,
                    "message": message,
                    "redirect_url": reverse("add_offer_view"),
                }
                return JsonResponse(response, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"status": False, "message": str(e)}, status=400)


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
        except Offers.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Offer does not exist"}, status=404
            )

        offer_form = OffersForm(request.POST, request.FILES, instance=offer_obj)
        if offer_form.is_valid():
            offer_obj = offer_form.save(commit=False)
            offer_obj.updated_by = request.user
            offer_obj.save()
            return JsonResponse(
                {"status": True, "message": "Offer has been updated successfully"}
            )
        else:
            errors = offer_form.errors.as_json()
            return JsonResponse({"status": False, "errors": errors}, status=400)


class OfferDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except Offers.DoesNotExist:
            messages.error(request, "Offer does not exist")
            return redirect("offers_view")
        offer_obj = Offers.objects.get(pk=id)
        context = dict(
            offer_obj=offer_obj,
            is_offer=True,
        )
        return render(request, "offers/offer_view.html", context)


class DeleteOfferView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except Offers.DoesNotExist:
            messages.error(request, "Offer does not exist")
            return redirect("offers_view")
        offer_obj.delete()
        messages.success(request, "Offer has been deleted successfully")
        return redirect("offers_view")


class RedeemedOffersView(AdminLoginView):
    def get(self, request):
        redeemed_offers = UserRedeemedOffers.objects.all().order_by("-created_on")
        context = dict(
            redeemed_offers=redeemed_offers,
            is_redeemed_offers=True,
        )
        return render(request, "offers/redeemed_offers.html", context)
