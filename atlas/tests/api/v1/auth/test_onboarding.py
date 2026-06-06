import pytest

from atlas.models.user import User


@pytest.mark.django_db
def test_unauthenticated_returns_403(api_client):
    response = api_client.patch("/api/v1/auth/onboarding", {}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_updates_full_name(authenticated_client, user):
    response = authenticated_client.patch(
        "/api/v1/auth/onboarding",
        {"full_name": "Santosh Patro"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["ok"] is True
    assert response.data["data"]["full_name"] == "Santosh Patro"

    user.refresh_from_db()
    assert user.full_name == "Santosh Patro"
    assert user.is_onboarded is True


@pytest.mark.django_db
def test_updates_full_name_and_email(authenticated_client, user):
    response = authenticated_client.patch(
        "/api/v1/auth/onboarding",
        {"full_name": "Santosh Patro", "email_address": "santosh@example.com"},
        format="json",
    )

    assert response.status_code == 200

    user.refresh_from_db()
    assert user.full_name == "Santosh Patro"
    assert user.email_address == "santosh@example.com"


@pytest.mark.django_db
def test_empty_email_stored_as_null(authenticated_client, user):
    response = authenticated_client.patch(
        "/api/v1/auth/onboarding",
        {"full_name": "Santosh Patro", "email_address": ""},
        format="json",
    )

    assert response.status_code == 200

    user.refresh_from_db()
    assert user.email_address is None


@pytest.mark.django_db
def test_missing_full_name_returns_400(authenticated_client):
    response = authenticated_client.patch(
        "/api/v1/auth/onboarding",
        {},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_invalid_email_returns_400(authenticated_client):
    response = authenticated_client.patch(
        "/api/v1/auth/onboarding",
        {"full_name": "Santosh Patro", "email_address": "not-an-email"},
        format="json",
    )

    assert response.status_code == 400
