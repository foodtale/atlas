from pathlib import Path

from django.conf import settings
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET


@require_GET
def health_check(request):
    return JsonResponse({"ok": True, "version": settings.ATLAS_VERSION})


@csrf_exempt
@require_POST
def upload_local(request, file_key):
    if not settings.DEBUG:
        raise Http404

    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"ok": False, "message": "No file provided."}, status=400)

    dest = Path(settings.MEDIA_ROOT) / file_key
    dest.parent.mkdir(parents=True, exist_ok=True)

    with dest.open("wb") as f:
        for chunk in file.chunks():
            f.write(chunk)

    return JsonResponse({"ok": True}, status=200)
