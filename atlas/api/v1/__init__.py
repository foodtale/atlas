from rest_framework.routers import SimpleRouter

from .auth import AuthViewSet
from .common import AttachmentViewSet

router = SimpleRouter(trailing_slash=False, use_regex_path=False)

router.register("auth", AuthViewSet, basename="auth")
router.register("attachments", AttachmentViewSet, basename="attachment")

urlpatterns = router.urls
