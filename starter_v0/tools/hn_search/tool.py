from __future__ import annotations

from typing import Any

from tools._shared import err


# SCAFFOLD (Lead, Buoc 0): signature below is FROZEN. Owner C fills the body only.
# Do not rename the function or its parameters (tools.yaml + contract test depend on them).
def search_hacker_news(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    try:
        # TODO (C): call Algolia HN API (https://hn.algolia.com/api/v1/search or search_by_date),
        # return {"tool": "hn_search", "query": query, "sort": sort, "items": [...]}
        # items: title, url, source, summary, score (points), plus hn id/url.
        raise NotImplementedError("hn_search is not implemented yet")
    except Exception as exc:
        return err("hn_search", exc)
