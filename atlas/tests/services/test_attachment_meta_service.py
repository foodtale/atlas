import pytest
from datetime import date

from atlas.models.choices import AttachmentAssetType
from atlas.services.attachment_meta_service import AttachmentMetaService


# --- resolve_asset_type ---

@pytest.mark.parametrize("mime_type", [
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml", "image/avif",
])
def test_resolve_image_types(mime_type):
    assert AttachmentMetaService.resolve_asset_type(mime_type) == AttachmentAssetType.IMAGE


@pytest.mark.parametrize("mime_type", [
    "video/mp4", "video/webm", "video/quicktime", "video/x-msvideo", "video/x-matroska",
])
def test_resolve_video_types(mime_type):
    assert AttachmentMetaService.resolve_asset_type(mime_type) == AttachmentAssetType.VIDEO


def test_resolve_unsupported_raises_value_error():
    with pytest.raises(ValueError):
        AttachmentMetaService.resolve_asset_type("application/pdf")


def test_resolve_is_case_insensitive():
    assert AttachmentMetaService.resolve_asset_type("IMAGE/JPEG") == AttachmentAssetType.IMAGE


# --- generate_file_key ---

def test_file_key_starts_with_asset_type_prefix():
    key = AttachmentMetaService.generate_file_key("image/jpeg", "photo.jpg")

    assert key.startswith("images/")


def test_file_key_video_prefix():
    key = AttachmentMetaService.generate_file_key("video/mp4", "clip.mp4")

    assert key.startswith("videos/")


def test_file_key_contains_today_date():
    today = date.today()
    key = AttachmentMetaService.generate_file_key("image/png", "photo.png")
    date_segment = f"{today.year}/{today.month:02d}/{today.day:02d}"

    assert date_segment in key


def test_file_key_preserves_extension():
    key = AttachmentMetaService.generate_file_key("image/jpeg", "photo.jpg")

    assert key.endswith(".jpg")


def test_file_key_extension_lowercased():
    key = AttachmentMetaService.generate_file_key("image/jpeg", "photo.JPG")

    assert key.endswith(".jpg")


def test_file_key_no_extension_when_filename_has_none():
    key = AttachmentMetaService.generate_file_key("image/jpeg", "photowithoutext")

    assert "." not in key.split("/")[-1]


def test_file_key_is_unique():
    key1 = AttachmentMetaService.generate_file_key("image/jpeg", "photo.jpg")
    key2 = AttachmentMetaService.generate_file_key("image/jpeg", "photo.jpg")

    assert key1 != key2


# --- .call() ---

def test_call_returns_asset_type_and_file_key():
    result, error = AttachmentMetaService.call(mime_type="image/jpeg", file_name="photo.jpg")

    assert error is None
    assert result["asset_type"] == AttachmentAssetType.IMAGE
    assert "file_key" in result


def test_call_unsupported_mime_returns_error():
    result, error = AttachmentMetaService.call(mime_type="application/pdf", file_name="doc.pdf")

    assert result is None
    assert error is not None
    assert error.message == "This file format is not supported."
    assert "mime_type" in error.payload
