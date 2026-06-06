from django.conf import settings
from django.utils.timezone import now
from rest_framework.viewsets import ViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from atlas.response import APIResponse
from atlas.models.otp_request import OTPRequest
from atlas.models.choices import OTPPurpose, OTPTarget
from atlas.models.user import User, UserSession
from atlas.tasks.otp import send_otp


class OTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp_request_id = serializers.UUIDField()
    otp = serializers.CharField()


class OnboardingSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email_address = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    def validate_email_address(self, value):
        return value or None


class LoggedInUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "full_name", "email_address", "is_onboarded"]


class AuthViewSet(ViewSet):
    @action(
        methods=["POST"], detail=False, url_name="otp-request", url_path="otp/request"
    )
    def otp_request(self, request, *args, **kwargs):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        user = User.objects.filter(
            phone_number=validated_data.get("phone_number")
        ).first()
        if not user:
            user = User.objects.create(phone_number=validated_data.get("phone_number"))

        request, otp = OTPRequest.create_otp(
            purpose=OTPPurpose.LOGIN, target=OTPTarget.PHONE, user=user
        )

        send_otp.delay(phone_number=validated_data.get("phone_number"), otp=otp)

        payload = {
            "otp_request_id": request.id,
        }
        return APIResponse(
            ok=True,
            message="OTP has been sent.",
            status=status.HTTP_200_OK,
            payload=payload,
        )

    @action(
        methods=["POST"], detail=False, url_name="otp-verify", url_path="otp/verify"
    )
    def otp_verify(self, request, *args, **kwargs):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        otp_request = OTPRequest.objects.filter(
            id=validated_data.get("otp_request_id"),
            user__phone_number=validated_data.get("phone_number"),
        ).first()
        if not otp_request:
            return APIResponse(
                ok=False,
                message="Invalid OTP Verify ID.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        ok, message = otp_request.verify_otp(validated_data.get("otp"))
        if not ok:
            return APIResponse(
                ok=False, message=message, status=status.HTTP_400_BAD_REQUEST
            )

        user = otp_request.user
        if not user.is_verified:
            user.mark_as_verified()

        session = UserSession.objects.create(user=user)
        logged_in_user_serializer = LoggedInUserSerializer(user)

        paylaod = {
            "session_token": session.session_token,
            "user": logged_in_user_serializer.data,
        }

        return APIResponse(ok=True, payload=paylaod, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_name="profile",
        url_path="profile",
        permission_classes=[IsAuthenticated],
    )
    def profile(self, request, *args, **kwargs):
        user = request.user
        serializer = LoggedInUserSerializer(user)
        return APIResponse(ok=True, payload=serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["PATCH"],
        detail=False,
        url_name="onboarding",
        url_path="onboarding",
        permission_classes=[IsAuthenticated],
    )
    def onboarding(self, request, *args, **kwargs):
        serializer = OnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        validated_data = serializer.validated_data

        for key, value in validated_data.items():
            setattr(user, key, value)
        user.onboarded_at = now()
        user.save(update_fields=[*validated_data.keys(), "onboarded_at"])

        return APIResponse(
            ok=True,
            payload=LoggedInUserSerializer(user).data,
            status=status.HTTP_200_OK,
        )