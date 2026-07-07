"""Shared fixtures for Issue-Finder tests."""

from __future__ import annotations

import time
from unittest import mock

import pytest
import requests


class MockResponse:
    """Build a mock requests.Response with the shape the code expects."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: dict | None = None,
        headers: dict[str, str] | None = None,
        text: str = "",
    ):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._json_data or {}


def make_search_result(
    total_count: int = 0,
    issue_ids: list[int] | None = None,
) -> dict:
    """Build a GitHub Search API result body."""
    items = []
    for iid in (issue_ids or []):
        items.append(
            {
                "id": iid,
                "title": f"Issue {iid}",
                "html_url": f"https://github.com/owner/repo/issues/{iid}",
                "repository_url": "https://api.github.com/repos/owner/repo",
                "score": 1.0,
            }
        )
    return {"total_count": total_count, "items": items, "incomplete_results": False}


@pytest.fixture
def success_response():
    """Return a MockResponse configured for a successful 200."""
    return MockResponse(
        status_code=200,
        json_data=make_search_result(),
        headers={
            "X-RateLimit-Remaining": "30",
            "X-RateLimit-Reset": str(int(time.time()) + 3600),
        },
    )


@pytest.fixture
def mock_requests(success_response):
    """Replace requests.get with a mock returning the success_response by default."""
    with mock.patch.object(requests, "get") as mg:
        mg.return_value = success_response
        yield mg


@pytest.fixture
def mock_sleep():
    """Replace time.sleep with a no-op so tests don't actually wait."""
    with mock.patch("time.sleep"):
        yield


@pytest.fixture
def empty_env(monkeypatch):
    """Remove GITHUB_TOKEN so the unauthenticated path is exercised."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
