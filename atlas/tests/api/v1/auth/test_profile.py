import pytest


@pytest.mark.django_db
def test_unauthenticated_user_gets_401(api_client):
    response = api_client.get("/api/v1/auth/profile")

    assert response.status_code == 403