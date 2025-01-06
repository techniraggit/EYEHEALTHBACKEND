import json
import requests

from django.conf import settings
from django.http import Http404
from core.mixins import UserViewMixin
from rest_framework.response import Response
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework.views import APIView
from datetime import datetime
from .utility import store_file_upload_handle, store_reindex_elastic
from .models import (
    StoreAvail,
    Holiday,
    Timing,
    StoreDetail,
    Store,
    Days,
    Services,
    StoreHoliday,
    StoreAppointment,
)
from core.mixins import AdminViewMixin
from .serializers import (
    StoreDetailSerializer,
    DaysSerializer,
    HolidaysSerializer,
    CompleteStoreDetailSerializer,
    TimingSerializer,
    StoreAvailSerializer,
    StoreAvailSerializer2,
    CombineSerializer,
    ServiceSerializer,
    StoreDetailCreateSerializer,
    StoreServiceCreateSerializer,
    StoreServiceDetailSerializer,
)
from django.http import JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder


# Create your views here.
class StoreAvailabilityView(AdminViewMixin):
    @extend_schema(responses={200: StoreAvailSerializer2}, methods=["GET"])
    def get(self, request):
        snippets = StoreAvail.objects.all()
        serializer = StoreAvailSerializer2(snippets, many=True)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=inline_serializer(
            name="StoreAvailabilityCreateSerializer",
            fields={
                "days": serializers.DictField(),
                "holidays": serializers.ListField(child=serializers.IntegerField()),
                "store": serializers.IntegerField(),
            },
        ),
        responses={201: None},
        methods=["POST"],
    )
    def post(self, request):
        try:
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_store_availability",
                data=json.dumps(request.data),
                headers=HEADERS,
            )

            if request_response.status_code == 201:
                store_id = request.data.get("store")
                for day, timeing in request.data.get("days").items():
                    StoreAvail(
                        store_id=store_id, day_id=int(day), timing_id=timeing
                    ).save()
                for holiday in request.data.get("holidays"):
                    StoreHoliday(store_id=store_id, holiday_id=holiday).save()
                store_reindex_elastic()
                return Response(data=dict(status=True, data=None), status=201)
            else:
                return Response(
                    data=dict(status=False, data=request_response.json()["msg"]),
                    status=400,
                )
        except Exception:
            return Response(
                data=dict(
                    status=False,
                    data=dict(success=False, message="Error in store_availability api"),
                ),
                status=400,
            )


class StoreAvailabilityDetailView(AdminViewMixin):
    @staticmethod
    def get_objects(pk):
        try:
            return StoreAvail.objects.filter(store_id=pk)
        except StoreAvail.DoesNotExist:
            raise Http404

    @extend_schema(responses={200: StoreAvailSerializer2}, methods=["GET"])
    def get(self, request, pk):
        snippets = StoreAvailabilityDetailView.get_objects(pk)
        serializer = StoreAvailSerializer2(snippets, many=True)
        store_holidays = StoreHoliday.objects.filter(store_id=pk)
        names = []
        for holiday in store_holidays:
            try:
                holi = Holiday.objects.get(id=holiday.holiday_id)
                names.append({"name": holi.name, "id": holi.id})
            except Exception:
                pass

        return Response(
            data=dict(status=True, data=serializer.data, holidays=names),
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=StoreAvailSerializer,
        responses={200: StoreAvailSerializer},
        methods=["PUT"],
    )
    def put(self, request, pk):
        try:
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/edit_store_availability",
                data=json.dumps(request.data),
                headers=HEADERS,
            )

            if request_response.json()['success']:
                store_id = request.data.get("store_id")
                for day, timing in request.data.get('days').items():
                    s_avail = StoreAvail.objects.filter(store_id = store_id, day_id = int(day)).first()
                    if s_avail:
                        timing_obj = Timing.objects.get(id=timing)
                        s_avail.timing = timing_obj
                        s_avail.save()
                    else:
                        StoreAvail(store_id=store_id, day_id=int(day), timing_id=timing).save()
                
                s_holiday = StoreHoliday.objects.filter(store_id = store_id)
                s_holiday.delete()
                for holiday in request.data.get('holidays'):
                    StoreHoliday(store_id=store_id, holiday_id=holiday).save()
                store_reindex_elastic()
                return Response(data=dict(status=True, data={"message": "Values Updated successfully"}), status=status.HTTP_200_OK)

            return Response(
                data=dict(status=False, data={"message": ""}),
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                data=dict(status=False, data=str(e)),
                status=status.HTTP_400_BAD_REQUEST,
            )


class DaysListView(AdminViewMixin):
    @extend_schema(responses={200: DaysSerializer}, methods=["GET"])
    def get(self, request):
        snippets = Days.objects.all().order_by('-id')
        serializer = DaysSerializer(snippets, many=True)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=DaysSerializer, responses={201: DaysSerializer}, methods=["POST"]
    )
    def post(self, request):
        serializer = DaysSerializer(data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_day/",
                data=request.data,
                headers=HEADERS,
            )

            return Response(
                data=dict(status=True, data=serializer.data),
                status=status.HTTP_201_CREATED,
            )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class HolidaysListView(AdminViewMixin):
    @extend_schema(responses={200: HolidaysSerializer}, methods=["GET"])
    def get(self, request):
        snippets = Holiday.objects.all().order_by('-id')
        serializer = HolidaysSerializer(snippets, many=True)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=HolidaysSerializer,
        responses={201: HolidaysSerializer},
        methods=["POST"],
    )
    def post(self, request):
        serializer = HolidaysSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
            }

            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_holiday/",
                data=serializer.data,
                headers=HEADERS,
            )
            return Response(
                data=dict(status=True, data=serializer.data),
                status=status.HTTP_201_CREATED,
            )

            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=dict(status=True, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class ServiceListView(AdminViewMixin):
    @extend_schema(responses={200: ServiceSerializer}, methods=["GET"])
    def get(self, request):
        snippets = Services.objects.all().order_by('-id')
        serializer = ServiceSerializer(snippets, many=True)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=ServiceSerializer,
        responses={201: ServiceSerializer},
        methods=["POST"],
    )
    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
            }

            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_service/",
                data=request.data,
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class ServiceDetailView(AdminViewMixin):
    def get_object(self, pk):
        try:
            return Services.objects.get(pk=pk)
        except Services.DoesNotExist:
            raise Http404

    @extend_schema(responses={200: ServiceSerializer}, methods=["GET"])
    def get(self, request, pk):
        snippet = self.get_object(pk)
        serializer = ServiceSerializer(snippet)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=ServiceSerializer, responses={200: ServiceSerializer}, methods=["PUT"]
    )
    def put(self, request, pk):
        snippet = self.get_object(pk)
        serializer = ServiceSerializer(snippet, data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
            }

            request_response = requests.put(
                f"{settings.EYEMYEYE_BASE_URL}/store/update_service/<int:{pk}>",
                data=request.data,
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class CombineListView(AdminViewMixin):
    @extend_schema(responses={200: CombineSerializer}, methods=["GET"])
    def get(self, request):
        timings = Timing.objects.all()
        holidays = Holiday.objects.all()
        days = Days.objects.all()
        services = Services.objects.all()

        tim_serial = TimingSerializer(timings, many=True)
        holi_serial = HolidaysSerializer(holidays, many=True)
        days_serial = DaysSerializer(days, many=True)
        serv_serial = ServiceSerializer(services, many=True)
        return Response(
            data=dict(
                status=True,
                data={
                    "timings": tim_serial.data,
                    "holidays": holi_serial.data,
                    "days": days_serial.data,
                    "services": serv_serial.data,
                },
            ),
            status=status.HTTP_200_OK,
        )


class TimingListView(AdminViewMixin):
    @extend_schema(responses={200: TimingSerializer}, methods=["GET"])
    def get(self, request):
        snippets = Timing.objects.all().order_by('-id')
        serializer = TimingSerializer(snippets, many=True)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=TimingSerializer, responses={201: TimingSerializer}, methods=["POST"]
    )
    def post(self, request):
        serializer = TimingSerializer(data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_timing/",
                data=request.data,
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class TimingDetailView(AdminViewMixin):
    def get_object(self, pk):
        try:
            return Timing.objects.get(pk=pk)
        except Timing.DoesNotExist:
            raise Http404

    @extend_schema(responses={200: TimingSerializer}, methods=["GET"])
    def get(self, request, pk):
        snippet = self.get_object(pk)
        serializer = TimingSerializer(snippet)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=TimingSerializer, responses={200: TimingSerializer}, methods=["PUT"]
    )
    def put(self, request, pk):
        snippet = self.get_object(pk)
        serializer = TimingSerializer(snippet, data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/update_timing/{pk}",
                data=json.dumps(request.data),
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class HolidaysListView(AdminViewMixin):
    @extend_schema(responses={200: HolidaysSerializer}, methods=["GET"])
    def get(self, request):
        snippets = Holiday.objects.all()
        serializer = HolidaysSerializer(snippets, many=True)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=HolidaysSerializer,
        responses={201: HolidaysSerializer},
        methods=["POST"],
    )
    def post(self, request):
        serializer = HolidaysSerializer(data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_holiday/",
                data=request.data,
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class HolidaysDetailView(AdminViewMixin):
    def get_object(self, pk):
        try:
            return Holiday.objects.get(pk=pk)
        except Holiday.DoesNotExist:
            raise Http404

    @extend_schema(responses={200: HolidaysSerializer}, methods=["GET"])
    def get(self, request, pk):
        snippet = self.get_object(pk)
        serializer = HolidaysSerializer(snippet)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )

    @extend_schema(
        request=HolidaysSerializer, responses={200: HolidaysSerializer}, methods=["PUT"]
    )
    def put(self, request, pk):  # not worked yet
        snippet = self.get_object(pk)
        serializer = HolidaysSerializer(snippet, data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/update_holiday/{pk}",
                data=json.dumps(request.data),
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class CompleteStoreDetailView(AdminViewMixin):
    def get_object(self, pk):
        try:
            return StoreDetail.objects.select_related("store").get(store__pk=pk)
        except Store.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        snippet = self.get_object(pk)
        serializer = CompleteStoreDetailSerializer(snippet)
        return Response(
            data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
        )


class StoreDetailListView(AdminViewMixin):
    @extend_schema(
        request=StoreDetailCreateSerializer,
        responses={201: StoreDetailSerializer},
        methods=["POST"],
    )
    def post(self, request):
        latest_Store_pk = Store.objects.last().pk
        store_images = request.FILES
        response = store_file_upload_handle(
            latest_Store_pk, store_images, put=True, post=False
        )
        new_request_data = {
            "phone": request.data.get("phone"),
            "description": request.data.get("description"),
            "latitude": request.data.get("latitude"),
            "location": request.data.get("location"),
            "longitude": request.data.get("longitude"),
            "store": request.data.get("store"),
            "images": response,
        }
        serializer = StoreDetailCreateSerializer(data=new_request_data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_store_detail/",
                data=json.dumps(new_request_data),
                headers=HEADERS,
            )
            print(request_response.status_code, f"{settings.EYEMYEYE_BASE_URL}/store/create_store_detail/", "===========")
            if request_response.status_code == 201:
                serializer.save()
                store_reindex_elastic()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class StoreDetailView(AdminViewMixin):
    def get_object(self, pk):
        try:
            return StoreDetail.objects.get(store__pk=pk)
        except StoreDetail.DoesNotExist:
            # raise Http404
            return False

    @extend_schema(responses={200: StoreDetailSerializer}, methods=["GET"])
    def get(self, request, pk):
        snippet = self.get_object(pk)
        if snippet:
            serializer = StoreDetailSerializer(snippet)
            return Response(
                data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
            )
        return Response(
            data=dict(status=False, data={"msg": "Not Found"}),
            status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        request=StoreDetailCreateSerializer,
        responses={200: StoreDetailSerializer},
        methods=["PUT"],
    )
    def put(self, request, pk):
        snippet = self.get_object(pk)
        store_images = request.FILES
        response = store_file_upload_handle(pk, store_images, put=True, post=False)
        new_request_data = {
            "phone": request.data.get("phone"),
            "description": request.data.get("description"),
            "latitude": request.data.get("latitude"),
            "location": request.data.get("location"),  # lcoation
            "longitude": request.data.get("longitude"),
            "store": request.data.get("store"),
            "images": response,
        }
        serializer = StoreDetailSerializer(snippet, data=new_request_data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/update_store_detail/{pk}",
                data=json.dumps(new_request_data),
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                serializer.save()
                store_reindex_elastic()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class StoreappointmentListView(APIView):
    def post(self, request):
        try:
            # STATIC_TOKEN = settings.STATIC_TOKEN
            # request_token = request.headers.get('Authorization')
            # if request_token != f'Token {STATIC_TOKEN}':
            #     return JsonResponse({'message': 'Invalid or missing authentication token'}, status=401)
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone_number = request.POST.get("phone_number")
            date = request.POST.get("date")
            store_id = request.POST.get("store_id")
            gender = request.POST.get("gender")
            startslot_time = request.POST.get("startslot_time")
            endslot_time = request.POST.get("endslot_time")
            service = request.POST.get("service")
            productlink = request.POST.get("productlink")
            if not productlink:
                productlink = ""

            if (
                not name
                or not email
                or not phone_number
                or not store_id
                or not date
                or not startslot_time
                or not endslot_time
                or not service
            ):
                return HttpResponse(
                    json.dumps(
                        {
                            "success": False,
                            "data": None,
                            "error": "All fields are required in the request",
                        }
                    ),
                    content_type="application/json",
                )
            if not Store.objects.filter(id=store_id).exists():
                return HttpResponse(
                    json.dumps(
                        {
                            "success": False,
                            "data": None,
                            "error": "Store not found with the given store_id",
                        }
                    ),
                    content_type="application/json",
                )
            date_obj = datetime.strptime(date, "%d/%m/%Y")
            start_time_obj = datetime.strptime(startslot_time, "%H:%M").time()
            end_time_obj = datetime.strptime(endslot_time, "%H:%M").time()

            # Create and save StoreAppointment object
            appointment = StoreAppointment(
                name=name,
                email=email,
                phone_number=phone_number,
                gender=gender,  # You may need to adjust this based on your data
                date_of_slot=date_obj,
                start_slot_time=start_time_obj,
                end_slot_time=end_time_obj,
                store_id=store_id,
                service=service,
                productlink=productlink,
            )
            appointment.save()

            return HttpResponse(
                json.dumps(
                    {
                        "success": True,
                        "data": "Appointment Sucessfully  booked",
                        "error": None,
                    }
                ),
                content_type="application/json",
            )
        except Exception:
            return JsonResponse(
                status=400,
                data=dict(success=False, msg="Error in booking appointment api"),
            )

class StoreAppoitmentView(UserViewMixin):
    def get(self, request):
        store_obj = request.user.store
        all_appointments = (
            StoreAppointment.objects.filter(store=store_obj)
            .select_related("store")
            .values(
                "store__store_name",
                "name",
                "id",
                "email",
                "phone_number",
                "gender",
                "date_of_slot",
                "start_slot_time",
                "end_slot_time",
                "service",
                "status",
                "productlink",
            )
            .order_by("-id")
        )
        serialized_data = json.dumps(
            {"success": True, "data": list(all_appointments), "error": None},
            default=str,
            cls=DjangoJSONEncoder,
        )
        return HttpResponse(serialized_data, content_type="application/json")

    def delete(self, request):
        try:
            appoitment_id = request.data.get("id")
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }

            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/store_appointment_delete/{appoitment_id}",
                data=json.dumps({"pk": appoitment_id}),
                headers=HEADERS,
            )
            if (
                request_response.status_code == 200
                and request_response.json()["success"]
            ):
                StoreAppointment.objects.filter(pk=appoitment_id).update(status=False)
                return Response(
                    data=dict(
                        status=True,
                        data={
                            "success": True,
                            "message": "Appointment cancle successfully",
                        },
                    ),
                    status=status.HTTP_200_OK,
                )
        except:
            return Response(
                {"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND
        )

class StoreServiceListView(AdminViewMixin):
    @extend_schema(
        request=StoreServiceCreateSerializer,
        responses={201: StoreServiceCreateSerializer},
        methods=["POST"],
    )
    def post(self, request):
        serializer = StoreServiceCreateSerializer(data=request.data)
        if serializer.is_valid():
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }
            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/create_store_service/",
                data=json.dumps(request.data),
                headers=HEADERS,
            )
            if request_response.status_code == 201:
                std = StoreDetail.objects.filter(
                    store_id=request.data.get("store_id")
                ).first()
                for service in Services.objects.filter(
                    id__in=request.data.get("services")
                ):
                    std.services.add(service)

                store_reindex_elastic()
                return Response(
                    data=dict(status=True, data=serializer.data),
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    data=dict(status=False, data=None),
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            data=dict(status=False, data=serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )


class StoreServiceDetailView(AdminViewMixin):
    def get_object(self, pk):
        try:
            return StoreDetail.objects.get(store__pk=pk)
        except StoreDetail.DoesNotExist:
            # raise Http404
            return False

    @extend_schema(responses={200: StoreServiceDetailSerializer}, methods=["GET"])
    def get(self, request, pk):
        snippet = self.get_object(pk)
        if snippet:
            serializer = StoreServiceDetailSerializer(snippet)
            return Response(
                data=dict(status=True, data=serializer.data), status=status.HTTP_200_OK
            )
        return Response(
            data=dict(status=False, data={"msg": "Not Found"}),
            status=status.HTTP_404_NOT_FOUND,
        )


class StoreServieView(AdminViewMixin):
    def get(self, request, pk):
        try:
            store_obj = Store.objects.get(id=pk)
            if store_obj:
                store_detail_obj = StoreDetail.objects.get(store_id=store_obj.id)
                services = ServiceSerializer(
                    store_detail_obj.services.all(), many=True
                ).data
                return Response({"status": True, "services": services}, status=200)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=400)

    def put(self, request, pk):
        try:
            HEADERS = {
                "Authorization": f"{settings.STATIC_TOKEN}",
                "Content-Type": "application/json",
            }

            request_response = requests.post(
                f"{settings.EYEMYEYE_BASE_URL}/store/update_store_service/",
                data=json.dumps(request.data),
                headers=HEADERS,
            )

            if (
                request_response.status_code == 201
                and request_response.json()["success"]
            ):
                services = request.data.get("services")
                store_detail_obj = StoreDetail.objects.get(store_id=pk)
                store_services = store_detail_obj.services.all()
                if len(store_services) > 0:
                    store_detail_obj.services.clear()

                for service in Services.objects.filter(id__in=services):
                    store_detail_obj.services.add(service)
                return Response(
                    {"status": True, "message": "Store Services Updated Successfully"},
                    status=200,
                )

            return Response(
                {"status": False, "message": "Failed to Update Store Services"},
                status=500,
            )
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=400)
