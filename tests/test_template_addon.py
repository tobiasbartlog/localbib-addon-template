"""Tests of the Add-on Template — run only against plugin_api and its fakes.

The Bundle root goes on ``sys.path`` the way the core loader will put it
there, so ``import template`` resolves to the package next to ``plugin.json``.
Mirrors the Add-on Contract's own fixture Add-on (``plugin_api/tests/fixtures/hello``).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

BUNDLE_ROOT = Path(__file__).resolve().parent.parent
if str(BUNDLE_ROOT) not in sys.path:
    sys.path.insert(0, str(BUNDLE_ROOT))

import template  # noqa: E402

from plugin_api import LocalBibPlugin, Permission  # noqa: E402
from plugin_api.testing import InMemoryLibrary, make_api  # noqa: E402

REFS = [{"citekey": "doe2024", "title": "Deep Things"}]


@pytest.fixture
def plugin():
    p = template.TemplatePlugin()
    yield p
    asyncio.run(p.deactivate())


def test_module_exposes_a_plugin_with_the_bundle_manifest():
    assert isinstance(template.plugin, LocalBibPlugin)
    m = template.plugin.manifest
    assert (m.id, m.version, m.api_version) == ("template", "0.1.0", 2)
    assert m.declares("library.read") and not m.declares(Permission.NETWORK)


def test_activate_registers_nav_item_and_counts_views(plugin):
    api = make_api(plugin.manifest.permissions, library=InMemoryLibrary(REFS))
    asyncio.run(plugin.activate(api))

    assert [n.route for n in api.ui.nav_items] == ["/template"]
    result = plugin.lookup("doe2024")
    assert (result["title"], result["greeting"], result["views"]) == ("Deep Things", "Hello", 1)
    assert plugin.lookup("doe2024")["views"] == 2
    assert plugin.lookup("x2020")["views"] == 1  # counted per citekey


def test_undeclared_library_falls_back_to_the_citekey_as_title(plugin):
    api = make_api([])
    asyncio.run(plugin.activate(api))
    assert api.library is None
    assert plugin.lookup("doe2024")["title"] == "doe2024"


def test_own_setting_overrides_the_greeting(plugin):
    api = make_api([], settings={"greeting": "Ahoy"})
    asyncio.run(plugin.activate(api))
    assert plugin.lookup("x2020")["greeting"] == "Ahoy"


def test_deactivate_forgets_the_api_and_the_view_counts(plugin):
    asyncio.run(plugin.activate(make_api(["library.read"], library=InMemoryLibrary(REFS))))
    plugin.lookup("doe2024")
    asyncio.run(plugin.deactivate())
    with pytest.raises(RuntimeError):
        plugin.lookup("doe2024")


def test_router_answers_under_the_addon_prefix(plugin):
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    api = make_api(["library.read"], library=InMemoryLibrary(REFS))
    asyncio.run(plugin.activate(api))
    app = FastAPI()
    for router in api.routes.routers:
        app.include_router(router)
    response = TestClient(app).get("/api/plugins/template/lookup/doe2024")
    assert response.json()["title"] == "Deep Things"
