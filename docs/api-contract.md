# API contract — `POST /posts`

> **Status: contract only, not implemented.** This documents the endpoint that will sit on top of
> `app.services.posts.create_post`. The HTTP layer will only parse the request, call the service,
> and map service exceptions to the responses below.

Creates a new post on behalf of an existing user.

## Request

```http
POST /posts
Content-Type: application/json
```

```json
{
  "user_id": 1,
  "content": "hello world, this is my first post"
}
```

| Field | Type | Required | Rules |
|---|---|---|---|
| `user_id` | integer | yes | Must reference an existing user. |
| `content` | string | yes | Leading/trailing whitespace is trimmed. After trimming: 1–500 characters. |

Unknown extra fields are ignored.

## Successful response

`201 Created` — the stored post (the `Post` domain model), with `id` and `created_at` assigned by the server.

```json
{
  "id": 7,
  "user_id": 1,
  "content": "hello world, this is my first post",
  "created_at": "2026-10-19T19:30:00"
}
```

## Errors

All errors use FastAPI's standard `{"detail": ...}` body.

| Status | When | Source | Example body |
|---|---|---|---|
| `422 Unprocessable Entity` | Body is not valid JSON, a field is missing, or has the wrong type (e.g. `"user_id": "abc"`). | Request validation (Pydantic) | FastAPI's default list of validation errors |
| `422 Unprocessable Entity` | `content` is empty or only whitespace. | `InvalidPostContent` | `{"detail": "content must not be empty"}` |
| `422 Unprocessable Entity` | `content` is longer than 500 characters after trimming. | `InvalidPostContent` | `{"detail": "content must be at most 500 characters"}` |
| `404 Not Found` | No user with the given `user_id`. | `UserNotFound` | `{"detail": "user 42 does not exist"}` |

Checks run in this order: request shape → content → user existence. A request that fails several
checks gets the first matching error.

## Out of scope

Authentication (the author is taken from `user_id` in the body for now), images/attachments,
editing or deleting posts, and any feed/ranking side effects.
