"""Serving the built frontend: prerendered public pages, built files and the single-page shell."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

RESERVED_PREFIXES = ("api", "static")
PAGES = "pages"
SHELL_HEADERS = {"X-Robots-Tag": "noindex, nofollow"}

_SOURCE = Path(__file__).resolve().parent


def frontend_directory() -> Path:
    """Locate the built frontend.

    `FRONTEND_DIR` names it explicitly. Otherwise the image's copy in `src/frontend_dist` is used,
    and in a checkout the Vite output in `frontend/dist`.
    """
    configured = os.getenv("FRONTEND_DIR")
    if configured:
        return Path(configured)
    bundled = _SOURCE / "frontend_dist"
    return bundled if bundled.is_dir() else _SOURCE.parent / "frontend" / "dist"


def mount_frontend(app: FastAPI, directory: Path) -> None:
    """Serve the built frontend for every path outside the API and the scenario files.

    Paths under those prefixes are never answered with HTML, so a mistyped API call fails as a 404.
    Everything else is answered by `frontend_response`.
    """

    @app.get("/{path:path}", include_in_schema=False)
    async def frontend(path: str) -> FileResponse:
        if is_reserved(path):
            raise HTTPException(status_code=404)
        return frontend_response(directory, path)


def frontend_response(directory: Path, path: str) -> FileResponse:
    """Resolve a path to a prerendered page, a built file or the single-page shell.

    A prerendered page (`/`, `/hilfe` and the help topics below it) comes from `pages/<path>/index.html`. A built file is
    served as it is, except the shell itself and the prerendered pages under their file names, so
    each page has one address. `build.json` is never cached, so open pages notice a new build. A
    missing file under `assets/` is a 404 rather than the shell, so a page still running an older
    build sees its chunk fail to load instead of receiving HTML. Every other path gets the shell.
    Paths are resolved before they are checked, so dot segments cannot reach around these rules.
    """
    root = directory.resolve()
    pages = root / PAGES
    page = (pages / path.strip("/") / "index.html").resolve()
    if page.is_relative_to(pages) and page.is_file():
        return FileResponse(page)
    candidate = (root / path.strip("/")).resolve()
    if candidate.is_relative_to(root) and candidate != root and candidate.is_file():
        relative = candidate.relative_to(root)
        if relative != Path("index.html") and relative.parts[0] != PAGES:
            headers = {"Cache-Control": "no-store"} if relative == Path("build.json") else None
            return FileResponse(candidate, headers=headers)
    if path.strip("/").split("/", 1)[0] == "assets":
        raise HTTPException(status_code=404)
    return shell_response(root)


def shell_response(directory: Path) -> FileResponse:
    """Answer with the single-page shell, which search engines are told not to index.

    Its content depends on an exercise code; only the prerendered pages are meant for search
    engines. Without a built frontend the answer is a 404.
    """
    shell = directory / "index.html"
    if not shell.is_file():
        raise HTTPException(status_code=404, detail="Frontend not built")
    return FileResponse(shell, headers=SHELL_HEADERS)


def is_reserved(path: str) -> bool:
    """Tell whether a path belongs to the API or the scenario files."""
    return path.split("/", 1)[0] in RESERVED_PREFIXES
