from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db, make_engine, make_session_factory, session_scope
from app.deps import get_session
from app.routers import handoff, incidents, machines

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def create_app() -> FastAPI:
    engine = make_engine()
    init_db(engine)
    factory = make_session_factory(engine)
    app = FastAPI(title="Linewalk", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def bind_session():
        yield from session_scope(factory)

    app.dependency_overrides[get_session] = bind_session
    app.include_router(machines.router, prefix="/api/machines", tags=["machines"])
    app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
    app.include_router(handoff.router, prefix="/api/handoff", tags=["handoff"])

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True, "dataset": "berlin-style-simulated"}

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
    else:

        @app.get("/")
        def root() -> dict:
            return {
                "service": "linewalk",
                "dataset": "berlin-style-simulated",
                "ui": "http://127.0.0.1:8742",
            }

    return app


app = create_app()
