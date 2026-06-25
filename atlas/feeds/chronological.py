from atlas.feeds.base import BaseFeed


class ChronologicalFeed(BaseFeed):
    """
    Following + city tales sorted purely by recency.
    """

    def get_tales(self, user, cursor: str | None) -> dict:
        pass
