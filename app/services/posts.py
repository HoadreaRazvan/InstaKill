"""Application service for publishing posts.

Coordinates the rules around creating a Post for an existing User. It knows nothing
about HTTP or SQLite: storage is reached through the PostRepository protocol, and
failures are reported as service exceptions that the API layer maps to status codes.
"""
from typing import Protocol

from app.domain.models import Post, User

MAX_CONTENT_LENGTH = 500


class PostRepository(Protocol):
    """Storage operations the service needs. Implemented later on top of SQLite."""

    def get_user(self, user_id: int) -> User | None: ...

    def add_post(self, post: Post) -> Post:
        """Persist the post and return it with `id` and `created_at` filled in."""
        ...


class PostServiceError(Exception):
    """Base class for expected, user-facing failures of the post service."""


class InvalidPostContent(PostServiceError):
    pass


class UserNotFound(PostServiceError):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"user {user_id} does not exist")
        self.user_id = user_id


def create_post(repo: PostRepository, user_id: int, content: str) -> Post:
    """Validate and publish a new post on behalf of `user_id`.

    Raises InvalidPostContent if the content is blank or longer than
    MAX_CONTENT_LENGTH characters, and UserNotFound if the author does not exist.
    """
    content = content.strip()
    if not content:
        raise InvalidPostContent("content must not be empty")
    if len(content) > MAX_CONTENT_LENGTH:
        raise InvalidPostContent(
            f"content must be at most {MAX_CONTENT_LENGTH} characters"
        )

    if repo.get_user(user_id) is None:
        raise UserNotFound(user_id)

    return repo.add_post(Post(user_id=user_id, content=content))
