from __future__ import annotations

import html
import json
import re
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse

# SCAFFOLD (Lead, Buoc 0): signature below is FROZEN. Owner C fills the body only.
# Do not rename the function or its parameters (tools.yaml + contract test depend on them).
def search_hacker_news(
    query: str | None = None,
    sort: str = "relevance",
    limit: int = 10,
) -> dict:
    """Search Hacker News via Algolia API."""

    if sort not in ("relevance", "date"):
        return {
            "error": "ValueError",
            "message": f"Invalid sort parameter '{sort}'. Must be 'relevance' or 'date'."
        }


    try:
        limit_val = int(limit)
    except (TypeError, ValueError):
        return {
            "error": "ValueError",
            "message": f"Invalid limit parameter '{limit}'. Must be an integer."
        }
    
    clamped_limit = max(1, min(20, limit_val))


    q_str = query if query is not None else ""


    endpoint = (
        "https://hn.algolia.com/api/v1/search_by_date"
        if sort == "date"
        else "https://hn.algolia.com/api/v1/search"
    )
    
    url = f"{endpoint}?query={urllib.parse.quote(q_str)}&tags=story&hitsPerPage={clamped_limit}"

    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ResearchAgent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": "HTTPError", "message": str(e)}
    except (socket.timeout, TimeoutError) as e:
        return {"error": "TimeoutError", "message": f"Request timed out: {e}"}
    except json.JSONDecodeError as e:
        return {"error": "JSONDecodeError", "message": str(e)}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


    items = []
    for hit in data.get("hits", []):
        object_id = hit.get("objectID")
        hn_url = f"https://news.ycombinator.com/item?id={object_id}" if object_id else ""
        raw_url = hit.get("url")
        
        item_url = raw_url if raw_url else hn_url
        parsed_url = urlparse(item_url)
        source = parsed_url.netloc if parsed_url.netloc else "news.ycombinator.com"

        points = hit.get("points", 0)
        author = hit.get("author", "unknown")
        num_comments = hit.get("num_comments", 0)


        story_text = hit.get("story_text")
        if story_text:
            clean_text = re.sub(r"<[^>]*>", "", story_text)
            summary = html.unescape(clean_text)
        else:
            summary = f"{points} points by {author}, {num_comments} comments"

        items.append({
            "title": hit.get("title", ""),
            "url": item_url,
            "source": source,
            "score": points,
            "hn_id": object_id,
            "hn_url": hn_url,
            "summary": summary,
        })

    return {
        "tool": "hn_search",
        "query": q_str,
        "sort": sort,
        "items": items,
    }