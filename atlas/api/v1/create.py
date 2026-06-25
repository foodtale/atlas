from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated

from atlas.models.choices import TaleVisibility
from atlas.models.dish import Dish
from atlas.models.outlet import Outlet
from atlas.models.tale import Tale
from atlas.response import APIResponse
from atlas.services.create_tale_service import CreateTaleService
from atlas.services.outlet_search_service import OutletSearchService
from atlas.tasks.attachments import optimize_image


class OutletSearchSerializer(serializers.Serializer):
    query = serializers.CharField()


class DishSearchSerializer(serializers.Serializer):
    place_id = serializers.CharField()
    dish_name = serializers.CharField()


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = [
            "id",
            "name",
            "created_at",
        ]


class TaleCreateSerializer(serializers.Serializer):
    place_id = serializers.CharField()
    dish_name = serializers.CharField()
    story = serializers.CharField(required=False, allow_blank=True, default="")
    would_order_again = serializers.BooleanField(default=True)
    visibility = serializers.ChoiceField(
        choices=TaleVisibility.choices,
        default=TaleVisibility.PUBLIC,
    )
    photo_id = serializers.UUIDField(required=False, allow_null=True, default=None)


class TaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tale
        fields = [
            "id",
            "outlet_id",
            "dish_id",
            "would_order_again",
            "story",
            "visibility",
            "photo_url",
            "created_at",
        ]


class CreateViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(
        methods=["GET"],
        detail=False,
        url_name="outlet-search",
        url_path="outlet/search",
    )
    def outlet_search(self, request, *args, **kwargs):
        serializer = OutletSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        query = serializer.validated_data["query"]

        result, error = OutletSearchService.call(
            query=query,
            include_google_searches=True,
        )

        if error:
            return APIResponse(
                ok=False,
                message=error.message,
                payload=error.payload,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return APIResponse(
            ok=True,
            payload=result["outlets"],
            status=status.HTTP_200_OK,
        )

    @action(
        methods=["GET"], detail=False, url_name="dish-search", url_path="dish/search"
    )
    def dish_search(self, request, *args, **kwargs):
        serializer = DishSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        outlet = Outlet.objects.filter(place_id=validated_data.get("place_id")).first()
        if not outlet:
            return APIResponse(ok=True, payload=[], status=status.HTTP_200_OK)

        dishes = Dish.objects.filter(
            outlet__place_id=validated_data.get("place_id"),
            name__icontains=validated_data.get("dish_name").strip().lower(),
        )
        dish_serializer = DishSerializer(dishes, many=True)

        return APIResponse(
            ok=True, payload=dish_serializer.data, status=status.HTTP_200_OK
        )

    @action(methods=["POST"], detail=False, url_name="tale", url_path="tale")
    def tale(self, request, *args, **kwargs):
        serializer = TaleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result, error = CreateTaleService.call(
            user=request.user,
            **serializer.validated_data,
        )

        if error:
            return APIResponse(
                ok=False,
                message=error.message,
                status=status.HTTP_400_BAD_REQUEST,
            )

        tale = result.get("tale")

        if tale.photo_id:
            optimize_image.delay(str(tale.photo_id))

        tale_serializer = TaleSerializer(tale)

        return APIResponse(
            ok=True,
            message="You'r tale is published....",
            payload=tale_serializer.data,
            status=status.HTTP_201_CREATED,
        )
