from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler

from atlas.response import APIResponse


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Unexpected exception
    if response is None:
        return APIResponse(
            ok=False,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error.",
            payload={
                "code": "INTERNAL_SERVER_ERROR",
            },
        )

    # Validation errors
    if isinstance(exc, ValidationError):
        return APIResponse(
            ok=False,
            status=response.status_code,
            message="Validation failed.",
            payload={
                "code": "VALIDATION_ERROR",
                "fields": response.data,
            },
        )

    detail = response.data.get("detail")

    # Custom structured detail
    if isinstance(detail, dict):
        return APIResponse(
            ok=False,
            status=response.status_code,
            message=detail.get("message"),
            payload={key: value for key, value in detail.items() if key != "message"},
        )

    # Plain DRF exceptions
    return APIResponse(
        ok=False,
        status=response.status_code,
        message=str(detail),
        payload={
            "code": "API_ERROR",
        },
    )
