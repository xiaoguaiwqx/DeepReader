from fastapi.testclient import TestClient
from unittest.mock import patch

from deep_reader.server.app import app


client = TestClient(app)


def test_trigger_rejects_days_with_date_range():
    response = client.post(
        "/api/trigger",
        json={
            "days": 3,
            "start_date": "2026-02-01",
            "end_date": "2026-02-05",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "INVALID_PARAMS"


def test_trigger_rejects_partial_date_range():
    response = client.post(
        "/api/trigger",
        json={
            "start_date": "2026-02-01",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "INVALID_PARAMS"


def test_trigger_requires_category_when_query_missing():
    response = client.post(
        "/api/trigger",
        json={
            "days": 2,
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "INVALID_PARAMS"


def test_trigger_passes_max_results():
    with patch("deep_reader.server.app.run_daily_cycle") as mock_run:
        response = client.post(
            "/api/trigger",
            json={
                "query": "cat:cs.AI",
                "max_results": 7,
            },
        )

    assert response.status_code == 200
    _, kwargs = mock_run.call_args
    assert kwargs["max_results"] == 7


def test_get_stats():
    fake_stats = {
        "total": 10,
        "last_fetch_time": "2026-02-06T08:10:00+00:00",
        "categories": {"cs.AI": 6, "cs.LG": 4},
        "with_summary": 8,
        "without_summary": 2,
    }

    with patch("deep_reader.server.app.db_manager.get_stats", return_value=fake_stats):
        response = client.get("/api/stats")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 10
    assert data["categories"]["cs.AI"] == 6


def test_get_categories():
    fake_categories = ["cs.AI", "cs.LG", "cs.CV"]

    with patch("deep_reader.server.app.db_manager.get_categories", return_value=fake_categories):
        response = client.get("/api/categories")

    assert response.status_code == 200
    data = response.json()
    assert data["categories"] == fake_categories
