import pytest
from rest_framework.test import APIClient

from atlas.models.user import User, UserSession


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create(phone_number="9999999999")


@pytest.fixture
def authenticated_client(user):
    session = UserSession.objects.create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {session.session_token}")
    return client
