from types import SimpleNamespace

from api.routers.dashboard import classify, format_timestamp, normalize_content


def test_classify_ai_comic_content():
    assert classify("AI漫剧合集", "")[0] == "明确漫剧"
    assert classify("原创二次元故事", "")[0] == "相关内容"
    assert classify("普通生活记录", "")[0] == "弱相关"


def test_format_timestamp_supports_seconds_and_milliseconds():
    assert format_timestamp(1719216000) == "2024-06-24 16:00:00"
    assert format_timestamp(1719216000000) == "2024-06-24 16:00:00"


def test_normalize_kuaishou_uses_mysql_metrics_and_top_comment():
    video = SimpleNamespace(
        video_id="v1",
        title="AI漫剧",
        desc="",
        publish_time="2026-06-24 12:00:00",
        create_time=0,
        view_count="1000",
        viewd_count="",
        like_count="80",
        liked_count="",
        comment_count="12",
        video_url="https://example.com/v1",
        nickname="作者",
        source_keyword="AI漫剧",
        last_modify_ts=1,
    )
    comments = [
        SimpleNamespace(content="普通评论", like_count="2", create_time=1),
        SimpleNamespace(content="最高赞评论", like_count="20", create_time=2),
    ]

    row = normalize_content("kuaishou", video, comments)

    assert row["view_count"] == 1000
    assert row["like_count"] == 80
    assert row["captured_comment_count"] == 2
    assert row["top_comment"] == "最高赞评论"
