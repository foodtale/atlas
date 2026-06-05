from celery import shared_task
from celery.utils.log import get_task_logger
from atlas.services.otp_send_service import OTPSendService

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
)
def send_otp(self, phone_number: str, otp: str):
    logger.info("Sending OTP to %s (attempt %d)", phone_number, self.request.retries + 1)

    _, error = OTPSendService.call(phone_number=phone_number, otp=otp)

    if error:
        logger.warning(
            "OTPSendService failed for %s: %s (attempt %d/%d)",
            phone_number,
            error.message,
            self.request.retries + 1,
            self.max_retries + 1,
        )
        raise self.retry(
            exc=Exception(error.message),
            countdown=10 * (2 ** self.request.retries),
        )

    logger.info("OTP sent successfully to %s", phone_number)
