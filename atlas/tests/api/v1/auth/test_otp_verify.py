import pytest
from unittest.mock import patch

from atlas.models.otp_request import OTPRequest
from atlas.models.user import User
from atlas.models.choices import OTPPurpose, OTPTarget


@pytest.mark.django_db
def test_invalid_request_id_returns_400(api_client):
    response = api_client.post(
        "/api/v1/auth/otp/verify",
        {
            "phone_number": "9999999999",
            "otp_request_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
            "otp": "123456",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
@patch.object(
    OTPRequest,
    "verify_otp",
    return_value=(True, None),
)
def test_valid_otp_creates_session(
    mock_verify,
    api_client,
):
    user = User.objects.create(phone_number="9999999999")

    otp_request, _ = OTPRequest.create_otp(
        user=user,
        purpose=OTPPurpose.LOGIN,
        target=OTPTarget.PHONE,
    )

    response = api_client.post(
        "/api/v1/auth/otp/verify",
        {
            "phone_number": user.phone_number,
            "otp_request_id": str(otp_request.id),
            "otp": "123456",
        },
        format="json",
    )

    assert response.status_code == 200

    assert response.data["ok"] is True
    assert "session_token" in response.data["data"]