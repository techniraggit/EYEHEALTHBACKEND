from .base import UserMixin
import requests
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings

BASE_URL = settings.EYE_TEST_BASE_API_URL

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
}

from utilities.redis_client import SessionManager


def get_eye_access_token(user_id):
    print("user_id == ", user_id)
    response = requests.get(END_POINTS.get("get_eye_access_token"), params={'user_id': user_id})
    try:
        response.json()
        return response
    except:
        return HttpResponse(response)

def get_user_token(user_id):
    session_manager = SessionManager()
    access_token = session_manager.get_session_token(user_id=user_id)
    if not access_token:
        response = get_eye_access_token(user_id)
        print("Access token=============================befoer")
        access_token  = response.json()
        print("access_token === ", access_token, "********************")
        session_manager.store_session_token(user_id=user_id, session_token=access_token)
    return access_token

secure_headers = dict(Authorization=f"Bearer {settings.STATIC_TOKEN}")

def add_customer(data):
    response = requests.post(END_POINTS.get("add_customer"), json=data)
    return response


def get_question_details():
    response = requests.get(
        END_POINTS.get("get_question_details"), headers=secure_headers
    )
    return response


def select_question(data):
    response = requests.post(
        END_POINTS.get("select_question"), json=data, headers=secure_headers
    )
    return response


def select_eye(data):
    response = requests.post(
        END_POINTS.get("select_eye"), json=data, headers=secure_headers
    )
    return response


def get_snellen_fraction(params):
    # ?test_name=hyperopia
    headers = {"Authorization": settings.SNELLEN_FRACTION_STATIC_TOKEN}
    response = requests.get(
        END_POINTS.get("get_snellen_fraction"), params=params, headers=headers
    )
    return response


def random_text(data):
    response = requests.post(
        END_POINTS.get("random_text"), json=data, headers=secure_headers
    )
    return response


def myopia_or_hyperopia_or_presbyopia_test(data):
    response = requests.put(
        END_POINTS.get("myopia_or_hyperopia_or_presbyopia_test"),
        json=data,
        headers=secure_headers,
    )
    return response


def choose_astigmatism(data):
    response = requests.put(
        END_POINTS.get("choose_astigmatism"), json=data, headers=secure_headers
    )
    return response


def get_degrees(params):
    # ?test_id={{eye_test_test_id}}
    response = requests.get(
        END_POINTS.get("get_degrees"), params=params, headers=secure_headers
    )
    return response


def choose_degree_api(data):
    response = requests.put(
        END_POINTS.get("choose_degree_api"), json=data, headers=secure_headers
    )
    return response


def cyl_test(data):
    response = requests.put(
        END_POINTS.get("cyl_test"), json=data, headers=secure_headers
    )
    return response


def get_snellen_fraction_red_green_test(params):
    # ?test_id={{eye_test_test_id}}
    response = requests.get(
        END_POINTS.get("get_snellen_fraction_red_green_test"),
        params=params,
        headers=secure_headers,
    )
    return response


def final_red_green_action_test(data):
    response = requests.post(
        END_POINTS.get("final_red_green_action_test"), json=data, headers=secure_headers
    )
    return response


def update_red_green_action_api(data):
    response = requests.put(
        END_POINTS.get("update_red_green_action_api"), json=data, headers=secure_headers
    )
    return (response,)


def random_word_test(data):
    response = requests.post(
        END_POINTS.get("random_word_test"), json=data, headers=secure_headers
    )
    return response


def update_Reading_SnellenFraction_TestApi(data):
    response = requests.put(
        END_POINTS.get("update_Reading_SnellenFraction_TestApi"),
        json=data,
        headers=secure_headers,
    )
    return response


def get_generated_report(params):
    # ?test_id={{eye_test_test_id}}
    response = requests.get(
        END_POINTS.get("get_generated_report"), params=params, headers=secure_headers
    )
    return response


def calculate_distance(data):
    response = requests.post(
        END_POINTS.get("calculate_distance"), json=data, headers=secure_headers
    )
    return response

from api.models.eye_health import UserTestProfile
from api.serializers.eye_health import UserTestProfileSerializer
from utilities.utils import base64_encode
from core.utils import custom_404

class CustomerView(UserMixin):
    def get_object(self, pk):
        try:
            return UserTestProfile.objects.get(pk=pk)
        except UserTestProfile.DoesNotExist:
            raise custom_404("Profile does not exist.")

    def get(self, request):
        query_set = UserTestProfile.objects.filter(user=request.user)
        serialized_data = UserTestProfileSerializer(query_set, many=True).data
        return Response(serialized_data, 200)

    def post(self, request):
        request_user = request.user


        try:
            data = dict(
                email=request_user.email,
                name=request_user.get_full_name(),
                domain_url=settings.EYE_TEST_DOMAIN_URL,
                age=request_user.age(),
                mobile_no=request_user.phone_number,
            )
            response = add_customer(data)
            return Response(response.json(), response.status_code)
        except Exception:
            return HttpResponse(response)


        is_self = request.data.get('is_self', False)
        if is_self:
            data = dict(
                email=request_user.email,
                name=request_user.get_full_name(),
                domain_url=settings.EYE_TEST_DOMAIN_URL,
                age=request_user.age(),
                mobile_no=request_user.phone_number,
            )
        else:
            full_name = request.data.get('name')
            age = request.data.get('age')
            if not full_name or not age:
                return Response({"status":False, "message":"Name and age must be specified"})

            data = dict(
                email=request_user.email,
                name=full_name,
                domain_url=settings.EYE_TEST_DOMAIN_URL,
                age=age,
                mobile_no=request.data.get('mobile_no'),
            )
        
        try:
            
            profile_obj, created = UserTestProfile.objects.get_or_create(
                user = request.user,
                full_name = data.get('name'),
                age = data.get('age'),
                
            )

            if created:
                try:
                    response = add_customer(data)
                    json_response = response.json()
                    if response.status_code != 200:
                        return Response(response, response.status_code)
                    print("json_response === ", json_response)
                except:
                    return Response(response, response.status_code)
                profile_obj.customer_id =  base64_encode(json_response["data"]["id"])
                profile_obj.save()

            print("profile_obj.customer_id == ", profile_obj.customer_id)

            access_token = get_user_token(profile_obj.customer_id)
            data = profile_obj.to_json()
            data["access_token"] = access_token
            return Response(data)
        except Exception as e:
            raise e
            return HttpResponse(response)

class AccessTokenView(UserMixin):
    def get(self, request):
        response = get_eye_access_token(request.GET.get("user_id"))
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)

class GetQuestionDetails(UserMixin):
    def get(self, request):
        response = get_question_details()
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class SelectQuestion(UserMixin):
    def post(self, request):
        response = select_question(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class SelectEye(UserMixin):
    def post(self, request):
        response = select_eye(request.data)
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
        response = random_text(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class MyopiaOrHyperopiaOrPresbyopiaTest(UserMixin):
    def put(self, request):
        response = myopia_or_hyperopia_or_presbyopia_test(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class ChooseAstigmatism(UserMixin):
    def put(self, request):
        response = choose_astigmatism(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetDegrees(UserMixin):
    def get(self, request):
        response = get_degrees(request.GET)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class ChooseDegreeApi(UserMixin):
    def put(self, request):
        response = choose_degree_api(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class CylTest(UserMixin):
    def put(self, request):
        response = cyl_test(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetSnellenFractionRedGreenTest(UserMixin):
    def get(self, request):
        response = get_snellen_fraction_red_green_test(request.GET)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class FinalRedGreenActionTest(UserMixin):
    def post(self, request):
        response = final_red_green_action_test(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class UpdateRedGreenActionApi(UserMixin):
    def put(self, request):
        response = update_red_green_action_api(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class RandomWordTest(UserMixin):
    def post(self, request):
        response = random_word_test(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class UpdateReadingSnellenFractionTestApi(UserMixin):
    def put(self, request):
        response = update_Reading_SnellenFraction_TestApi(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class GetGeneratedReport(UserMixin):
    def get(self, request):
        response = get_generated_report(request.GET)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class CalculateDistance(UserMixin):
    def post(self, request):
        response = calculate_distance(request.data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)
