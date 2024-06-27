from utilities.services.notification import create_notification
from openpyxl import Workbook
import csv
from django.http import HttpResponse
from datetime import datetime
from openpyxl.writer.excel import save_virtual_workbook
from utilities.utils import time_localize
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
from django.db.models import Q

from django.core.paginator import Paginator


class OffersView(AdminLoginView):
    def get(self, request):
        search = str(request.GET.get("search", "")).strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        offer_status_filter = request.GET.get("offer_status_filter")

        offers_qs = Offers.objects.all().order_by("-created_on")

        if search:
            offers_qs = offers_qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(status=str(search).lower())
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            offers_qs = offers_qs.filter(created_on__date__gte=start_date_filter)

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            offers_qs = offers_qs.filter(created_on__date__lte=end_date_filter)

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            offers_qs = offers_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )

        if offer_status_filter:
            offers_qs = offers_qs.filter(status=offer_status_filter)

        paginator = Paginator(offers_qs, 10)
        page_number = request.GET.get("page")
        paginated_offers = paginator.get_page(page_number)
        context = dict(
            paginated_offers=paginated_offers,
            is_offer=True,
            search=search if search else "",
            start_date_filter=start_date_filter,
            end_date_filter=end_date_filter,
            offer_status_filter=offer_status_filter,
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
            return JsonResponse({"status": False, "message": "Offer does not exist"})

        offer_form = OffersForm(request.POST, request.FILES, instance=offer_obj)
        if offer_form.is_valid():
            offer_obj = offer_form.save(commit=False)
            offer_obj.updated_by = request.user
            offer_obj.update_offer_status()
            offer_obj.save()
            return JsonResponse(
                {"status": True, "message": "Offer has been updated successfully"}
            )
        else:
            errors = offer_form.errors.as_json()
            parsed_data = json.loads(errors)
            first_key = next(iter(parsed_data))
            first_object = parsed_data[first_key][0]
            message = (
                f"{first_key.title().replace('_', ' ')}: {first_object['message']}"
            )
            return JsonResponse({"status": False, "message": message})


class OfferDetailedView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except Offers.DoesNotExist:
            return JsonResponse({"status": False, "message": "Offer does not exist"})

        offer_data = dict(
            offer_id=offer_obj.offer_id,
            title=offer_obj.title,
            image=offer_obj.image.url if offer_obj.image else "",
            description=offer_obj.description,
            expiry_date=time_localize(offer_obj.expiry_date).strftime("%Y-%m-%d"),
            status=offer_obj.status,
            required_points=offer_obj.required_points,
        )
        return JsonResponse(offer_data)


class DeleteOfferView(AdminLoginView):
    def get(self, request, id):
        try:
            offer_obj = Offers.objects.get(pk=id)
        except Offers.DoesNotExist:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Offer does not exist",
                    "redirect_url": reverse("offers_view"),
                }
            )
        offer_obj.delete()
        return JsonResponse(
            {
                "status": True,
                "message": "Offer has been deleted successfully",
                "redirect_url": reverse("offers_view"),
            }
        )


class RedeemedOffersView(AdminLoginView):
    def get(self, request):
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        status_filter = request.GET.get("status_filter")

        redeemed_offer_qs = UserRedeemedOffers.objects.all().order_by("-redeemed_on")

        if search:
            redeemed_offer_qs = redeemed_offer_qs.filter(
                Q(offer__title__icontains=search)
                | Q(offer__description__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            redeemed_offer_qs = redeemed_offer_qs.filter(
                redeemed_on__date__gte=start_date_filter
            )

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            redeemed_offer_qs = redeemed_offer_qs.filter(
                redeemed_on__date__lte=end_date_filter
            )

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            redeemed_offer_qs = redeemed_offer_qs.filter(
                redeemed_on__date__range=(start_date_filter, end_date_filter)
            )

        if status_filter:
            redeemed_offer_qs = redeemed_offer_qs.filter(status=status_filter)

        paginator = Paginator(redeemed_offer_qs, 10)
        page_number = request.GET.get("page")
        paginated_redeemed_offers = paginator.get_page(page_number)
        context = dict(
            redeemed_offers=paginated_redeemed_offers,
            is_redeemed_offers=True,
            search=search,
            start_date_filter=start_date_filter,
            end_date_filter=end_date_filter,
            status_filter=status_filter,
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
        create_notification(
            user_ids=[redeemed_offer_obj.user.id],
            title="Your offer has been dispatched",
            message=f"Your offer with title '{redeemed_offer_obj.offer.title}' has been dispatched",
        )

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
            create_notification(
                user_ids=[redeemed_offer_obj.user.id],
                title="You have received an email regarding your redeemed offer",
                message=f"You have received an email regarding your redeemed offer with title '{redeemed_offer_obj.offer.title}'",
            )
            return JsonResponse({"status": True, "message": "Email sent successfully"})

        return JsonResponse({"status": False, "message": "Email not sent"})

    def get_redeemed_offer(self, redeemed_offer_id):
        try:
            return UserRedeemedOffers.objects.get(pk=redeemed_offer_id)
        except UserRedeemedOffers.DoesNotExist:
            return None


class OfferExportView(AdminLoginView):
    def get(self, request, file_type):
        print("file_type: ", file_type)
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def get_file_name(self):
        current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
        return f"offers-{current_timestamp}"

    def get_headers(self):
        return [
            "Title",
            "Image",
            "Description",
            "Expiry Date",
            "Status",
            "Required Points",
            "Created By",
        ]

    def get_queryset(self, request):
        search = str(request.GET.get("search", "")).strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        offer_status_filter = request.GET.get("offer_status_filter")

        offers_qs = Offers.objects.all().order_by("-created_on")

        if search:
            offers_qs = offers_qs.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(status=str(search).lower())
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            offers_qs = offers_qs.filter(created_on__date__gte=start_date_filter)

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            offers_qs = offers_qs.filter(created_on__date__lte=end_date_filter)

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            offers_qs = offers_qs.filter(
                created_on__date__range=(start_date_filter, end_date_filter)
            )

        if offer_status_filter:
            offers_qs = offers_qs.filter(status=offer_status_filter)

        return offers_qs

    def get_data_row(self, object, request):
        return [
            object.title,
            request.build_absolute_uri(object.image.url) if object.image else "",
            object.description,
            object.expiry_date.strftime("%Y-%m-%d"),
            object.status,
            object.required_points,
            object.created_by.get_full_name(),
        ]

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_file_name()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            writer.writerow(row)
        return response

    def excel_export(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_file_name()}.xlsx"
        )
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response


class RedeemedOffersExportView(AdminLoginView):
    def get(self, request, file_type):
        if file_type == "csv":
            return self.csv_export(request)
        elif file_type == "excel":
            return self.excel_export(request)
        else:
            return HttpResponse("Invalid file type")

    def get_file_name(self):
        current_timestamp = time_localize(datetime.now()).strftime("%Y%m%d%H%M%S")
        return f"user-redeemed-offers-{current_timestamp}"

    def get_headers(self):
        return [
            "ID",
            "User Email",
            "Offer ID",
            "Status",
            "Redeemed On",
            "Emailed On",
            "Dispatch On",
        ]

    def get_queryset(self, request):
        search = request.GET.get("search", "").strip()
        start_date_filter = request.GET.get("start_date_filter")
        end_date_filter = request.GET.get("end_date_filter")
        status_filter = request.GET.get("status_filter")

        redeemed_offer_qs = UserRedeemedOffers.objects.all().order_by("-redeemed_on")

        if search:
            redeemed_offer_qs = redeemed_offer_qs.filter(
                Q(offer__title__icontains=search)
                | Q(offer__description__icontains=search)
                | Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
            )

        if start_date_filter and not end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            redeemed_offer_qs = redeemed_offer_qs.filter(
                redeemed_on__date__gte=start_date_filter
            )

        if end_date_filter and not start_date_filter:
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            redeemed_offer_qs = redeemed_offer_qs.filter(
                redeemed_on__date__lte=end_date_filter
            )

        if start_date_filter and end_date_filter:
            start_date_filter = datetime.strptime(start_date_filter, "%Y-%m-%d").date()
            end_date_filter = datetime.strptime(end_date_filter, "%Y-%m-%d").date()
            redeemed_offer_qs = redeemed_offer_qs.filter(
                redeemed_on__date__range=(start_date_filter, end_date_filter)
            )

        if status_filter:
            redeemed_offer_qs = redeemed_offer_qs.filter(status=status_filter)
        return redeemed_offer_qs

    def get_data_row(self, object, request):
        return [
            str(object.pk),
            object.user.email,
            str(object.offer.pk),
            object.status.title(),
            object.redeemed_on.strftime("%Y-%m-%d") if object.redeemed_on else None,
            object.emailed_on.strftime("%Y-%m-%d") if object.emailed_on else None,
            object.dispatch_on.strftime("%Y-%m-%d") if object.dispatch_on else None,
        ]

    def csv_export(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.get_file_name()}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            writer.writerow(row)
        return response

    def excel_export(self, request):
        workbook = Workbook()
        worksheet = workbook.active
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        worksheet.append(self.get_headers())
        for user in self.get_queryset(request):
            row = self.get_data_row(user, request)
            worksheet.append(row)

        worksheet.column_dimensions["A"].width = 10
        worksheet.column_dimensions["B"].width = 15
        worksheet.column_dimensions["C"].width = 15
        worksheet.column_dimensions["D"].width = 15
        worksheet.column_dimensions["E"].width = 20
        worksheet.column_dimensions["F"].width = 20
        worksheet.column_dimensions["G"].width = 10

        virtual_excel_file = save_virtual_workbook(workbook)
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_file_name()}.xlsx"
        )
        response["Content-Type"] = "application/octet-stream"
        response.write(virtual_excel_file)
        return response
