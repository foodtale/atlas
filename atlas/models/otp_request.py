import secrets
from django.db import models
from django.utils.timezone import now, timedelta
from django.contrib.auth.hashers import make_password, check_password

from atlas.models.base import BaseModel
from atlas.models.choices import OTPPurpose, OTPTarget


class OTPRequest(BaseModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="otp_requests",
    )
    otp_hash = models.CharField(max_length=255)
    target = models.CharField(max_length=128, choices=OTPTarget.choices)
    purpose = models.CharField(max_length=128, choices=OTPPurpose.choices)

    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    attempt_count = models.PositiveIntegerField(default=0)
    resend_count = models.PositiveIntegerField(default=0)

    MAX_ATTEMPTS = 5

    class Meta:
        db_table = "otp_requests"

    @classmethod
    def create_otp(cls, *, purpose, target, expiry_minutes=5, user=None):
        otp = f"{secrets.randbelow(1_000_000):06d}"
        otp_request = cls.objects.create(
            user=user,
            purpose=purpose,
            target=target,
            otp_hash=make_password(otp),
            expires_at=now() + timedelta(minutes=expiry_minutes),
        )
        return otp_request, otp

    def verify_otp(self, otp: str) -> bool:
        if self.verified_at is not None:
            return False, "OTP has already been used"

        if self.expires_at <= now():
            return False, "OTP has expired"

        if self.attempt_count >= self.MAX_ATTEMPTS:
            return False, "Maximum OTP attempts exceeded"

        if not check_password(otp, self.otp_hash):
            self.attempt_count += 1
            self.save(update_fields=["attempt_count"])

            remaining = self.MAX_ATTEMPTS - self.attempt_count

            if remaining <= 0:
                return False, "Maximum OTP attempts exceeded"

            return False, f"Invalid OTP. {remaining} attempts remaining"

        self.verified_at = now()
        self.save(update_fields=["verified_at"])

        return True, "OTP verified successfully"
