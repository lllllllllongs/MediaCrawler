from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database.db_session import get_async_engine
from database.models import (
    DouyinAweme,
    DouyinAwemeComment,
    KuaishouVideo,
    KuaishouVideoComment,
    XhsNote,
    XhsNoteComment,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

EXACT_TERMS = ("漫剧", "ai短剧", "ai动画")
RELATED_TERMS = ("短剧", "动画", "动漫", "二次元", "漫画", "灵境计划", "剧场", "兽世")

PLATFORMS = {
    "kuaishou": {
        "label": "快手",
        "content_model": KuaishouVideo,
        "comment_model": KuaishouVideoComment,
        "content_id": "video_id",
        "comment_content_id": "video_id",
    },
    "douyin": {
        "label": "抖音",
        "content_model": DouyinAweme,
        "comment_model": DouyinAwemeComment,
        "content_id": "aweme_id",
        "comment_content_id": "aweme_id",
    },
    "xiaohongshu": {
        "label": "小红书",
        "content_model": XhsNote,
        "comment_model": XhsNoteComment,
        "content_id": "note_id",
        "comment_content_id": "note_id",
    },
}


def as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def classify(title: str, desc: str) -> tuple[str, str]:
    text = f"{title or ''} {desc or ''}".lower()
    exact = [term for term in EXACT_TERMS if term in text]
    if exact:
        return "明确漫剧", "、".join(exact)
    related = [term for term in RELATED_TERMS if term in text]
    if related:
        return "相关内容", "、".join(related)
    return "弱相关", "仅由平台搜索返回"


def format_timestamp(value, milliseconds: bool = False) -> str:
    timestamp = as_int(value)
    if not timestamp:
        return ""
    if milliseconds or timestamp > 10_000_000_000:
        timestamp /= 1000
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def normalize_content(platform: str, item, comments: list) -> dict:
    if platform == "kuaishou":
        content_id = str(item.video_id or "")
        title = item.title or ""
        desc = item.desc or ""
        publish_time = item.publish_time or format_timestamp(item.create_time, True)
        views = as_int(item.view_count or item.viewd_count)
        likes = as_int(item.like_count or item.liked_count)
        collected = 0
        comment_count = as_int(item.comment_count)
        share_count = 0
        url = item.video_url or ""
    elif platform == "douyin":
        content_id = str(item.aweme_id or "")
        title = item.title or ""
        desc = item.desc or ""
        publish_time = format_timestamp(item.create_time)
        views = 0
        likes = as_int(item.liked_count)
        collected = as_int(item.collected_count)
        comment_count = as_int(item.comment_count)
        share_count = as_int(item.share_count)
        url = item.aweme_url or ""
    else:
        content_id = str(item.note_id or "")
        title = item.title or ""
        desc = item.desc or ""
        publish_time = format_timestamp(item.time, True)
        views = 0
        likes = as_int(item.liked_count)
        collected = as_int(item.collected_count)
        comment_count = as_int(item.comment_count)
        share_count = as_int(item.share_count)
        url = item.note_url or ""

    sorted_comments = sorted(
        comments,
        key=lambda comment: (
            as_int(getattr(comment, "like_count", 0)),
            as_int(getattr(comment, "create_time", 0)),
        ),
        reverse=True,
    )
    top_comment = sorted_comments[0] if sorted_comments else None
    relevance, relevance_reason = classify(title, desc)
    return {
        "content_id": content_id,
        "title": title,
        "desc": desc,
        "author": item.nickname or "",
        "publish_time": publish_time,
        "view_count": views,
        "like_count": likes,
        "collected_count": collected,
        "comment_count": comment_count,
        "share_count": share_count,
        "captured_comment_count": len(comments),
        "top_comment": getattr(top_comment, "content", "") if top_comment else "",
        "top_comment_likes": as_int(getattr(top_comment, "like_count", 0)),
        "url": url,
        "source_keyword": item.source_keyword or "",
        "relevance": relevance,
        "relevance_reason": relevance_reason,
        "last_modify_ts": as_int(item.last_modify_ts),
    }


async def load_platform_data(platform: str) -> dict:
    settings = PLATFORMS.get(platform)
    if not settings:
        raise HTTPException(status_code=404, detail="Unsupported dashboard platform")

    engine = get_async_engine("db")
    if engine is None:
        raise HTTPException(status_code=503, detail="MySQL is not configured")

    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with session_factory() as session:
            contents = (
                await session.execute(select(settings["content_model"]))
            ).scalars().all()
            comments = (
                await session.execute(select(settings["comment_model"]))
            ).scalars().all()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"MySQL query failed: {type(exc).__name__}",
        ) from exc

    comments_by_content = defaultdict(list)
    for comment in comments:
        key = str(getattr(comment, settings["comment_content_id"]) or "")
        comments_by_content[key].append(comment)

    rows = [
        normalize_content(
            platform,
            item,
            comments_by_content[str(getattr(item, settings["content_id"]) or "")],
        )
        for item in contents
    ]
    rows.sort(key=lambda row: (row["relevance"] == "弱相关", -row["like_count"]))
    relevant = [row for row in rows if row["relevance"] != "弱相关"]
    updated_at = max((row["last_modify_ts"] for row in rows), default=0)
    if updated_at and updated_at < 100_000_000_000:
        updated_at *= 1000
    return {
        "platform": platform,
        "platform_label": settings["label"],
        "source": "MySQL",
        "updated_at": updated_at,
        "summary": {
            "content_count": len(rows),
            "relevant_count": len(relevant),
            "total_views": sum(row["view_count"] for row in relevant),
            "total_likes": sum(row["like_count"] for row in relevant),
            "total_collected": sum(row["collected_count"] for row in relevant),
            "total_comments": sum(row["comment_count"] for row in relevant),
            "captured_comments": len(comments),
        },
        "rows": rows,
    }


@router.get("/summary")
async def get_dashboard_summary():
    platforms = []
    for platform in PLATFORMS:
        data = await load_platform_data(platform)
        platforms.append(
            {
                "platform": platform,
                "platform_label": data["platform_label"],
                "updated_at": data["updated_at"],
                **data["summary"],
            }
        )
    return {"source": "MySQL", "platforms": platforms}


@router.get("/{platform}")
async def get_platform_dashboard(platform: str):
    return await load_platform_data(platform)
