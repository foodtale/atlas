import uuid
from datetime import date

from atlas.models.choices import AttachmentAssetType
from atlas.services.base import BaseService

_MIME_TO_ASSET_TYPE = {
    "image/jpeg": AttachmentAssetType.IMAGE,
    "image/png": AttachmentAssetType.IMAGE,
    "image/gif": AttachmentAssetType.IMAGE,
    "image/webp": AttachmentAssetType.IMAGE,
    "image/svg+xml": AttachmentAssetType.IMAGE,
    "image/avif": AttachmentAssetType.IMAGE,
    "video/mp4": AttachmentAssetType.VIDEO,
    "video/webm": AttachmentAssetType.VIDEO,
    "video/quicktime": AttachmentAssetType.VIDEO,
    "video/x-msvideo": AttachmentAssetType.VIDEO,
    "video/x-matroska": AttachmentAssetType.VIDEO,
}


class AttachmentMetaService(BaseService):
    @staticmethod
    def resolve_asset_type(mime_type: str) -> AttachmentAssetType:
        asset_type = _MIME_TO_ASSET_TYPE.get(mime_type.lower())
        if asset_type is None:
            raise ValueError(mime_type)
        return asset_type

    @staticmethod
    def generate_file_key(mime_type: str, file_name: str) -> str:
        today = date.today()
        ext = file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
        asset_type = AttachmentMetaService.resolve_asset_type(mime_type).value
        uid = uuid.uuid7().hex
        path = f"{asset_type}s/{today.year}/{today.month:02d}/{today.day:02d}/{uid}"
        return f"{path}.{ext}" if ext else path

    def perform(self):
        mime_type = self.context["mime_type"]
        file_name = self.context["file_name"]

        try:
            asset_type = self.resolve_asset_type(mime_type)
        except ValueError:
            self.fail(
                message="This file format is not supported.",
                payload={"mime_type": [f"{mime_type} is not a supported format."]},
            )

        self.result["asset_type"] = asset_type
        self.result["file_key"] = self.generate_file_key(mime_type, file_name)
