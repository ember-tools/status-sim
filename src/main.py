"""Entry point of the Status Sim server."""

import asyncio
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import router
from frontend import frontend_directory, mount_frontend
from logging_conf import setup_logging
from manager import manager

setup_logging()

CLEANUP_INTERVAL = 60
DEFAULT_CORS_ORIGINS = "https://statussim.emberbox.app"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Restore the exercises from Redis when configured, and tidy them up while the server runs."""
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        await manager.init_redis(redis_url)

    tasks = [asyncio.create_task(cleanup_task())]

    if os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes"):
        from demo import run_demo

        tasks.append(asyncio.create_task(run_demo()))

    yield

    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await manager.close()


async def cleanup_task():
    """Once a minute, drop connections nobody has polled for a while and exercises nobody has accessed for seven days."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        await manager.cleanup_inactive()
        await manager.expire_stale()


def cors_origins() -> list[str]:
    """The origins allowed to call the API from another site, comma separated in `CORS_ORIGINS`."""
    configured = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


def build_app() -> FastAPI:
    """Build the application with its routes, CORS policy, scenario files and the built frontend."""
    application = FastAPI(title="Status Sim", lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    application.mount("/static", StaticFiles(directory=static_dir), name="static")
    application.include_router(router)
    mount_frontend(application, frontend_directory())
    return application


app = build_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
