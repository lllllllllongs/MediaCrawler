import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.time_util import get_time_str_from_unix_time


DATA_DIR = PROJECT_ROOT / "data" / "kuaishou" / "json"


def backfill_file(path: Path, is_comment: bool) -> int:
    records = json.loads(path.read_text(encoding="utf-8"))
    changed = 0

    for record in records:
        before = dict(record)
        create_time = record.get("create_time")
        if create_time:
            record.setdefault("publish_time", get_time_str_from_unix_time(create_time))

        if is_comment:
            record.setdefault("like_count", "0")
        else:
            record.setdefault("like_count", record.get("liked_count", "0"))
            record.setdefault("view_count", record.get("viewd_count", "0"))
            record.setdefault("comment_count", "0")

        changed += record != before

    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=4),
        encoding="utf-8",
    )
    return changed


def main() -> None:
    total = 0
    for path in DATA_DIR.glob("*.json"):
        total += backfill_file(path, "comments" in path.name)
    print(f"Backfilled {total} Kuaishou records")


if __name__ == "__main__":
    main()
