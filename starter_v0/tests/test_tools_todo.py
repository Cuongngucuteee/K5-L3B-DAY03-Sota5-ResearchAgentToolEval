"""CP3 — Tool Unit Test Challenge (đã hoàn thành).

Mọi test chạy offline: HTTP được mock bằng `fake_http`, key giả đặt bằng `monkeypatch.setenv`.
Mỗi test kiểm tra một hành vi và đặt tên theo hành vi đó.
"""
from __future__ import annotations

import socket

from conftest import FakeResponse
from test_tool_hn_search import _FakeUrlResponse, _patch_urlopen
from tools import TOOL_FUNCTIONS

clarify_tool = TOOL_FUNCTIONS["clarify"]
format_tool = TOOL_FUNCTIONS["format"]
send_tool = TOOL_FUNCTIONS["send"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
fetch_tool = TOOL_FUNCTIONS["fetch"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
policy_tool = TOOL_FUNCTIONS["policy"]
hn_search_tool = TOOL_FUNCTIONS["hn_search"]


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = clarify_tool(question="Chọn nền tảng?", response_type="choice", options=["X", "Hacker News"])

    assert result["options"] == ["X", "Hacker News"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "section": "A"},
        {"title": "b1", "section": "B"},
        {"title": "a2", "section": "A"},
    ]
    markdown = format_tool(items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [{"title": "một"}, {"title": "hai"}]
    markdown = format_tool(items=items, template="thread")["markdown"]
    lines = [line for line in markdown.splitlines() if line.strip()]

    assert lines[0].startswith("1/")
    assert lines[1].startswith("2/")


def test_format_empty_items_does_not_crash() -> None:
    assert format_tool(items=None)["item_count"] == 0
    assert format_tool(items=[])["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Xin chào nhóm", confirmed=True)

    assert result["status"] == "sent"
    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "fake-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "12345"
    assert calls[0]["json"]["text"] == "Xin chào nhóm"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = send_tool(text="Xin chào", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "fake-key")
    calls = fake_http(FakeResponse({"results": []}))

    lookup_tool(query="llm", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "llm"


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-key")
    fake_http(FakeResponse({"data": {
        "markdown": "# Nội dung trang",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/page"},
    }}))

    item = fetch_tool(url="https://www.example.com/page")["items"][0]

    assert item["title"] == "T"
    assert item["url"] == "https://www.example.com/page"
    assert item["source"] == "example.com"
    assert item["summary"] == "# Nội dung trang"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fake-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 9000, "metadata": {}}}))

    item = fetch_tool(url="https://example.com")["items"][0]

    assert len(item["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "fake-key")
    raw = [{"screen_name": "sama", "text": "không có id"}]
    raw += [{"screen_name": "sama", "tweet_id": str(i), "text": f"tweet {i}"} for i in range(1, 7)]
    fake_http(FakeResponse({"timeline": raw}))

    items = timeline_tool(screenname="sama", limit=3)["items"]

    assert len(items) == 3
    assert all(item["url"].startswith("https://x.com/sama/status/") for item in items)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "fake-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    social_search_tool(query="passkey", search_type="Top")

    assert calls[0]["params"]["query"] == "passkey"
    assert calls[0]["params"]["search_type"] == "Top"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert policy_tool(query="")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = policy_tool(query="data privacy personal", policy_area="data_privacy")["results"]

    assert results
    assert all(hit["policy_area"] == "data_privacy" for hit in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = policy_tool(query="injection probe citation", policy_area="source_citation")["results"]
    hits = [hit for hit in results if hit["section"] == "Injection probe"]

    assert hits
    assert any("ignore the citation policy" in line for line in hits[0]["untrusted_text"])
    assert "ignore the citation policy" not in hits[0]["facts"]


# ---------------- tool mới: hn_search ----------------

def test_my_new_tool_happy_path(monkeypatch) -> None:
    payload = {"hits": [{"objectID": "42", "title": "Post", "url": "https://example.com/x",
                         "points": 10, "num_comments": 2, "author": "tester"}]}
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse(payload))

    result = hn_search_tool(query="sqlite", sort="date", limit=3)

    assert result["tool"] == "hn_search"
    assert result["items"][0]["title"] == "Post"
    assert result["items"][0]["hn_url"].endswith("id=42")
    assert "search_by_date" in calls[0]["url"]
    assert "hitsPerPage=3" in calls[0]["url"]


def test_my_new_tool_bad_input_from_model(monkeypatch) -> None:
    calls = _patch_urlopen(monkeypatch, response=_FakeUrlResponse({"hits": []}))

    assert hn_search_tool(query="x", sort="top")["error"] == "ValueError"
    assert hn_search_tool(query="x", limit="abc")["error"] == "ValueError"
    assert calls == []


def test_my_new_tool_failure_returns_error_dict(monkeypatch) -> None:
    _patch_urlopen(monkeypatch, raises=socket.timeout("timed out"))

    result = hn_search_tool(query="x")

    assert result["error"] == "TimeoutError"
