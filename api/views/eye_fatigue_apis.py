from .base import UserMixin
import requests
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings

BASE_URL = "https://mobile.testing-f-meter-backend.zuktiinnovations.com"


END_POINTS = {
    "add_customer": f"{BASE_URL}/add-customer/",
    "calculate_blink_rate": f"{BASE_URL}/calculate-blink-rate/",
    "blinks_report_details": f"{BASE_URL}/blinks-report-details/",
}

secure_headers = dict(Authorization=f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MzgwMTUwLCJpYXQiOjE3MTYzNzY1NTAsImp0aSI6ImFjM2NiM2FhZTM1MjRjOTY5YjRhNjViMmI5ZGE1YWYyIiwidXNlcl9pZCI6MTF9.bpTrL6ZBML5GgGP3aOY2OUl8ip75wJyjidK_KYIIC5A")


def add_customer(data):
    response = requests.post(END_POINTS.get("add_customer"), json=data)
    return response

def calculate_blink_rate(video):
    response = requests.post(END_POINTS.get("calculate_blink_rate"), files=video, headers=secure_headers)
    return response

def blinks_report_details(data):
    response = requests.get(END_POINTS.get("blinks_report_details"), params=data, headers=secure_headers)
    return response

class AddCustomer(UserMixin):
    def post(self, request):
        request_user = request.user
        data = dict(
            email=request_user.email,
            name=request_user.get_full_name(),
            domain_url=settings.EYE_TEST_DOMAIN_URL,
            age=request_user.age(),
            mobile_no=request_user.phone_number,
        )
        response = add_customer(data)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)


class CalculateBlinkRate(UserMixin):
    def post(self, request):
        response = calculate_blink_rate(request.FILES)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)

class BlinkReportDetails(UserMixin):
    def get(self, request):
        response = blinks_report_details(request.GET)
        try:
            return Response(response.json(), response.status_code)
        except:
            return HttpResponse(response)