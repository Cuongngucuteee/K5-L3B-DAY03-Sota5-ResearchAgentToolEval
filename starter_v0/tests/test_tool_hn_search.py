import io
import json
import socket
import urllib.error
from urllib.parse import parse_qs, urlparse

import pytest

from tools import TOOL_FUNCTIONS

hn_search_tool = TOOL_FUNCTIONS["hn_search"]


# ---------------- hn_search ----------------

class _FakeUrlResponse:
    """Giả lập object trả về của urlopen (dùng được với `with`)."""

    def __init__(self, payload) -> None:
        raw = payload if isinstance(payload, (bytes, str)) else json.dumps(payload)
        self._raw = raw.encode("utf-8") if isinstance(raw, str) else raw

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> bool:
        return False


def _patch_urlopen(monkeypatch, response=None, raises=None) -> list:
    """Thay urlopen bằng hàm giả, ghi lại mọi request để assert. Không bao giờ gọi mạng thật."""
    calls: list = []

    def fake_urlopen(req, timeout=None):
        calls.append({"url": req.full_url, "timeout": timeout})
        if raises is not None:
            raise raises
        return response

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    return calls


def test_hn_search_sort_date_uses_search_by_date_endpoint(monkeypatch) -> None:
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse({"hits": []}))

    result = hn_search_tool(query="llm", sort="date", limit=3)

    assert urlparse(calls[0]["url"]).path == "/api/v1/search_by_date"
    assert result["sort"] == "date"
    assert result["items"] == []


def test_hn_search_bad_limit_is_rejected_or_clamped(monkeypatch) -> None:
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse({"hits": []}))
    assert hn_search_tool(query="x", limit="abc")["error"] == "ValueError"
    assert calls == []

    hn_search_tool(query="x", limit=999)
    hn_search_tool(query="x", limit=0)
    sizes = [parse_qs(urlparse(c["url"]).query)["hitsPerPage"] for c in calls]
    assert sizes == [["20"], ["1"]]


def test_hn_search_empty_query_does_not_crash(monkeypatch) -> None:
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse({"hits": []}))

    result = hn_search_tool(query=None)

    assert "error" not in result
    assert parse_qs(urlparse(calls[0]["url"]).query, keep_blank_values=True)["query"] == [""]


def test_hn_search_http_error_returns_error_dict(monkeypatch) -> None:
    err = urllib.error.HTTPError(
        "https://hn.algolia.com/api/v1/search", 429, "Too Many Requests", {}, io.BytesIO(b"")
    )
    _patch_urlopen(monkeypatch, raises=err)

    result = hn_search_tool(query="x")

    assert result["error"] == "HTTPError"


def test_hn_search_timeout_returns_error_dict(monkeypatch) -> None:
    _patch_urlopen(monkeypatch, raises=socket.timeout("timed out"))

    result = hn_search_tool(query="x")

    assert "error" in result
    assert "timed out" in result["message"]


def test_hn_search_invalid_json_returns_error_dict(monkeypatch) -> None:
    _patch_urlopen(monkeypatch, response=_FakeUrlResponse("<html>502 Bad Gateway</html>"))

    result = hn_search_tool(query="x")

    assert result["error"] == "JSONDecodeError"
    
# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise


def test_my_new_tool_happy_path(monkeypatch) -> None:
    payload = {"hits": [
        {
            "objectID": "111", "title": "Show HN: Tiny agent", "url": "https://www.example.com/agent",
            "points": 250, "num_comments": 40, "author": "alice",
        },
        {
            "objectID": "222", "title": "Ask HN: Best RAG setup?", "url": None,
            "story_text": "<p>I use <b>BM25</b> &amp; embeddings.</p>",
            "points": 10, "num_comments": 5, "author": "bob",
        },
    ]}
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse(payload))

    result = hn_search_tool(query="agent", sort="relevance", limit=2)

    assert len(calls) == 1
    parsed = urlparse(calls[0]["url"])
    qs = parse_qs(parsed.query)
    assert parsed.netloc == "hn.algolia.com"
    assert parsed.path == "/api/v1/search"
    assert qs["query"] == ["agent"]
    assert qs["tags"] == ["story"]
    assert qs["hitsPerPage"] == ["2"]
    assert calls[0]["timeout"] is not None

    assert result["tool"] == "hn_search"
    assert result["query"] == "agent"
    assert result["sort"] == "relevance"
    assert len(result["items"]) == 2

    first, second = result["items"]
    assert first["title"] == "Show HN: Tiny agent"
    assert first["url"] == "https://www.example.com/agent"
    assert first["source"] == "www.example.com"
    assert first["score"] == 250
    assert first["hn_id"] == "111"
    assert first["hn_url"] == "https://news.ycombinator.com/item?id=111"
    assert "250 points by alice, 40 comments" in first["summary"]

    assert second["url"] == "https://news.ycombinator.com/item?id=222"
    assert second["source"] == "news.ycombinator.com"
    assert second["summary"] == "I use BM25 & embeddings."

def test_my_new_tool_bad_input_from_model(monkeypatch) -> None:
    # Test out-of-enum value for sort and wrong type for limit
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse({"hits": []}))
    
    # 1. Bad sort option returns error dict without network call
    res_sort = hn_search_tool(query="test", sort="invalid_sort")
    assert res_sort["error"] == "ValueError"
    assert "sort" in res_sort["message"]
    
    # 2. Bad limit option (non-integer string) returns error dict
    res_limit = hn_search_tool(query="test", limit="not-an-int")
    assert res_limit["error"] == "ValueError"
    assert "limit" in res_limit["message"]
    
    assert calls == []


def test_my_new_tool_failure_returns_error_dict(monkeypatch) -> None:
    _patch_urlopen(monkeypatch, raises=socket.timeout("connection timed out"))
    
    result = hn_search_tool(query="test")
    
    assert isinstance(result, dict)
    assert result["error"] == "TimeoutError"
    assert "timed out" in result["message"]    