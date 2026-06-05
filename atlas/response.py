from rest_framework import status as http_status
from rest_framework.response import Response


class APIResponse(Response):
    def __init__(
        self,
        *,
        ok: bool,
        message=None,
        payload=None,
        status=None,
        **kwargs,
    ):
        if status is None:
            status = http_status.HTTP_200_OK if ok else http_status.HTTP_400_BAD_REQUEST

        super().__init__(
            data={
                "ok": ok,
                "message": message,
                "data": payload if ok else None,
                "error": payload if not ok else None,
            },
            status=status,
            **kwargs,
        )
