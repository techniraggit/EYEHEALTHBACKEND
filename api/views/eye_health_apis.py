from .base import UserMixin
import requests

BASE_URL = "https://mobile.testing.backend.zuktiinnovations.com"

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
}


def add_customer(data):
    response = requests.post(END_POINTS.get("add_customer"), data=data)
    return response.json()


def get_question_details():
    response = requests.get(END_POINTS.get("get_question_details"))
    return response.json()


def select_question(data):
    response = requests.post(END_POINTS.get("select_question"), data=data)
    return response.json()


def select_eye(data):
    response = requests.post(END_POINTS.get("select_eye"), data=data)
    return response.json()


def get_snellen_fraction(params):
    # ?test_name=hyperopia
    response = requests.get(END_POINTS.get("get_snellen_fraction"), params=params)
    return response.json()


def random_text(data):
    response = requests.post(END_POINTS.get("random_text"), data=data)
    return response.json()


def myopia_or_hyperopia_or_presbyopia_test(data):
    response = requests.put(
        END_POINTS.get("myopia_or_hyperopia_or_presbyopia_test"), data=data
    )
    return response.json()


def choose_astigmatism(data):
    response = requests.put(END_POINTS.get("choose_astigmatism"), data=data)
    return response.json()


def get_degrees(params):
    # ?test_id={{eye_test_test_id}}
    response = requests.get(END_POINTS.get("get_degrees"), params=params)
    return response.json()


def choose_degree_api(data):
    response = requests.put(END_POINTS.get("choose_degree_api"), data=data)
    return response.json()


def cyl_test(data):
    response = requests.put(END_POINTS.get("cyl_test"), data=data)
    return response.json()


def get_snellen_fraction_red_green_test(params):
    # ?test_id={{eye_test_test_id}}
    response = requests.get(
        END_POINTS.get("get_snellen_fraction_red_green_test"), params=params
    )
    return response.json()


def final_red_green_action_test(data):
    response = requests.post(END_POINTS.get("final_red_green_action_test"), data=data)
    return response.json()


def update_red_green_action_api(data):
    response = requests.put(END_POINTS.get("update_red_green_action_api"), data=data)
    return response.json()


def random_word_test(data):
    response = requests.post(END_POINTS.get("random_word_test"), data=data)
    return response.json()


def update_Reading_SnellenFraction_TestApi(data):
    response = requests.put(
        END_POINTS.get("update_Reading_SnellenFraction_TestApi"), data=data
    )
    return response.json()


def get_generated_report(params):
    # ?test_id={{eye_test_test_id}}
    response = requests.get(END_POINTS.get("get_generated_report"), params=params)
    return response.json()


class AddCustomer(UserMixin):
    def post(self, request):
        return add_customer(request.data)


class GetQuestionDetails(UserMixin):
    def get(self, request):
        return get_question_details()


class SelectQuestion(UserMixin):
    def post(self, request):
        return select_question(request.data)


class SelectEye(UserMixin):
    def post(self, request):
        return select_eye(request.data)


class GetSnellenFraction(UserMixin):
    def get(self, request):
        return get_snellen_fraction(request.GET)


class RandomText(UserMixin):
    def post(self, request):
        return random_text(request.data)


class MyopiaOrHyperopiaOrPresbyopiaTest(UserMixin):
    def put(self, request):
        return myopia_or_hyperopia_or_presbyopia_test(request.data)


class ChooseAstigmatism(UserMixin):
    def put(self, request):
        return choose_astigmatism(request.data)


class GetDegrees(UserMixin):
    def get(self, request):
        return get_degrees(request.GET)


class ChooseDegreeApi(UserMixin):
    def put(self, request):
        return choose_degree_api(request.data)


class CylTest(UserMixin):
    def put(self, request):
        return cyl_test(request.data)


class GetSnellenFractionRedGreenTest(UserMixin):
    def get(self, request):
        return get_snellen_fraction_red_green_test(request.GET)


class FinalRedGreenActionTest(UserMixin):
    def post(self, request):
        return final_red_green_action_test(request.data)


class UpdateRedGreenActionApi(UserMixin):
    def put(self, request):
        return update_red_green_action_api(request.data)


class RandomWordTest(UserMixin):
    def post(self, request):
        return random_word_test(request.data)


class UpdateReadingSnellenFractionTestApi(UserMixin):
    def put(self, request):
        return update_Reading_SnellenFraction_TestApi(request.data)


class GetGeneratedReport(UserMixin):
    def get(self, request):
        return get_generated_report(request.GET)
