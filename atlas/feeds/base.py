import base64
import json

PAGE_SIZE = 20


class BaseFeed:
    """
    All feed types inherit from this. Subclasses implement `get_tales`.

    get_tales must return:
        {
            "tales": [...],       # Tale instances with ._source attached
            "next_cursor": str | None,
            "prev_cursor": None,  # reserved for future
        }
    """

    def get_tales(self, user, cursor: str | None) -> dict:
        raise NotImplementedError

    # ── Cursor helpers shared across all feed types ───────────────────────────

    @staticmethod
    def encode_cursor(tale) -> str:
        data = {"published_at": tale.published_at.isoformat(), "id": str(tale.id)}
        return base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> dict:
        return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
