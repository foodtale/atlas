from atlas.feeds.base import BaseFeed


class RankedFeed(BaseFeed):
    """
    Scores tales by likes, recency decay, and follow relationship.
    """

    def get_tales(self, user, cursor: str | None) -> dict:
        pass
