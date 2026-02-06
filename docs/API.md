# DeepReader API

This document describes the current backend API for the DeepReader service.

## Base

- Base URL: `http://<host>:8000`
- Content-Type: `application/json`
- Error format (all non-2xx responses):
  - `{"status": "error", "code": "...", "message": "..."}`
  - Common codes:
    - `INVALID_PARAMS` (400/422)
    - `HTTP_ERROR` (4xx)
    - `INTERNAL_ERROR` (500)

## Health

### GET /

Response:
```
{"status": "ok", "message": "DeepReader API is running"}
```

## Papers

### GET /api/papers

Query parameters:
- `limit` (int, default 20)
- `offset` (int, default 0)
- `topic` (string, optional)
- `start_date` (string, optional, `YYYY-MM-DD`)
- `end_date` (string, optional, `YYYY-MM-DD`)

Topic search behavior:
- If SQLite FTS5 is available, the backend uses full-text search for `topic`.
- If FTS5 is unavailable, it falls back to `LIKE` matching across title/summary/category fields.

Response:
```
{
  "items": ["Paper"],
  "total": 120,
  "limit": 20,
  "offset": 0
}
```

Pagination guidance:
- The client should compute current range as `offset + 1` to `min(offset + limit, total)`.
- When `offset + limit >= total`, there are no more pages.

### GET /api/papers/{paper_id}

Response:
```
{"Paper"}
```

Error example (not found):
```
{"status": "error", "code": "HTTP_ERROR", "message": "Paper not found"}
```

## Jobs

### POST /api/trigger

Start a fetch/summarize job. Returns a `job_id` used for polling.

Request body:
- `query` (string, optional) Custom search query. If provided, it overrides other fetch params.
- `category` (string, required when `query` is not provided)
- `days` (int, optional) Mutually exclusive with `start_date/end_date`.
- `start_date` (string, optional, `YYYY-MM-DD`)
- `end_date` (string, optional, `YYYY-MM-DD`)
- `topic` (string, optional)
- `max_results` (int, default 200)

Validation:
- `category` is required when `query` is not provided.
- `days` cannot be used together with `start_date` or `end_date`.
- `start_date` and `end_date` must be provided together.

Response:
```
{
  "status": "accepted",
  "job_id": "<job_id>",
  "message": "Fetch job triggered for category: ..."
}
```

Error example (invalid params):
```
{"status": "error", "code": "INVALID_PARAMS", "message": "days is mutually exclusive with start_date/end_date."}
```

### GET /api/jobs/{job_id}

Response:
```
{
  "job_id": "<job_id>",
  "status": "pending|running|completed|failed",
  "total": 200,
  "processed": 45,
  "new": 12,
  "error": null,
  "started_at": "2026-02-06T08:10:00+00:00",
  "finished_at": null
}
```

Status lifecycle:
- `pending`: accepted, not started
- `running`: fetching or processing
- `completed`: finished successfully
- `failed`: error, see `error`

## Stats

### GET /api/stats

Response:
```
{
  "total": 120,
  "last_fetch_time": "2026-02-06T08:10:00+00:00",
  "categories": {
    "cs.AI": 40,
    "cs.LG": 25
  },
  "with_summary": 90,
  "without_summary": 30
}
```

### GET /api/categories

Response:
```
{
  "categories": ["cs.AI", "cs.LG", "cs.CV"]
}
```

## Models

### Paper

Fields:
- `arxiv_id` (string)
- `title` (string)
- `authors` (string[])
- `summary` (string)
- `published_date` (datetime)
- `updated_date` (datetime)
- `primary_category` (string)
- `categories` (string[])
- `pdf_url` (string, optional)
- `llm_summary` (string, optional)
- `key_insights` (string, optional)
