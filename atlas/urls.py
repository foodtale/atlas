from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from atlas.views import health_check, upload_local

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("atlas.api.v1")),
    path("health", health_check),
    path("debug/upload/<path:file_key>", upload_local),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
