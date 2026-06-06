from django.db import models


class OTPPurpose(models.TextChoices):
    LOGIN = ("login", "Login")
    EMAIL_VERIFICATION = ("email_verification", "Email Verification")
    PASSWORD_RESET = ("password_reset", "Password Reset")


class OTPTarget(models.TextChoices):
    EMAIL = ("email", "Email")
    PHONE = ("phone", "Phone")


class AttachmentAssetType(models.TextChoices):
    IMAGE = ("image", "Image")
    VIDEO = ("video", "Video")
    FILE = ("file", "File")


class FoodTaleVisibility(models.TextChoices):
    PUBLIC = ("public", "Public")
    FOLLOWERS = ("followers", "Followers")
    PRIVATE = ("private", "Private")
