from django.db import models
from django.conf import settings

from atlas.models.base import BaseModel
from atlas.models.choices import AttachmentAssetType


class Attachment(BaseModel):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="attachments",
    )
    file_key = models.TextField()
    file_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=AttachmentAssetType.choices)
    expires_at = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        db_table = "attachments"

    @property
    def url(self):
        base = settings.MEDIA_CDN_URL.rstrip("/")
        key = self.file_key.lstrip("/")
        return f"{base}/{key}"

    @property
    def upload_url(self) -> str:
        if settings.DEBUG:
            base = settings.LOCAL_BASE_URL.rstrip("/")
            return f"{base}/debug/upload/{self.file_key}"

        # TODO: replace with real S3 presigned PUT URL once boto3 is added
        # import boto3
        # s3 = boto3.client("s3")
        # return s3.generate_presigned_url(
        #     "put_object",
        #     Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": self.file_key},
        #     ExpiresIn=3600,
        # )
        raise NotImplementedError("S3 presigned URL generation is not configured yet.")

    @property
    def is_expired(self):
        return self.expires_at is not None
