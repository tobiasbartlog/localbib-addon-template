"""HTTP routes of the Add-on Template, mounted under ``/api/plugins/template/``.

The core enforces this prefix at load time (``plugin_loader._check_prefix``) —
every route your Add-on registers must live under ``/api/plugins/<your id>/``.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter


def build_router(plugin: Any) -> APIRouter:
    router = APIRouter(prefix="/api/plugins/template")

    @router.get("/lookup/{citekey}")
    def lookup(citekey: str) -> dict:
        return plugin.lookup(citekey)

    return router
