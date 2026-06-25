from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import serializers, status

from atlas.models.tale import Tale
from atlas.models.dish import Dish
from atlas.models.outlet import Outlet
from atlas.models.choices import TaleVisibility
from atlas.response import APIResponse


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ["id", "name", "created_at"]


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Outlet
        fields = ["id", "name", "address", "city", "state", "country", "created_at"]


class TaleSerializer(serializers.ModelSerializer):
    dish = DishSerializer()
    outlet = OutletSerializer()

    class Meta:
        model = Tale
        fields = [
            "id",
            "story",
            "visibility",
            "photo_url",
            "dish",
            "outlet",
            "created_at",
        ]


class RecentTaleQuerySerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=["published", "private", "drafts"], required=False
    )


class ProfileViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(
        methods=["GET"], detail=False, url_name="tales-recent", url_path="tales/recent"
    )
    def tales_recent(self, request, *args, **kwargs):
        query_serializer = RecentTaleQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        query = query_serializer.validated_data
        tales = Tale.objects.filter(user=request.user)

        match query.get("type"):
            case "drafts":
                tales = tales.filter(published_at__isnull=True)
            case "published":
                tales = tales.filter(published_at__isnull=False)
            case "private":
                tales = tales.filter(visibility=TaleVisibility.PRIVATE)
            case _:
                pass

        tales = (
            tales.select_related("photo")
            .select_related("dish")
            .select_related("outlet")
            .order_by("-created_at")
        )
        serializer = TaleSerializer(tales, many=True)

        return APIResponse(ok=True, payload=serializer.data, status=status.HTTP_200_OK)
