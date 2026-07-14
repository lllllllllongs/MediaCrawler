import os

target = "D:/codex/MediaCrawler/MediaCrawler/api/routers/dashboard_zhihu.py"

content = '''# -*- coding: utf-8 -*-
"""
Zhihu JSON-file dashboard router.
Reads crawled data from data/zhihu/json/*.json and serves it via API.
"""
import glob
import json
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/dashboard", tags=["zhihu-dashboard"])

_ZHIHU_JSON_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "zhihu", "json")
)


def _resolve_zhihu_json_dir() -> str:
    """Return the resolved zhihu json directory, creating it if missing."""
    if not os.path.isdir(_ZHIHU_JSON_DIR):
        os.makedirs(_ZHIHU_JSON_DIR, exist_ok=True)
    return _ZHIHU_JSON_DIR


def _as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _normalize_zhihu_content(item: dict) -> dict:
    created_time = _as_int(item.get("created_time", 0))
    publish_time = (
        datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M:%S")
        if created_time
        else ""
    )
    return {
        "content_id": str(item.get("content_id", "")),
        "content_type": item.get("content_type", ""),
        "title": item.get("title", ""),
        "desc": item.get("desc", ""),
        "author": item.get("user_nickname", ""),
        "publish_time": publish_time,
        "voteup_count": _as_int(item.get("voteup_count", 0)),
        "comment_count": _as_int(item.get("comment_count", 0)),
        "url": item.get("content_url", ""),
        "source_keyword": item.get("source_keyword", ""),
        "user_link": item.get("user_link", ""),
        "last_modify_ts": _as_int(item.get("last_modify_ts", 0)),
    }


async def load_zhihu_data() -> dict:
    json_dir = _resolve_zhihu_json_dir()
    json_files = sorted(glob.glob(os.path.join(json_dir, "*.json")))
    if not json_files:
        return {
            "platform": "zhihu",
            "platform_label": "\u77e5\u4e4e",
            "source": "JSON File",
            "updated_at": 0,
            "summary": {
                "content_count": 0,
                "total_voteups": 0,
                "total_comments": 0,
            },
            "rows": [],
        }

    all_contents: list[dict] = []
    for filepath in json_files:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to read {os.path.basename(filepath)}: {exc}",
            )
        if isinstance(data, list):
            all_contents.extend(data)
        elif isinstance(data, dict):
            all_contents.append(data)

    rows = [_normalize_zhihu_content(item) for item in all_contents]
    rows.sort(key=lambda row: -row["voteup_count"])

    updated_at = max((row["last_modify_ts"] for row in rows), default=0)
    if updated_at and updated_at < 100_000_000_000:
        updated_at *= 1000

    return {
        "platform": "zhihu",
        "platform_label": "\u77e5\u4e4e",
        "source": "JSON File",
        "updated_at": updated_at,
        "summary": {
            "content_count": len(rows),
            "total_voteups": sum(row["voteup_count"] for row in rows),
            "total_comments": sum(row["comment_count"] for row in rows),
        },
        "rows": rows,
    }


@router.get("/zhihu")
async def get_zhihu_dashboard():
    return await load_zhihu_data()


@router.get("/zhihu-summary")
async def get_zhihu_summary():
    data = await load_zhihu_data()
    return {
        "platform": data["platform"],
        "platform_label": data["platform_label"],
        "source": data["source"],
        "updated_at": data["updated_at"],
        **data["summary"],
    }
'''

with open(target, "w", encoding="utf-8") as f:
    f.write(content)
print("Written OK, size:", os.path.getsize(target))
