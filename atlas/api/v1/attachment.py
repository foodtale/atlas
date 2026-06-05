from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ViewSet

from atlas.models.attachment import Attachment
from atlas.response import APIResponse
from atlas.services.attachment_meta_service import AttachmentMetaService


class UploadRequestSerializer(serializers.Serializer):
    file_name = serializers.CharField()
    mime_type = serializers.CharField()


class AttachmentViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=["POST"], detail=False, url_path="request/upload", url_name="request-upload")
    def request_upload(self, request):
        serializer = UploadRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mime_type = serializer.validated_data["mime_type"]
        file_name = serializer.validated_data["file_name"]

        result, error = AttachmentMetaService.call(
            mime_type=mime_type,
            file_name=file_name,
        )

        if error:
            return APIResponse(
                ok=False,
                message=error.message,
                payload=error.payload,
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        attachment = Attachment.objects.create(
            uploaded_by=request.user,
            file_key=result["file_key"],
            file_name=file_name,
            mime_type=mime_type,
            asset_type=result["asset_type"],
            expires_at=timezone.now() + timedelta(days=1),
        )

        return APIResponse(
            ok=True,
            message="Upload URL generated.",
            status=status.HTTP_201_CREATED,
            payload={
                "attachment_id": attachment.id,
                "upload_url": attachment.upload_url,
                "file_key": attachment.file_key,
            },
        )
