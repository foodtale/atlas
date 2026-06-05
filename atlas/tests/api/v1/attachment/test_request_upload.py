import pytest
from unittest.mock import patch, PropertyMock

from django.utils import timezone

from atlas.models.attachment import Attachment
from atlas.models.choices import AttachmentAssetType

MOCK_UPLOAD_URL = "http://localhost:8000/debug/upload/images/2026/06/06/test.jpg"


@pytest.mark.django_db
def test_unauthenticated_returns_403(api_client):
    response = api_client.post(
        "/api/v1/attachments/request/upload",
        {"file_name": "photo.jpg", "mime_type": "image/jpeg"},
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
@patch.object(Attachment, "upload_url", new_callable=PropertyMock, return_value=MOCK_UPLOAD_URL)
def test_valid_image_returns_201(mock_upload_url, authenticated_client, user):
    response = authenticated_client.post(
        "/api/v1/attachments/request/upload",
        {"file_name": "photo.jpg", "mime_type": "image/jpeg"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["ok"] is True

    data = response.data["data"]
    assert "attachment_id" in data
    assert "upload_url" in data
    assert "file_key" in data
    assert data["file_key"].startswith("images/")
    assert data["file_key"].endswith(".jpg")


@pytest.mark.django_db
@patch.object(Attachment, "upload_url", new_callable=PropertyMock, return_value=MOCK_UPLOAD_URL)
def test_valid_video_returns_201(mock_upload_url, authenticated_client):
    response = authenticated_client.post(
        "/api/v1/attachments/request/upload",
        {"file_name": "clip.mp4", "mime_type": "video/mp4"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["data"]["file_key"].startswith("videos/")


@pytest.mark.django_db
def test_unsupported_mime_returns_422(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/attachments/request/upload",
        {"file_name": "doc.pdf", "mime_type": "application/pdf"},
        format="json",
    )

    assert response.status_code == 422
    assert response.data["ok"] is False


@pytest.mark.django_db
def test_missing_fields_returns_400(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/attachments/request/upload",
        {"mime_type": "image/jpeg"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
@patch.object(Attachment, "upload_url", new_callable=PropertyMock, return_value=MOCK_UPLOAD_URL)
def test_attachment_created_with_pending_expiry(mock_upload_url, authenticated_client, user):
    authenticated_client.post(
        "/api/v1/attachments/request/upload",
        {"file_name": "photo.jpg", "mime_type": "image/jpeg"},
        format="json",
    )

    attachment = Attachment.objects.filter(uploaded_by=user).first()
    assert attachment is not None
    assert attachment.expires_at is not None
    assert attachment.expires_at > timezone.now()


@pytest.mark.django_db
@patch.object(Attachment, "upload_url", new_callable=PropertyMock, return_value=MOCK_UPLOAD_URL)
def test_attachment_belongs_to_authenticated_user(mock_upload_url, authenticated_client, user):
    response = authenticated_client.post(
        "/api/v1/attachments/request/upload",
        {"file_name": "photo.png", "mime_type": "image/png"},
        format="json",
    )

    attachment_id = response.data["data"]["attachment_id"]
    attachment = Attachment.objects.get(id=attachment_id)

    assert attachment.uploaded_by == user
    assert attachment.asset_type == AttachmentAssetType.IMAGE
