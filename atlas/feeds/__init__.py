from atlas.feeds.chronological import ChronologicalFeed
from atlas.feeds.ranked import RankedFeed
from atlas.feeds.trending import TrendingFeed

REGISTRY = {
    "chronological": ChronologicalFeed,
    "ranked": RankedFeed,
    "trending": TrendingFeed,
}


def resolve(feed_type: str | None):
    return REGISTRY.get(feed_type or "chronological", ChronologicalFeed)()
