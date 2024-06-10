from django.utils import timezone
from utilities.services.email import send_email
from django.http import JsonResponse
import json
from django.urls import reverse
from .base import AdminLoginView
from django.shortcuts import render, redirect
from api.models.rewards import Offers, UserRedeemedOffers
from admin_panel.forms.offers import OffersForm
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

from utilities.utils import time_localize
class OfferDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except Offers.DoesNotExist:
            return JsonResponse({"status": False, "message": "Offer does not exist"})

        offer_data = dict(
            offer_id = offer_obj.offer_id,
            title = offer_obj.title,
            image = offer_obj.image.url if offer_obj.image else "",
            description = offer_obj.description,
            expiry_date = time_localize(offer_obj.expiry_date).strftime("%Y-%m-%d"),
            status = offer_obj.status,
            required_points = offer_obj.required_points,
        )
        return JsonResponse(offer_data)


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


class EditRedeemedOffer(AdminLoginView):
    def get(self, request, id):
        try:
            redeemed_offer_obj = UserRedeemedOffers.objects.get(pk=id)
        except UserRedeemedOffers.DoesNotExist:
            messages.error(request, "Offer does not exist")
            return redirect("redeemed_offers_view")
        context = dict(
            redeemed_offer_obj=redeemed_offer_obj,
            is_redeemed_offers=True,
            address_obj=(
                redeemed_offer_obj.address if redeemed_offer_obj.address else None
            ),
        )
        return render(request, "offers/edit_redeemed_offers.html", context)


class OfferDispatchView(AdminLoginView):
    def post(self, request):
        required_fields = ["redeemed_offer_id", "dispatch_address"]
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse(
                    {
                        "status": False,
                        "message": f"{field.replace('_', ' ').title()} required",
                    }
                )

        redeemed_offer_id = request.POST.get("redeemed_offer_id")
        dispatch_address = request.POST.get("dispatch_address")

        redeemed_offer_obj = self.get_redeemed_offer(redeemed_offer_id)
        if not redeemed_offer_obj:
            return JsonResponse({"status": False, "message": "Offer does not exist"})

        redeemed_offer_obj.status = "dispatched"
        redeemed_offer_obj.dispatch_address = dispatch_address
        redeemed_offer_obj.dispatch_on = timezone.now()
        redeemed_offer_obj.save()

        return JsonResponse({"status": True, "message": "Offer has been dispatched"})

    def get_redeemed_offer(self, redeemed_offer_id):
        try:
            return UserRedeemedOffers.objects.get(pk=redeemed_offer_id)
        except UserRedeemedOffers.DoesNotExist:
            return None


class OfferEmailView(AdminLoginView):
    def post(self, request):
        required_fields = ["redeemed_offer_id", "email_body", "email_subject"]
        for field in required_fields:
            if not request.POST.get(field):
                return JsonResponse(
                    {
                        "status": False,
                        "message": f"{field.replace('_', ' ').title()} required",
                    }
                )

        redeemed_offer_id = request.POST.get("redeemed_offer_id")
        email_body = request.POST.get("email_body")
        email_subject = request.POST.get("email_subject")

        redeemed_offer_obj = self.get_redeemed_offer(redeemed_offer_id)
        if not redeemed_offer_obj:
            return JsonResponse({"status": False, "message": "Offer does not exist"})

        if send_email(
            subject=email_subject,
            message=email_body,
            recipients=[redeemed_offer_obj.user.email],
        ):
            redeemed_offer_obj.status = "emailed"
            redeemed_offer_obj.emailed_on = timezone.now()
            redeemed_offer_obj.email_body = email_body
            redeemed_offer_obj.email_subject = email_subject
            redeemed_offer_obj.save()
            return JsonResponse({"status": True, "message": "Email sent successfully"})

        return JsonResponse({"status": False, "message": "Email not sent"})

    def get_redeemed_offer(self, redeemed_offer_id):
        try:
            return UserRedeemedOffers.objects.get(pk=redeemed_offer_id)
        except UserRedeemedOffers.DoesNotExist:
            return None
