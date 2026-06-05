import pytest
from io import BytesIO

from django.test import override_settings


FILE_KEY = "images/2026/06/06/test-upload.jpg"
UPLOAD_URL = f"/debug/upload/{FILE_KEY}"


def make_file(content=b"fake-image-data", name="photo.jpg"):
    f = BytesIO(content)
    f.name = name
    return f


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_upload_saves_file(api_client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path

    response = api_client.post(UPLOAD_URL, {"file": make_file()}, format="multipart")

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert (tmp_path / FILE_KEY).exists()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_upload_creates_parent_dirs(api_client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    nested_key = "videos/2026/06/06/deep/nested/clip.mp4"

    api_client.post(f"/debug/upload/{nested_key}", {"file": make_file()}, format="multipart")

    assert (tmp_path / nested_key).exists()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_upload_stores_correct_content(api_client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    content = b"binary-file-content-123"

    api_client.post(UPLOAD_URL, {"file": make_file(content=content)}, format="multipart")

    assert (tmp_path / FILE_KEY).read_bytes() == content


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_missing_file_returns_400(api_client):
    response = api_client.post(UPLOAD_URL, {}, format="multipart")

    assert response.status_code == 400
    assert response.json()["ok"] is False


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_not_allowed(api_client):
    response = api_client.get(UPLOAD_URL)

    assert response.status_code == 405
