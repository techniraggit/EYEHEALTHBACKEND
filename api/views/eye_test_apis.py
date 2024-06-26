from django.shortcuts import get_object_or_404
from utilities.utils import generate_pdf
from core.utils import api_response
from api.models.eye_health import UserTestProfile, EyeTestReport
from core.utils import custom_404
from utilities.utils import base64_encode
from api.serializers.eye_health import (
    UserTestProfileSerializer,
    EyeTestReportSerializer,
)
from utilities.redis_client import store_token, get_token
from .base import UserMixin, SecureHeadersMixin
import requests
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings

BASE_URL = settings.EYE_TEST_BASE_API_URL
from core.logs import Logger

logger = Logger("eye_test.logs")

END_POINTS = {
    "add_customer": f"{BASE_URL}/add-customer/",
    "get_question_details": f"{BASE_URL}/get-question-details/",
    "select_question": f"{BASE_URL}/select-questions/",
    "select_eye": f"{BASE_URL}/select-eye/",
    "get_snellen_fraction": f"{BASE_URL}/snellen-fraction/",
    "random_text": f"{BASE_URL}/random-text/",
    "myopia_or_hyperopia_or_presbyopia_test": f"{BASE_URL}/myopia-or-hyperopia-or-presbyopia-test/",
    "choose_astigmatism": f"{BASE_URL}/choose-astigmatism/",
    "get_degrees": f"{BASE_URL}/get-degrees/",
    "choose_degree_api": f"{BASE_URL}/choose-degree-api/",
    "cyl_test": f"{BASE_URL}/cyl-test/",
    "get_snellen_fraction_red_green_test": f"{BASE_URL}/snellen-fraction-red-green-test/",
    "final_red_green_action_test": f"{BASE_URL}/final-red-green-action-test/",
    "update_red_green_action_api": f"{BASE_URL}/update-red-green-action-api/",
    "random_word_test": f"{BASE_URL}/random-word-test/",
    "update_Reading_SnellenFraction_TestApi": f"{BASE_URL}/update-Reading-SnellenFraction-TestApi/",
    "get_generated_report": f"{BASE_URL}/genrate-report/",
    "calculate_distance": f"{BASE_URL}/calculate-distance/",
    "get_eye_access_token": f"{BASE_URL}/get-eye-access-token/",
    "counter_api": f"{BASE_URL}/counter-api/",
    "reading_snellen_fraction": f"{BASE_URL}/reading-snellen-fraction/",
    "random_word_Reading_test": f"{BASE_URL}/random-word-Reading-test/",
}


def get_eye_access_token(user_id):
    response = requests.get(
        END_POINTS.get("get_eye_access_token"), params={"user_id": user_id}
    )
    try:
        response.json()
        return response
    except:
        return HttpResponse(response)


def get_user_token(user_id):
    access_token = get_token(user_id=user_id)
    if not access_token:
        response = get_eye_access_token(user_id)
        access_token = response.json()["access_token"]
        store_token(user_id=user_id, token=access_token)
    return access_token


def add_customer(data):
    response = requests.post(END_POINTS.get("add_customer"), json=data)
    return response


def get_question_details(customer_id):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.get(END_POINTS.get("get_question_details"), headers=headers)
    return response


def select_question(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.post(
        END_POINTS.get("select_question"), json=data, headers=headers
    )
    return response


def select_eye(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.post(END_POINTS.get("select_eye"), json=data, headers=headers)
    return response


def get_snellen_fraction(params):
    # ?test_name=hyperopia
    headers = {"Authorization": settings.SNELLEN_FRACTION_STATIC_TOKEN}
    response = requests.get(
        END_POINTS.get("get_snellen_fraction"), params=params, headers=headers
    )
    return response


def random_text(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.post(END_POINTS.get("random_text"), json=data, headers=headers)
    return response


def myopia_or_hyperopia_or_presbyopia_test(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.put(
        END_POINTS.get("myopia_or_hyperopia_or_presbyopia_test"),
        json=data,
        headers=headers,
    )
    return response


def choose_astigmatism(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.put(
        END_POINTS.get("choose_astigmatism"), json=data, headers=headers
    )
    return response


def get_degrees(customer_id, params):
    # ?test_id={{eye_test_test_id}}
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.get(
        END_POINTS.get("get_degrees"), params=params, headers=headers
    )
    return response


def choose_degree_api(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.put(
        END_POINTS.get("choose_degree_api"), json=data, headers=headers
    )
    return response


def cyl_test(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.put(END_POINTS.get("cyl_test"), json=data, headers=headers)
    return response


def get_snellen_fraction_red_green_test(customer_id, params):
    # ?test_id={{eye_test_test_id}}
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.get(
        END_POINTS.get("get_snellen_fraction_red_green_test"),
        params=params,
        headers=headers,
    )
    return response


def final_red_green_action_test(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.post(
        END_POINTS.get("final_red_green_action_test"), json=data, headers=headers
    )
    return response


def update_red_green_action_api(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.put(
        END_POINTS.get("update_red_green_action_api"), json=data, headers=headers
    )
    return response


def random_word_test(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.post(
        END_POINTS.get("random_word_test"), json=data, headers=headers
    )
    return response


def update_Reading_SnellenFraction_TestApi(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.put(
        END_POINTS.get("update_Reading_SnellenFraction_TestApi"),
        json=data,
        headers=headers,
    )
    return response


def get_generated_report(customer_id, params):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    # ?test_id={{eye_test_test_id}}
    response = requests.get(
        END_POINTS.get("get_generated_report"), params=params, headers=headers
    )
    return response


def calculate_distance(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    data["source_type"] = "app"
    response = requests.post(
        END_POINTS.get("calculate_distance"), json=data, headers=headers
    )
    return response


def counter_api(params):
    headers = {"Authorization": settings.SNELLEN_FRACTION_STATIC_TOKEN}
    response = requests.get(
        END_POINTS.get("counter_api"), params=params, headers=headers
    )
    return response

def reading_snellen_fraction(customer_id, params):
    token =  get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.get(
        END_POINTS.get("reading_snellen_fraction"), params=params, headers=headers
    )
    return response

def random_word_Reading_test(customer_id, data):
    token = get_user_token(customer_id)
    headers = dict(Authorization=f"Bearer {token}")
    response = requests.post(
        END_POINTS.get("random_word_Reading_test"), json=data, headers=headers
    )
    return response


class CustomerView(UserMixin):
    def get_object(self, pk):
        try:
            return UserTestProfile.objects.get(pk=pk)
        except UserTestProfile.DoesNotExist:
            raise custom_404("Profile does not exist.")

    def get(self, request):
        query_set = UserTestProfile.objects.filter(user=request.user)
        serialized_data = UserTestProfileSerializer(
            query_set, many=True, fields=["id", "full_name", "customer_id", "age"]
        ).data
        return Response(serialized_data, 200)

    def post(self, request):
        # try:
        #     data = dict(
        #         email=request_user.email,
        #         name=request_user.get_full_name(),
        #         domain_url=settings.EYE_TEST_DOMAIN_URL,
        #         age=request_user.age(),
        #         mobile_no=request_user.phone_number,
        #     )
        #     response = add_customer(data)
        #     return Response(response.json(), response.status_code)
        # except Exception:
        #     return HttpResponse(response)

        request_user = request.user
        is_self = request.data.get("is_self", False)
        if is_self:
            data = dict(
                email=request_user.email,
                name=request_user.get_full_name(),
                domain_url=settings.EYE_TEST_DOMAIN_URL,
                age=request_user.age(),
                mobile_no=request_user.phone_number,
            )
        else:
            full_name = request.data.get("name")
            age = request.data.get("age")
            if not full_name or not age:
                return Response(
                    {"status": False, "message": "Name and age must be specified"}
                )

            data = dict(
                email=request_user.email,
                name=full_name,
                domain_url=settings.EYE_TEST_DOMAIN_URL,
                age=age,
                mobile_no=request_user.phone_number,
            )

        try:

            profile_obj, created = UserTestProfile.objects.get_or_create(
                user=request.user,
                full_name=data.get("name"),
                age=data.get("age"),
            )

            if created:
                try:
                    response = add_customer(data)
                    if response.status_code != 200:
                        profile_obj.delete()
                        return Response(response, response.status_code)
                except:
                    return Response(response, response.status_code)

                profile_obj.customer_id = base64_encode(response.json()["data"]["id"])
                profile_obj.save()

            access_token = get_user_token(profile_obj.customer_id)
            data = profile_obj.to_json()
            data["message"] = "Profile found successfully. You may start your eye test."
            data["status_code"] = 200
            # data["access_token"] = access_token
            return Response(data, 200)
        except Exception:
            # raise Exception
            return HttpResponse(response)


class AccessTokenView(UserMixin):
    def get(self, request):
        response = get_eye_access_token(request.GET.get("user_id"))
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetQuestionDetails(SecureHeadersMixin):
    def get(self, request):
        customer_id = request.headers.get("Customer-Id")
        response = get_question_details(customer_id)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class SelectQuestion(SecureHeadersMixin):
    def post(self, request):
        response = select_question(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class SelectEye(UserMixin):
    def post(self, request):
        response = select_eye(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetSnellenFraction(UserMixin):
    def get(self, request):
        response = get_snellen_fraction(request.GET)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class RandomText(UserMixin):
    def post(self, request):
        response = random_text(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class MyopiaOrHyperopiaOrPresbyopiaTest(UserMixin):
    def put(self, request):
        response = myopia_or_hyperopia_or_presbyopia_test(
            request.headers.get("Customer-Id"), request.data
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class ChooseAstigmatism(UserMixin):
    def put(self, request):
        response = choose_astigmatism(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetDegrees(UserMixin):
    def get(self, request):
        response = get_degrees(request.headers.get("Customer-Id"), request.GET)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class ChooseDegreeApi(UserMixin):
    def put(self, request):
        response = choose_degree_api(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class CylTest(UserMixin):
    def put(self, request):
        response = cyl_test(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetSnellenFractionRedGreenTest(UserMixin):
    def get(self, request):
        response = get_snellen_fraction_red_green_test(
            request.headers.get("Customer-Id"), request.GET
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class FinalRedGreenActionTest(UserMixin):
    def post(self, request):
        response = final_red_green_action_test(
            request.headers.get("Customer-Id"), request.data
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class UpdateRedGreenActionApi(UserMixin):
    def put(self, request):
        response = update_red_green_action_api(
            request.headers.get("Customer-Id"), request.data
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class RandomWordTest(UserMixin):
    def post(self, request):
        response = random_word_test(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class UpdateReadingSnellenFractionTestApi(UserMixin):
    def put(self, request):
        response = update_Reading_SnellenFraction_TestApi(
            request.headers.get("Customer-Id"), request.data
        )
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


from api.models.rewards import GlobalPointsModel
from api.models.accounts import UserPoints


class GetGeneratedReport(UserMixin):
    def get(self, request):
        customer_id = request.headers.get("Customer-Id")
        report_id = request.GET.get("test_id")
        response = get_generated_report(customer_id, request.GET)

        try:
            user_profile_obj = UserTestProfile.objects.get(customer_id=customer_id)
        except:
            return api_response(False, 404, "User profile not found")

        try:
            json_response = response.json()
            try:
                data = dict(
                    report_id=report_id,
                    user_profile=user_profile_obj,
                    right_eye=json_response["data"]["test"][1],
                    left_eye=json_response["data"]["test"][0],
                    health_score=json_response["data"]["health_score"],
                )

                try:
                    points = GlobalPointsModel.objects.get(event_type="eye_test").value
                    usr_pnt = UserPoints.objects.create(
                        user=user_profile_obj.user,
                        event_type="eye_test",
                    )
                    usr_pnt.increase_points(points)
                    usr_pnt.save()
                except Exception as e:
                    logger.error(str(e))

                try:
                    data = EyeTestReport.objects.create(**data)
                    return api_response(
                        True,
                        200,
                        "Eye Test Report saved successfully",
                        data=data.to_json(),
                    )
                except Exception as e:
                    return api_response(
                        False, 500, "Something went wrong", error=str(e)
                    )
            except:
                return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class CalculateDistance(UserMixin):
    def post(self, request):
        response = calculate_distance(request.headers.get("Customer-Id"), request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class EyeTestReports(UserMixin):
    def get(self, request):
        report_id = request.GET.get("report_id")
        if report_id:
            try:
                data = EyeTestReport.objects.get(report_id=report_id)
                serialized_data = EyeTestReportSerializer(data).data
                return api_response(True, 200, data=serialized_data)
            except EyeTestReport.DoesNotExist:
                return api_response(False, 404, "Report not found")
            except Exception as e:
                return api_response(False, 500, "Error processing report")
        data = EyeTestReport.objects.filter(user_profile__user=request.user).order_by("-created_on")
        serialized_data = EyeTestReportSerializer(data, many=True).data
        return api_response(True, 200, data=serialized_data)


class DownloadReportView(UserMixin):
    def get(self, request):
        report_id = request.GET.get("report_id")
        if not report_id:
            return api_response(False, 400, message="Report ID is required")

        try:
            report = get_object_or_404(EyeTestReport, report_id=report_id)

            buffer = generate_pdf("reports/eye_test_report.html", report.report())
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="prescription_{report_id}.pdf"'
            )
            return response

        except EyeTestReport.DoesNotExist:
            return api_response(False, 404, message="Report not found")


class CounterApiView(UserMixin):
    def get(self, request):
        params = request.GET
        response = counter_api(params)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)

class ReadingSnellenFractionView(UserMixin):
    def get(self, request):
        params = request.GET
        customer_id = request.headers.get("Customer-Id")
        response = reading_snellen_fraction(customer_id, params)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)

class RandomWordReadingTestView(UserMixin):
    def post(self, request):
        data = request.data
        customer_id = request.headers.get("Customer-Id")
        response = random_word_Reading_test(customer_id, data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)