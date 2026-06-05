from rest_framework.routers import SimpleRouter

from .auth import AuthViewSet
from .attachment import AttachmentViewSet
from .onboarding import OnboardingViewSet

router = SimpleRouter(trailing_slash=False, use_regex_path=False)

router.register("auth", AuthViewSet, basename="auth")
router.register("onboarding", OnboardingViewSet, basename="onboarding")
router.register("attachments", AttachmentViewSet, basename="attachment")

urlpatterns = router.urls
