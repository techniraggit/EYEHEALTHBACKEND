from utilities.utils import get_object_or_none
from django.shortcuts import get_object_or_404
import datetime
from django.template.loader import render_to_string
from utilities.services.email import send_email
from django.core.paginator import Paginator
from django.shortcuts import render
from .base import AdminLoginView
from django.http import JsonResponse
import logging
from admin_panel.forms.stores import BusinessModelForm, StoreForm
from utilities.utils import generate_password
from django.contrib import messages
from django.shortcuts import redirect
from store.models.models import Stores, BusinessModel, Services, StoreImages
from store.models.appointments import StoreAvailability, Days, StoreAppointment
from django.core.exceptions import ValidationError
from utilities.utils import get_form_error_msg
from api.models.accounts import UserModel
from django.db.models import Q
from django.db import transaction

logger = logging.getLogger(__name__)


def validate_opening_and_closing_time(opening_time, closing_time):
    try:
        # Check if both times are provided
        if not opening_time or not closing_time:
            return "Both opening time and closing time must be provided."

        # Parse the times to ensure they are valid
        opening_time_obj = datetime.datetime.strptime(opening_time, "%H:%M").time()
        closing_time_obj = datetime.datetime.strptime(closing_time, "%H:%M").time()

        # Validate that opening time is earlier than closing time
        if opening_time_obj >= closing_time_obj:
            return "Opening time must be earlier than closing time."

        # If all validations pass
        return None
    except ValueError:
        return "Invalid time format. Please use HH:MM format."


class BusinessView(AdminLoginView):
    def get(self, request):
        companies = BusinessModel.objects.all().order_by("-created_on")
        paginator = Paginator(companies, 10)
        page_number = request.GET.get("page")
        paginated_companies = paginator.get_page(page_number)
        context = dict(
            paginated_companies=paginated_companies,
            is_business=True,
        )
        return render(request, "store/business_listing.html", context)


class BusinessDetailView(AdminLoginView):
    def get(self, request):
        business_id = request.GET.get("id")
        try:
            business = BusinessModel.objects.get(id=business_id)
        except:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Business does not exist",
                }
            )

        return JsonResponse(
            {
                "status": True,
                "data": business.to_json(),
            }
        )


class BusinessAddView(AdminLoginView):
    def get(self, request):
        return render(
            request,
            "store/business_add.html",
        )

    def post(self, request):
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        logo = request.FILES.get("logo")
        status = request.POST.get("status", "") == "active"
        if not all([name, phone, email]):
            return JsonResponse(
                {
                    "status": False,
                    "message": "Name, phone and email are required",
                }
            )

        existing_user = UserModel.objects.filter(
            Q(email=email) | Q(phone_number=phone)
        ).first()
        if existing_user and existing_user.email == email:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Email already exists",
                }
            )

        if existing_user and existing_user.phone_number == phone:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Phone Number already exists",
                }
            )
        try:
            with transaction.atomic():
                raw_password = generate_password()
                user_obj = UserModel.objects.create(
                    email=email,
                    phone_number=phone,
                    is_active=status,
                )
                user_obj.set_password(raw_password)
                user_obj.save()
                business_obj = BusinessModel.objects.create(
                    name=name,
                    logo=logo,
                    user=user_obj,
                )

                # send password email to new business
                email_body = render_to_string(
                    "email/send_password.html",
                    {"name": name, "password": raw_password},
                )
                send_email(
                    subject="Welcome to EyeCare",
                    message=email_body,
                    recipients=[email],
                )

                return JsonResponse(
                    {
                        "status": True,
                        "message": "Business added successfully",
                    }
                )
        except Exception as e:
            # user_obj.delete()
            return JsonResponse(
                {
                    "status": False,
                    "message": "Failed to add business",
                    "error": str(e),
                }
            )


class BusinessStoreView(AdminLoginView):
    def get(self, request, business_id):
        try:
            business_obj = BusinessModel.objects.get(id=business_id)
        except:
            messages.error(request, "Business does not exist")
            return redirect("business_view")
        stores = Stores.objects.filter(business=business_obj)
        context = dict(business_name=business_obj.name, stores=stores)
        return render(request, "store/business_store_listing.html", context)


class StoreView(AdminLoginView):
    def get(self, request, store_id=None):
        if store_id:
            try:
                store = Stores.objects.get(id=store_id)
                store_images = [
                    f"{request.build_absolute_uri(i.image.url)}"
                    for i in store.images.all()
                ]
                return JsonResponse(
                    {
                        "status": True,
                        "data": store.to_json(),
                        "images": store_images,
                    }
                )
            except Stores.DoesNotExist:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Store does not exist",
                    }
                )
            except Exception as e:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "An error occurred",
                        "error": str(e),
                    }
                )

        stores = Stores.objects.all().order_by("-created_on")
        paginator = Paginator(stores, 10)
        page_number = request.GET.get("page")
        paginated_stores = paginator.get_page(page_number)
        context = dict(
            is_store=True,
            paginated_stores=paginated_stores,
        )
        return render(request, "store/store_listing.html", context)


class AddStoreView(AdminLoginView):
    def get(self, request):
        businesses_qs = BusinessModel.objects.all()
        services_qs = Services.objects.all()
        context = dict(
            businesses=businesses_qs,
            services=services_qs,
            is_store=True,
        )
        return render(request, "store/add_store.html", context=context)

    def post(self, request):
        from django.db import transaction

        services_lst = request.POST.getlist("service")
        opening_time = request.POST.get("opening_time")
        closing_time = request.POST.get("closing_time")
        images = request.FILES.getlist("images[]")
        form = StoreForm(request.POST, request.FILES)

        error = validate_opening_and_closing_time(opening_time, closing_time)
        if error:
            return JsonResponse(
                {
                    "status": False,
                    "message": error,
                },
            )

        if form.is_valid():
            services_qs = Services.objects.filter(id__in=services_lst)
            if services_qs.exists():
                instance = form.save()
                instance.services.add(
                    *services_qs
                )  # Add services to the store instance
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Some of the selected services are invalid.",
                    }
                )

            try:
                with transaction.atomic():
                    store_images = [
                        StoreImages(store=instance, image=i) for i in images
                    ]
                    if store_images:
                        StoreImages.objects.bulk_create(store_images)

                    days_qs = Days.objects.all()
                    store_availability_obj = StoreAvailability.objects.create(
                        store=instance,
                        start_working_hr=opening_time,
                        end_working_hr=closing_time,
                    )
                    store_availability_obj.days.set(days_qs)
                    return JsonResponse(
                        {
                            "status": True,
                            "message": "Store added successfully",
                        }
                    )

            except ValidationError as e:
                instance.delete()
                return JsonResponse(
                    {
                        "status": False,
                        "message": f"Error occurred while saving the store: {str(e)}",
                    }
                )
            except Exception as e:
                instance.delete()
                return JsonResponse(
                    {
                        "status": False,
                        "message": "An error occurred while saving the store",
                        "error": str(e),
                    }
                )
        return JsonResponse(
            {
                "status": False,
                "message": get_form_error_msg(form.errors.as_json()),
            }
        )


class EditStoreView(AdminLoginView):
    def get(self, request, store_id):
        try:
            # Retrieve the store instance by ID
            store_instance = Stores.objects.get(id=store_id)
        except Stores.DoesNotExist:
            return JsonResponse({"status": False, "message": "Store not found."})

        # Fetch related businesses and services for the dropdowns
        businesses_qs = BusinessModel.objects.all()
        services_qs = Services.objects.all()

        # Prepare context for rendering the edit form
        store_images = [
            f"{request.build_absolute_uri(i.image.url)}"
            for i in store_instance.images.all()
        ]
        context = dict(
            store=store_instance,
            store_availability=StoreAvailability.objects.filter(
                store=store_instance
            ).first(),
            businesses=businesses_qs,
            services=services_qs,
            service_ids=store_instance.services.all().values_list("id", flat=True),
            store_images=store_images,
            is_store=True,
        )
        return render(request, "store/store_edit.html", context=context)

    def post(self, request, store_id):
        try:
            # Retrieve the store instance to update
            store_instance = Stores.objects.get(id=store_id)
        except Stores.DoesNotExist:
            return JsonResponse({"status": False, "message": "Store not found."})

        # Get updated data from the form
        services_lst = request.POST.getlist("service")
        opening_time = request.POST.get("opening_time")
        closing_time = request.POST.get("closing_time")
        images = request.FILES.getlist("images[]")
        form = StoreForm(request.POST, request.FILES, instance=store_instance)

        error = validate_opening_and_closing_time(opening_time, closing_time)
        if error:
            return JsonResponse(
                {
                    "status": False,
                    "message": error,
                },
                status=400,
            )

        if form.is_valid():
            # Update the store instance
            instance = form.save()

            # Update the services related to the store
            services_qs = Services.objects.filter(id__in=services_lst)
            if services_qs.exists():
                instance.services.set(services_qs)  # Update related services
            else:
                return JsonResponse(
                    {
                        "status": False,
                        "message": "Some of the selected services are invalid.",
                    }
                )

            try:
                # Update images by clearing old ones and adding new ones
                if images:
                    StoreImages.objects.filter(store=instance).delete()
                    store_images = [
                        StoreImages(store=instance, image=i) for i in images
                    ]
                    StoreImages.objects.bulk_create(store_images)

                # days_qs = Days.objects.all()
                store_availability_obj = StoreAvailability.objects.filter(
                    store=instance
                ).first()
                store_availability_obj.start_working_hr = opening_time
                store_availability_obj.end_working_hr = closing_time
                store_availability_obj.save()
                # store_availability_obj.days.add(days_qs)

                return JsonResponse(
                    {
                        "status": True,
                        "message": "Store updated successfully",
                    }
                )

            except ValidationError as e:
                return JsonResponse(
                    {
                        "status": False,
                        "message": f"Error occurred while updating the store: {str(e)}",
                    }
                )

        # If the form is invalid, return the error messages
        return JsonResponse(
            {
                "status": False,
                "message": get_form_error_msg(form.errors.as_json()),
            }
        )


class DeleteStoreView(AdminLoginView):
    def get(self, request, store_id):
        try:
            # Retrieve the store instance to delete
            store_instance = Stores.objects.get(id=store_id)
        except Stores.DoesNotExist:
            return JsonResponse({"status": False, "message": "Store not found."})

        # Delete the store instance
        store_instance.delete()

        return JsonResponse({"status": True, "message": "Store deleted successfully."})


class UpdateStoreStatus(AdminLoginView):
    def post(self, request):
        store_id = request.POST.get("id")
        store_obj = get_object_or_none(Stores, id=store_id)
        if not store_obj:
            return JsonResponse({"status": False, "message": "Store not found."})
        store_obj.is_active = not store_obj.is_active
        store_obj.save()
        return JsonResponse({"status": True, "is_active": store_obj.is_active})


class AppointmentView(AdminLoginView):
    def get(self, request):
        appointments = StoreAppointment.objects.all().order_by("date")
        paginator = Paginator(appointments, 10)
        page_number = request.GET.get("page")
        paginated_appointments = paginator.get_page(page_number)
        context = dict(
            paginated_appointments=paginated_appointments,
            is_appointment=True,
        )
        return render(request, "store/appointment_listing.html", context)


class UpdateAppointmentStatusView(AdminLoginView):
    def post(self, request):
        appointment_id = request.POST.get("appointment_id")
        new_status = request.POST.get("status")

        if not appointment_id or not new_status:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Invalid data",
                }
            )

        try:
            appointment = StoreAppointment.objects.get(id=appointment_id)
            appointment.status = new_status
            appointment.save()

            return JsonResponse(
                {
                    "status": True,
                    "message": "Status updated successfully",
                    "updated_status": appointment.status,
                }
            )
        except StoreAppointment.DoesNotExist:
            return JsonResponse({"status": False, "message": "Appointment not found"})
        except Exception as e:
            return JsonResponse(
                {"status": False, "message": f"An error occurred: {str(e)}"}
            )


class AppointmentDetailView(AdminLoginView):
    def get(self, request, appointment_id):
        try:
            appointment_instance = StoreAppointment.objects.get(id=appointment_id)
        except StoreAppointment.DoesNotExist:
            return JsonResponse({"status": False, "message": "Appointment not found."})

        return JsonResponse(
            {
                "status": True,
                "data": appointment_instance.to_json(),
            }
        )


class BusinessEditView(AdminLoginView):
    def get(self, request, business_id):
        try:
            # Retrieve the business instance by ID
            business_instance = BusinessModel.objects.get(id=business_id)
        except BusinessModel.DoesNotExist:
            return JsonResponse({"status": False, "message": "Business not found."})

        # Prepare context for rendering the edit form
        context = dict(
            business=business_instance,
            is_business=True,
        )
        return render(request, "store/business_edit.html", context)

    def post(self, request, business_id):
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        logo = request.FILES.get("logo")
        status = request.POST.get("status", "") == "active"
        if not all([name, phone, email]):
            return JsonResponse(
                {
                    "status": False,
                    "message": "Name, phone and email are required",
                }
            )

        try:
            # Retrieve the business instance to update
            business_instance = BusinessModel.objects.get(id=business_id)
        except BusinessModel.DoesNotExist:
            return JsonResponse({"status": False, "message": "Business not found."})

        existing_user = (
            UserModel.objects.filter(Q(email=email) | Q(phone_number=phone))
            .exclude(id=business_instance.user.id)
            .first()
        )
        if existing_user and existing_user.email == email:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Email already exists",
                }
            )

        if existing_user and existing_user.phone_number == phone:
            return JsonResponse(
                {
                    "status": False,
                    "message": "Phone Number already exists",
                }
            )

        try:
            business_instance.name = name
            business_instance.user.phone_number = phone
            business_instance.user.email = email
            business_instance.user.is_active = status
            business_instance.user.save()
            business_instance.save()
            return JsonResponse(
                {
                    "status": True,
                    "message": "Business updated successfully",
                }
            )
        except Exception as e:
            return JsonResponse(
                {"status": False, "message": f"An error occurred: {str(e)}"}
            )

        # # Get updated data from the form
        # form = BusinessModelForm(request.POST, instance=business_instance)

        # if form.is_valid():
        #     # Update the business instance
        #     instance = form.save()

        #     return JsonResponse(
        #         {
        #             "status": True,
        #             "message": "Business updated successfully",
        #         }
        #     )

        # # If the form is invalid, return the error messages
        # return JsonResponse(
        #     {
        #         "status": False,
        #         "message": get_form_error_msg(form.errors.as_json()),
        #     }
        # )


class UpdateBusinessStatus(AdminLoginView):
    def post(self, request):
        company_id = request.POST.get("id")
        company = get_object_or_none(BusinessModel, id=company_id)
        if not company:
            return JsonResponse({"status": False, "message": "Company not found."})
        company.user.is_active = not company.user.is_active
        company.user.save()
        return JsonResponse({"status": True, "is_active": company.user.is_active})
