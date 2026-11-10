"""template — the LocalBib Add-on Template (Add-on Contract 2).

A Bundle in miniature, meant to be cloned and renamed: ``plugin.json`` at the
Bundle root, this package under the Add-on id, ``frontend/`` with one script,
one stylesheet and two locales. It imports only from ``plugin_api`` (and,
lazily, FastAPI for its router), so its own tests run with the Add-on
Contract package and its fakes alone — no LocalBib core required. See
``README.md`` for the step-by-step guide to turning this into your own
Add-on.

Declares only ``library.read``: a Berechtigung the core actually wires today
(``llm``, ``settings.core`` and, since 2.7, ``storage`` exist in the
contract too; ``files`` is reserved and grants nothing yet — see
``AUTHORING.md``. This template keeps its one demo minimal: view counts
live in the instance, not in a store).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from plugin_api import PluginApi, load_manifest

BUNDLE_ROOT = Path(__file__).resolve().parent.parent


class TemplatePlugin:
    """One endpoint, one view, one Slot — replace the pieces you don't need."""

    manifest = load_manifest(BUNDLE_ROOT)

    def __init__(self) -> None:
        self._api: Optional[PluginApi] = None
        self._views: dict[str, int] = {}

    async def activate(self, api: PluginApi) -> None:
        self._api = api
        if self.manifest.nav is not None:
            api.ui.register_nav_item(self.manifest.nav)
        router = _build_router(self)
        if router is not None:
            api.routes.register_router(router)

    async def deactivate(self) -> None:
        self._api = None
        self._views.clear()

    # --- behaviour -----------------------------------------------------
    def lookup(self, citekey: str) -> dict:
        """The Add-on's one endpoint: an Item's title, a configurable greeting
        (demonstrates ``library`` and the plugin's own ``settings``) and how
        often this citekey was looked up this session."""
        api = self._require_api()
        ref = api.library.get_reference(citekey) if api.library is not None else None
        title = (ref or {}).get("title") or citekey
        greeting = (api.settings.get("greeting") if api.settings else None) or "Hello"
        self._views[citekey] = self._views.get(citekey, 0) + 1
        return {"citekey": citekey, "title": title, "greeting": greeting, "views": self._views[citekey]}

    def _require_api(self) -> PluginApi:
        if self._api is None:
            raise RuntimeError("template is not active")
        return self._api


def _build_router(plugin: "TemplatePlugin") -> Any:
    try:
        from .api import build_router
    except ModuleNotFoundError as exc:
        if exc.name != "fastapi":
            raise
        return None  # contract-only test run: no web framework installed
    return build_router(plugin)


plugin = TemplatePlugin()
