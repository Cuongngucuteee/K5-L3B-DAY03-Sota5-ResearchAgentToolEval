---
name: hn_search
track: core
kind: live_api
provider: Hacker News (Algolia API)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hn_search

Searches Hacker News stories via the public Algolia API (no API key).
`sort` is `relevance` or `date`. `limit` caps the number of stories.

(Scaffold: owner C completes the implementation and these notes.)
