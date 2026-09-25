import os
from collections.abc import Iterator
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base, MachineRecord

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "linewalk.db"


def database_url() -> str:
    return os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_PATH}")


def make_engine() -> Engine:
    url = database_url()
    if url.startswith("sqlite"):
        path = url.removeprefix("sqlite:///")
        if path and path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db(engine: Engine) -> None:
    from app.seed import seed

    Base.metadata.create_all(engine)
    factory = make_session_factory(engine)
    with factory() as session:
        existing = session.scalar(select(func.count()).select_from(MachineRecord))
        if not existing:
            seed(session)
            session.commit()


def session_scope(factory: sessionmaker[Session]) -> Iterator[Session]:
    session = factory()
    try:
        yield session
    finally:
        session.close()
