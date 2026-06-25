from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.main import app


def assert_ok(response, label: str) -> None:
    if response.status_code != 200:
        raise AssertionError(f"{label} returned HTTP {response.status_code}: {response.text[:300]}")


def main() -> int:
    client = TestClient(app)

    checks = [
        ("GET /", client.get("/")),
        ("GET /api/health", client.get("/api/health")),
        ("GET /api/config/platforms", client.get("/api/config/platforms")),
        ("GET /api/config/options", client.get("/api/config/options")),
        ("GET /api/crawler/status", client.get("/api/crawler/status")),
    ]

    for label, response in checks:
        assert_ok(response, label)
        print(f"{label}: OK")

    index = checks[0][1].text
    if "<!doctype html>" not in index.lower() and "<html" not in index.lower():
        raise AssertionError("GET / did not return the WebUI HTML page")
    print("WebUI HTML: OK")

    platforms = checks[2][1].json()["platforms"]
    required_platforms = {"xhs", "dy", "ks"}
    actual_platforms = {item["value"] for item in platforms}
    missing = required_platforms - actual_platforms
    if missing:
        raise AssertionError(f"Missing required platforms in WebUI config: {sorted(missing)}")
    print("Required platforms: OK")

    options = checks[3][1].json()
    save_options = {item["value"] for item in options["save_options"]}
    if "sqlite" not in save_options:
        raise AssertionError("SQLite is missing from WebUI save options")
    print("SQLite option: OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
