from datetime import datetime

import pytest

from app.domain.models import Post, User
from app.services.posts import (
    MAX_CONTENT_LENGTH,
    InvalidPostContent,
    UserNotFound,
    create_post,
)


class InMemoryPostRepository:
    def __init__(self, users: list[User]) -> None:
        self.users = {u.id: u for u in users}
        self.posts: list[Post] = []

    def get_user(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def add_post(self, post: Post) -> Post:
        saved = post.model_copy(
            update={"id": len(self.posts) + 1, "created_at": datetime.now()}
        )
        self.posts.append(saved)
        return saved


@pytest.fixture
def repo() -> InMemoryPostRepository:
    return InMemoryPostRepository([User(id=1, username="alice")])


def test_create_post_returns_saved_post(repo):
    post = create_post(repo, user_id=1, content="  hello world  ")

    assert post.id == 1
    assert post.user_id == 1
    assert post.content == "hello world"
    assert post.created_at is not None
    assert repo.posts == [post]


@pytest.mark.parametrize("content", ["", "   ", "x" * (MAX_CONTENT_LENGTH + 1)])
def test_create_post_rejects_invalid_content(repo, content):
    with pytest.raises(InvalidPostContent):
        create_post(repo, user_id=1, content=content)
    assert repo.posts == []


def test_create_post_rejects_unknown_user(repo):
    with pytest.raises(UserNotFound):
        create_post(repo, user_id=42, content="hello")
    assert repo.posts == []
