from unittest.mock import AsyncMock

import pytest

from store import kuaishou


@pytest.mark.asyncio
async def test_video_metrics_are_saved_with_readable_fields(monkeypatch):
    store = AsyncMock()
    monkeypatch.setattr(kuaishou.KuaishouStoreFactory, "create_store", lambda: store)

    await kuaishou.update_kuaishou_video({
        "type": 1,
        "author": {"id": "author", "name": "name"},
        "photo": {
            "id": "video",
            "caption": "title",
            "timestamp": 1719216000000,
            "realLikeCount": 123,
            "viewCount": 4567,
            "commentCount": 89,
        },
    })

    item = store.store_content.await_args.kwargs["content_item"]
    assert item["like_count"] == "123"
    assert item["view_count"] == "4567"
    assert item["comment_count"] == "89"
    assert item["publish_time"] == "2024-06-24 16:00:00"


@pytest.mark.asyncio
async def test_comment_like_count_and_publish_time_are_saved(monkeypatch):
    store = AsyncMock()
    monkeypatch.setattr(kuaishou.KuaishouStoreFactory, "create_store", lambda: store)

    await kuaishou.update_ks_video_comment("video", {
        "comment_id": 1,
        "timestamp": 1719216000000,
        "content": "comment",
        "likeCount": 12,
    })

    item = store.store_comment.await_args.kwargs["comment_item"]
    assert item["like_count"] == "12"
    assert item["publish_time"] == "2024-06-24 16:00:00"
