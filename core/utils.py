from rest_framework.response import Response
from django.http import Http404


def api_response(status: bool, status_code: int, message: str = None, **kwargs):
    response_payload = {
        "status": status,
        "status_code": status_code,
    }

    if message:
        response_payload["message"] = message

    response_payload.update(kwargs)

    return Response(response_payload, status_code)


class custom_404(Http404):
    def __init__(self, message=""):
        if not message:
            message = "Custom Not Found Message"
        super().__init__(message)
