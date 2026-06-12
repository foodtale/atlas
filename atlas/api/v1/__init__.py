from rest_framework.routers import SimpleRouter

from .auth import AuthViewSet
from .common import AttachmentViewSet
from .create import CreateViewSet

router = SimpleRouter(trailing_slash=False, use_regex_path=False)

router.register("auth", AuthViewSet, basename="auth")
router.register("attachments", AttachmentViewSet, basename="attachment")
router.register("create", CreateViewSet, basename="create")

urlpatterns = router.urls
