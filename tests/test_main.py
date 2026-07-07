"""Tests for the Issue-Finder GitHub API crawler."""

from __future__ import annotations

import time
import unittest.mock

import pytest
import requests

from main import fetch_page, wait_for_rate_limit, crawl_github_algorithm_issues

from tests.conftest import MockResponse, make_search_result


# ---------------------------------------------------------------------------
# wait_for_rate_limit
# ---------------------------------------------------------------------------

class TestWaitForRateLimit:
    def test_uses_reset_ts(self, mock_sleep):
        """Sleeps until X-RateLimit-Reset when the header is present."""
        future = int(time.time()) + 30
        resp = MockResponse(headers={"X-RateLimit-Reset": str(future)})
        wait_for_rate_limit(resp)
        # 30s remaining + 2 buffer = 32
        time.sleep.assert_any_call(32)  # type: ignore[attr-defined]

    def test_fallback_60s(self, mock_sleep):
        """Sleeps 60s when no rate-limit headers exist."""
        resp = MockResponse(headers={})
        wait_for_rate_limit(resp)
        time.sleep.assert_any_call(60)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# fetch_page
# ---------------------------------------------------------------------------

class TestFetchPage:
    def test_success_returns_response(self, mock_sleep):
        """200 returns the response immediately."""
        resp = MockResponse(
            status_code=200,
            json_data=make_search_result(total_count=1, issue_ids=[42]),
        )
        with unittest.mock.patch.object(requests, "get", return_value=resp):
            result = fetch_page("https://api.github.com/search/issues", {}, {"q": "test"})
        assert result is resp

    def test_403_calls_wait_and_retries(self, mock_sleep):
        """403 triggers wait_for_rate_limit then retries."""
        ok_resp = MockResponse(status_code=200, json_data=make_search_result())
        rate_limited = MockResponse(status_code=403, headers={"X-RateLimit-Reset": str(int(time.time()) + 60)})
        with unittest.mock.patch.object(requests, "get", side_effect=[rate_limited, ok_resp]):
            result = fetch_page("https://api.github.com/search/issues", {}, {"q": "test"})
        assert result is ok_resp

    def test_422_returns_none(self, mock_sleep):
        """422 (query rejected) returns None without retrying."""
        with unittest.mock.patch.object(requests, "get", return_value=MockResponse(status_code=422)):
            result = fetch_page("https://api.github.com/search/issues", {}, {"q": "test"})
        assert result is None

    def test_unexpected_status_returns_none(self, mock_sleep):
        """Non-200/403/422 returns None."""
        with unittest.mock.patch.object(requests, "get", return_value=MockResponse(status_code=500)):
            result = fetch_page("https://api.github.com/search/issues", {}, {"q": "test"})
        assert result is None

    def test_timeout_retries(self, mock_sleep):
        """requests.exceptions.Timeout is caught and retried."""
        ok_resp = MockResponse(status_code=200, json_data=make_search_result())
        side_effects = [requests.exceptions.Timeout("timed out"), ok_resp]
        with unittest.mock.patch.object(requests, "get", side_effect=side_effects):
            result = fetch_page("https://api.github.com/search/issues", {}, {"q": "test"})
        assert result is ok_resp

    def test_max_retries_exceeded(self, mock_sleep):
        """Returns None after exhausting all retries."""
        with unittest.mock.patch.object(
            requests, "get", side_effect=requests.exceptions.ConnectionError("down")
        ):
            result = fetch_page("https://api.github.com/search/issues", {}, {"q": "test"}, retries=2)
        assert result is None


# ---------------------------------------------------------------------------
# crawl_github_algorithm_issues (integration-light)
# ---------------------------------------------------------------------------

class TestCrawl:
    def test_produces_output_file(self, tmp_path, monkeypatch, mock_sleep):
        """Writes results.md with expected headers."""
        import main as m
        monkeypatch.setattr(m, "OUTPUT_FILE", str(tmp_path / "results.md"))

        resp = MockResponse(
            status_code=200,
            json_data=make_search_result(total_count=1, issue_ids=[1001]),
        )
        with unittest.mock.patch.object(requests, "get", return_value=resp):
            crawl_github_algorithm_issues()

        content = (tmp_path / "results.md").read_text(encoding="utf-8")
        assert "GitHub Algorithm & Architecture Issues" in content
        assert "Issue 1001" in content
