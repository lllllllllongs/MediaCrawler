from database.models import KuaishouVideo
from scripts.import_json_to_mysql import deduplicate, normalize_record


def test_deduplicate_keeps_latest_record():
    records = [
        {"video_id": "v1", "like_count": "1", "last_modify_ts": 1},
        {"video_id": "v1", "like_count": "2", "last_modify_ts": 2},
    ]

    assert deduplicate(records, "video_id") == [records[1]]


def test_normalize_kuaishou_preserves_readable_metrics():
    record = {
        "video_id": "v1",
        "like_count": "12",
        "view_count": "345",
        "comment_count": "6",
        "publish_time": "2026-06-24 12:00:00",
        "unknown": "ignored",
    }

    item = normalize_record(KuaishouVideo, record)

    assert item["liked_count"] == "12"
    assert item["viewd_count"] == "345"
    assert item["like_count"] == "12"
    assert item["view_count"] == "345"
    assert "unknown" not in item
