from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from atlas.models.config import Config
from atlas.models.user import User, UserSession

admin.site.unregister(Group)


# ── User forms ────────────────────────────────────────────────────────────────

class UserCreationForm(forms.ModelForm):
    """Used by the admin add-user page. Collects a plain-text password and
    hashes it on save, exactly as Django docs recommend for AbstractBaseUser."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["phone_number", "full_name", "email_address", "username"]

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords don't match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Used by the admin change-user page. Replaces the raw password field
    with a read-only hash display, as Django docs recommend."""

    password = ReadOnlyPasswordHashField(
        help_text="Passwords are not stored in plain text. "
                  "Use <a href='../password/'>this form</a> to change it."
    )

    class Meta:
        model = User
        fields = [
            "phone_number",
            "email_address",
            "full_name",
            "username",
            "avatar",
            "password",
            "is_superuser",
            "verified_at",
            "onboarded_at",
            "blocked_at",
            "blocked_reason",
        ]


# ── User admin ────────────────────────────────────────────────────────────────

class UserSessionInline(admin.TabularInline):
    model = UserSession
    extra = 0
    readonly_fields = ["session_token", "device_name", "expires_at", "revoked_at", "created_at"]
    fields = ["session_token", "device_name", "expires_at", "revoked_at", "created_at"]
    can_delete = False
    show_change_link = False
    max_num = 10


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = [
        "phone_number", "full_name", "username",
        "is_superuser", "is_verified", "is_onboarded", "is_blocked",
        "created_at",
    ]
    list_filter = ["is_superuser"]
    search_fields = ["phone_number", "full_name", "username", "email_address"]
    ordering = ["-created_at"]
    filter_horizontal = []

    fieldsets = [
        (None, {
            "fields": ["phone_number", "password"],
        }),
        ("Personal info", {
            "fields": ["full_name", "email_address", "username", "avatar"],
        }),
        ("Status", {
            "fields": ["verified_at", "onboarded_at", "blocked_at", "blocked_reason"],
        }),
        ("Permissions", {
            "fields": ["is_superuser"],
        }),
        ("Stats", {
            "fields": [
                "followers_count", "following_count",
                "tales_count", "public_tales_count",
            ],
            "classes": ["collapse"],
        }),
    ]

    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": [
                "phone_number", "full_name", "email_address",
                "username", "password1", "password2",
            ],
        }),
    ]

    readonly_fields = [
        "followers_count", "following_count",
        "tales_count", "public_tales_count",
    ]

    inlines = [UserSessionInline]


# ── Config admin ──────────────────────────────────────────────────────────────

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ["key", "masked_value", "is_depreciated", "updated_at"]
    list_filter = ["is_depreciated"]
    search_fields = ["key", "description"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        (None, {
            "fields": ["key", "value"],
        }),
        ("Metadata", {
            "fields": ["description", "is_depreciated"],
        }),
        ("Timestamps", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"],
        }),
    ]

    @admin.display(description="Value")
    def masked_value(self, obj):
        if not obj.value:
            return "—"
        return f"{obj.value[:4]}{'•' * 12}"
