from fastapi.testclient import TestClient

from api import main


def test_kuaishou_dashboard_page_is_available():
    response = TestClient(main.app).get("/static/kuaishou-dashboard.html")

    assert response.status_code == 200
    assert "快手 AI 漫剧数据看板" in response.text


def test_dashboard_frontend_uses_mysql_api():
    response = TestClient(main.app).get("/static/dashboard.js")

    assert response.status_code == 200
    assert "/api/dashboard/kuaishou" in response.text
    assert "/api/kuaishou/dashboard-data" not in response.text


def test_legacy_json_dashboard_endpoint_is_not_exposed():
    response = TestClient(main.app).get("/api/kuaishou/dashboard-data")

    assert response.status_code == 404
