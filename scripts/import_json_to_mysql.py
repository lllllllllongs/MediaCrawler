import argparse
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import inspect, select, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config
from database.db import init_db
from database.db_session import get_async_engine
from database.models import DouyinAweme, KuaishouVideo, KuaishouVideoComment


IMPORTS = (
    ("douyin_contents", "douyin/json/*_contents_*.json", DouyinAweme, "aweme_id"),
    ("kuaishou_contents", "kuaishou/json/*_contents_*.json", KuaishouVideo, "video_id"),
    (
        "kuaishou_comments",
        "kuaishou/json/*_comments_*.json",
        KuaishouVideoComment,
        "comment_id",
    ),
)

KUAISHOU_COLUMNS = {
    "kuaishou_video": {
        "like_count": "TEXT NULL COMMENT '点赞数（可读字段）'",
        "view_count": "TEXT NULL COMMENT '播放数（可读字段）'",
        "comment_count": "TEXT NULL COMMENT '评论数'",
        "publish_time": "VARCHAR(255) NULL COMMENT '发布时间'",
    },
    "kuaishou_video_comment": {
        "like_count": "TEXT NULL COMMENT '点赞数'",
        "publish_time": "VARCHAR(255) NULL COMMENT '发布时间'",
    },
}


def as_int(value) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def load_records(paths: list[Path]) -> list[dict]:
    records = []
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{path} must contain a JSON array")
        records.extend(data)
    return records


def deduplicate(records: list[dict], key_field: str) -> list[dict]:
    by_key = {}
    for record in records:
        key = str(record.get(key_field) or "")
        if not key:
            continue
        current = by_key.get(key)
        if current is None or as_int(record.get("last_modify_ts")) >= as_int(
            current.get("last_modify_ts")
        ):
            by_key[key] = record
    return list(by_key.values())


def normalize_record(model, record: dict) -> dict:
    item = dict(record)
    if model is KuaishouVideo:
        item["liked_count"] = item.get("liked_count") or item.get("like_count")
        item["viewd_count"] = item.get("viewd_count") or item.get("view_count")
        item["like_count"] = item.get("like_count") or item.get("liked_count")
        item["view_count"] = item.get("view_count") or item.get("viewd_count")
    columns = {column.name for column in model.__table__.columns if column.name != "id"}
    return {key: value for key, value in item.items() if key in columns}


async def ensure_kuaishou_columns() -> None:
    engine = get_async_engine("db")
    async with engine.begin() as connection:
        existing = await connection.run_sync(
            lambda sync_connection: {
                table: {
                    column["name"]
                    for column in inspect(sync_connection).get_columns(table)
                }
                for table in KUAISHOU_COLUMNS
            }
        )
        for table, columns in KUAISHOU_COLUMNS.items():
            for column, definition in columns.items():
                if column not in existing[table]:
                    await connection.execute(
                        text(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}")
                    )


async def import_records(model, key_field: str, records: list[dict]) -> dict:
    unique_records = deduplicate(records, key_field)
    engine = get_async_engine("db")
    inserted = 0
    updated = 0

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        for record in unique_records:
            item = normalize_record(model, record)
            key = item[key_field]
            result = await session.execute(
                select(model).where(getattr(model, key_field) == key)
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                session.add(model(**item))
                inserted += 1
            else:
                for field, value in item.items():
                    setattr(existing, field, value)
                updated += 1
        await session.commit()

    return {
        "raw": len(records),
        "unique": len(unique_records),
        "inserted": inserted,
        "updated": updated,
    }


async def main(data_dir: Path) -> None:
    config.SAVE_DATA_OPTION = "db"
    await init_db("db")
    await ensure_kuaishou_columns()

    summary = {}
    for name, pattern, model, key_field in IMPORTS:
        paths = sorted(data_dir.glob(pattern))
        records = load_records(paths)
        summary[name] = await import_records(model, key_field, records)
        summary[name]["files"] = len(paths)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=PROJECT_ROOT / "data",
    )
    args = parser.parse_args()
    asyncio.run(main(args.data_dir))
