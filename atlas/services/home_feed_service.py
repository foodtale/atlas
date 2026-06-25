from atlas.feeds import resolve
from atlas.models.config import Config
from atlas.services.base import BaseService


class HomeFeedService(BaseService):
    """
    Entry point for the home feed. Resolves the feed type and delegates
    to the appropriate feed implementation.

    Context:
        user         — authenticated User instance
        next_cursor  — opaque cursor string to paginate forward (optional)

    Result:
        tales        — list of Tale instances, each with ._source attached
        next_cursor  — cursor for the next page, or None
        prev_cursor  — None (reserved)
    """

    def perform(self):
        user = self.context["user"]
        next_cursor = self.context.get("next_cursor")

        feed_type = user.feed_type or Config.get("DEFAULT_FEED_ALGORITHM") or "chronological"
        feed = resolve(feed_type)

        result = feed.get_tales(user=user, cursor=next_cursor)

        self.result["tales"] = result["tales"]
        self.result["next_cursor"] = result["next_cursor"]
        self.result["prev_cursor"] = result["prev_cursor"]
