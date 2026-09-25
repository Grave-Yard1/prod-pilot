from collections.abc import Iterator

from sqlalchemy.orm import Session


def get_session() -> Iterator[Session]:
    raise RuntimeError("Database session is not configured")
    yield  # pragma: no cover
