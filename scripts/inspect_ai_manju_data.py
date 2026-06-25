from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "database" / "sqlite_tables.db"


CONTENT_TABLES = {
    "xhs": ("xhs_note", "note_id", "title", "liked_count", "collected_count", "comment_count", "share_count", None),
    "dy": ("douyin_aweme", "aweme_id", "title", "liked_count", "collected_count", "comment_count", "share_count", None),
    "ks": ("kuaishou_video", "video_id", "title", "liked_count", None, None, None, "viewd_count"),
}

COMMENT_TABLES = {
    "xhs": ("xhs_note_comment", "note_id", "content", "like_count"),
    "dy": ("douyin_aweme_comment", "aweme_id", "content", "like_count"),
    "ks": ("kuaishou_video_comment", "video_id", "content", None),
}


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "select 1 from sqlite_master where type = 'table' and name = ?",
        (table,),
    ).fetchone()
    return row is not None


def metric_value(raw: object) -> float:
    if raw is None:
        return 0.0
    text = str(raw).strip().lower().replace(",", "")
    if not text:
        return 0.0
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return 0.0
    value = float(match.group(1))
    if "万" in text or "w" in text:
        value *= 10000
    elif "亿" in text:
        value *= 100000000
    return value


def select_existing_columns(conn: sqlite3.Connection, table: str, columns: Iterable[str | None]) -> list[str]:
    available = {row[1] for row in conn.execute(f"pragma table_info({table})")}
    return [column for column in columns if column and column in available]


def print_content_summary(conn: sqlite3.Connection) -> None:
    print("== Content ==")
    for platform, table_config in CONTENT_TABLES.items():
        table = table_config[0]
        if not table_exists(conn, table):
            print(f"{platform}: table missing ({table})")
            continue

        total = conn.execute(f"select count(*) from {table}").fetchone()[0]
        columns = select_existing_columns(conn, table, table_config[1:])
        print(f"{platform}: {total} rows in {table}; fields: {', '.join(columns)}")


def print_top_comments(conn: sqlite3.Connection, limit: int) -> None:
    print("\n== Top Comments ==")
    for platform, (table, item_id_col, content_col, like_col) in COMMENT_TABLES.items():
        if not table_exists(conn, table):
            print(f"{platform}: table missing ({table})")
            continue

        total = conn.execute(f"select count(*) from {table}").fetchone()[0]
        if not like_col:
            print(f"{platform}: {total} rows in {table}; no comment-like field in current schema")
            continue

        rows = conn.execute(
            f"select {item_id_col}, {content_col}, {like_col} from {table}"
        ).fetchall()
        rows = sorted(rows, key=lambda row: metric_value(row[2]), reverse=True)[:limit]
        print(f"{platform}: {total} rows in {table}")
        for item_id, content, like_count in rows:
            clean_content = " ".join(str(content or "").split())
            print(f"  like={like_count} item={item_id} content={clean_content[:120]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect AI manju SQLite crawler data.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    if not args.db.exists():
        print(f"SQLite database does not exist: {args.db}")
        return 1

    with sqlite3.connect(args.db) as conn:
        print_content_summary(conn)
        print_top_comments(conn, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
