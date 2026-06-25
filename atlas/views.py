from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET


@require_GET
def home(request):
    html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Atlas</title></head>
<body style="margin:0;display:flex;align-items:center;justify-content:center;height:100vh;background:#F7F2EA;font-family:sans-serif;">
  <div style="text-align:center;">
    <h1 style="color:#704F37;font-size:2rem;font-weight:900;margin:0;">Atlas</h1>
    <p style="color:#8C6D58;margin:8px 0 0;">FoodTale API Engine &mdash; v{version}</p>
  </div>
</body>
</html>""".format(version=settings.ATLAS_VERSION)
    return HttpResponse(html)


@require_GET
def health_check(request):
    html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Health</title></head>
<body style="margin:0;display:flex;align-items:center;justify-content:center;height:100vh;background:#22c55e;font-family:sans-serif;">
  <div style="text-align:center;">
    <p style="color:#ffffff;font-size:1.5rem;font-weight:700;margin:0;">&#10003; OK</p>
    <p style="color:#dcfce7;margin:8px 0 0;">v{version}</p>
  </div>
</body>
</html>""".format(version=settings.ATLAS_VERSION)
    return HttpResponse(html)


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
