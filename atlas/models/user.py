import secrets
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.timezone import now

from atlas.models.base import BaseModel


class UserManager(BaseUserManager):
    def create_superuser(self, phone_number, email_address, full_name, password):
        user = self.model(
            phone_number=phone_number,
            email_address=self.normalize_email(email_address),
            full_name=full_name,
            onboarded_at=now,
            verified_at=now,
            is_superuser=True,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(BaseModel, AbstractBaseUser):
    phone_number = models.CharField(max_length=32, unique=True)
    email_address = models.EmailField(blank=True, null=True)
    full_name = models.CharField(blank=True, null=True, max_length=256)
    is_superuser = models.BooleanField(default=False)
    avatar = models.ForeignKey(
        "atlas.Attachment", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    blocked_at = models.DateTimeField(blank=True, null=True)
    blocked_reason = models.TextField(blank=True, null=True)

    onboarded_at = models.DateTimeField(blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    food_tales_count = models.PositiveIntegerField(default=0)
    public_food_tales_count = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email_address", "full_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser

    @property
    def is_blocked(self):
        return self.blocked_at is not None

    @property
    def is_onboarded(self):
        return self.onboarded_at is not None

    @property
    def is_verified(self):
        return self.verified_at is not None

    @property
    def avatar_url(self):
        return self.avatar.url

    def mark_as_verified(self):
        self.verified_at = now()
        self.save(update_fields=["verified_at"])


class UserSession(BaseModel):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="sessions")
    session_token = models.CharField(max_length=64, unique=True, blank=True)
    fcm_token = models.TextField(blank=True, null=True)
    device_name = models.CharField(max_length=128, blank=True, null=True)

    expires_at = models.DateTimeField(blank=True, null=True)
    revoked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "user_sessions"

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.session_token = secrets.token_urlsafe(48)
        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= now()

    @property
    def is_revoked(self):
        return self.revoked_at is not None
