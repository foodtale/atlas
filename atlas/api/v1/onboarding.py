from django.utils.timezone import now
from rest_framework.viewsets import ViewSet
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from atlas.models.user import User
from atlas.response import APIResponse


class ProfileUpdateSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    email_address = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    def validate_email_address(self, value):
        return value or None


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email_address", "is_onboarded"]


class OnboardingViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(methods=["PATCH"], detail=False, url_name="profile", url_path="profile")
    def profile(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        validated_data = serializer.validated_data
        for key, value in validated_data.items():
            setattr(user, key, value)
        user.onboarded_at = now()
        user.save(update_fields=[*validated_data.keys(), "onboarded_at"])

        profile_serializer = ProfileSerializer(user)
        return APIResponse(
            ok=True, payload=profile_serializer.data, status=status.HTTP_200_OK
        )
