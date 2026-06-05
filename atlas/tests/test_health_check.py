import pytest

from atlas.settings import ATLAS_VERSION


@pytest.mark.django_db
def test_returns_200(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200


@pytest.mark.django_db
def test_response_shape(api_client):
    response = api_client.get("/health")

    assert response.json()["ok"] is True
    assert response.json()["version"] == ATLAS_VERSION


@pytest.mark.django_db
def test_post_not_allowed(api_client):
    response = api_client.post("/health")

    assert response.status_code == 405
