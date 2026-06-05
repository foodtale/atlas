import pytest

from atlas.models.user import User


@pytest.mark.django_db
def test_creates_user_and_otp_request(api_client):
    response = api_client.post(
        "/api/v1/auth/otp/request",
        {
            "phone_number": "9999999999",
        },
        format="json",
    )

    assert response.status_code == 200

    assert User.objects.filter(phone_number="9999999999").exists()

    assert response.data["ok"] is True
    assert "otp_request_id" in response.data["data"]


@pytest.mark.django_db
def test_existing_user_can_request_otp(api_client):
    User.objects.create(phone_number="9999999999")

    response = api_client.post(
        "/api/v1/auth/otp/request",
        {
            "phone_number": "9999999999",
        },
        format="json",
    )

    assert response.status_code == 200