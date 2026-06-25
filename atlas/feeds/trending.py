from atlas.feeds.base import BaseFeed


class TrendingFeed(BaseFeed):
    """
    Surfaces high-engagement tales in the user's city within a short time window.
    """

    def get_tales(self, user, cursor: str | None) -> dict:
        pass
