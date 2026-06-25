import io
import boto3
from pathlib import Path

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from PIL import Image, UnidentifiedImageError
from atlas.models.attachment import Attachment

logger = get_task_logger(__name__)

MAX_DIMENSION = 1920
JPEG_QUALITY = 82


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def optimize_image(self, attachment_id: str):
    try:
        attachment = Attachment.objects.get(id=attachment_id)
    except Attachment.DoesNotExist:
        logger.warning(
            "optimize_image: attachment %s not found, skipping", attachment_id
        )
        return

    if not attachment.mime_type.startswith("image/"):
        logger.info(
            "optimize_image: %s is not an image (%s), skipping",
            attachment_id,
            attachment.mime_type,
        )
        return

    if settings.DEBUG:
        _optimize_local(attachment)
    else:
        _optimize_s3(attachment)


def _optimize_local(attachment):
    src = Path(settings.MEDIA_ROOT) / attachment.file_key
    if not src.exists():
        logger.warning("optimize_image: file not found at %s", src)
        return

    try:
        with Image.open(src) as img:
            img = _compress(img)
            img.save(src, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    except Exception as exc:
        logger.error("optimize_image: failed to optimize %s: %s", src, exc)
        raise

    if attachment.mime_type != "image/jpeg":
        Attachment.objects.filter(pk=attachment.pk).update(mime_type="image/jpeg")

    logger.info("optimize_image: optimized %s", attachment.file_key)


def _optimize_s3(attachment):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    s3 = boto3.client("s3")

    obj = s3.get_object(Bucket=bucket, Key=attachment.file_key)
    raw = obj["Body"].read()

    with Image.open(io.BytesIO(raw)) as img:
        img = _compress(img)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        buf.seek(0)

    s3.put_object(
        Bucket=bucket,
        Key=attachment.file_key,
        Body=buf,
        ContentType="image/jpeg",
    )

    if attachment.mime_type != "image/jpeg":
        Attachment.objects.filter(pk=attachment.pk).update(mime_type="image/jpeg")

    logger.info("optimize_image: optimized s3://%s/%s", bucket, attachment.file_key)


def _compress(img):
    """Resize to MAX_DIMENSION on the longest side, convert to RGB JPEG."""
    # Strip orientation from EXIF by re-drawing
    img = img.copy()

    # Flatten transparency onto white background
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(
            img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
        )
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Downscale if larger than MAX_DIMENSION on either axis
    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    return img
