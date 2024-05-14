from rest_framework.response import Response


def api_response(
    status: bool, status_code: int, message: str = None, data=None, **kwargs
):
    response_payload = {
        "status": status,
        "status_code": status_code,
    }

    if message:
        response_payload["message"] = message

    if data:
        response_payload["data"] = data
    response_payload.update(kwargs)

    print(response_payload)

    return Response(response_payload, status_code)
