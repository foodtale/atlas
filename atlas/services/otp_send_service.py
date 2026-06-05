import logging

from django.conf import settings

from atlas.services.base import BaseService

logger = logging.getLogger(__name__)


class OTPSendService(BaseService):
    def perform(self):
        otp = self.context.get("otp")
        phone_number = self.context.get("phone_number")

        if settings.DEBUG:
            logger.info(
                "\n"
                "┌─────────────────────────────┐\n"
                "│         OTP DEBUG           │\n"
                "├─────────────────────────────┤\n"
                "│  Phone : %-19s│\n"
                "│  OTP   : %-19s│\n"
                "└─────────────────────────────┘",
                phone_number,
                otp,
            )
            return

        # TODO: integrate SMS gateway (Twilio / MSG91 / etc.)
        self.fail(message="SMS gateway not configured.")
