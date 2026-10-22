# LocalBib Add-on Template

A minimal LocalBib Add-on in Bundle form: one backend endpoint, one view, one
Slot, two languages, and tests that run against the Add-on Contract's fakes —
no LocalBib core installation required. Clone this repository and follow the
steps below to turn it into your own Add-on. The full contract (Manifest
fields, Berechtigungen, Slots, stable core endpoints, design tokens, locale
and namespace rules, submitting to the Marketplace-Index) is documented in
`AUTHORING.md` of the `localbib-plugin-api` package
(<https://pypi.org/project/localbib-plugin-api/>).

## 1. Set up

```bash
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install "localbib-plugin-api[dev]>=2,<3" -r requirements-dev.txt
```

## 2. Check the Bundle

```bash
localbib-addon check .
```

This validates `plugin.json` against the Manifest schema, the Bundle
structure (a Python package under the Add-on id, `frontend/` with exactly one
script), the namespace rules the core enforces at load time (view/slot keys,
routes, locale keys all prefixed with your Add-on id) and locale parity
between `en` and `de`. It should print `OK` before you change anything.

## 3. Run the tests

```bash
pytest tests
```

These tests exercise `template/__init__.py` through `plugin_api.testing`'s
fakes (`InMemoryLibrary`, `make_api`) — the same seam LocalBib's own official
Add-ons use for their isolated test suites. No LocalBib core, no database, no
network. `plugin_api.testing` also ships fakes for the other gated services
(`DummyLlm`, `NullFiles`, `TempSqliteStorage`) if your own Add-on uses them.

## 4. Rename it to your own Add-on

Replace every occurrence of `template` with your own Add-on id
(`^[a-z][a-z0-9_]{1,39}$`), in this order:

1. `plugin.json`: `id`, `name`, `author`, `license`, `homepage`, `tagline`,
   `description`. Keep `api_version: 2`; raise `min_core` only if you use
   something newer.
2. Rename the `template/` package folder to your id and update its imports.
3. Rename `frontend/template.js` / `.css` and the two locale files; update
   `plugin.json`'s `frontend` block to match.
4. In `frontend/template.js`: the `id` passed to `registerPlugin`, every view
   key (`template.main`), route (`/template`), Slot key (`template.aside`)
   and locale key (`template.*`) — all must start with your id.
5. In `frontend/template.css`: every class keeps the `<your-id>-` prefix
   (`localbib-addon check` warns, but does not block, if you forget one).
6. In the two locale files: every key starts with `<your-id>.`.
7. Decide your Add-on's Berechtigungen (`plugin.json`'s `permissions`): only
   ask for what you use. `AUTHORING.md` lists what each one unlocks and
   whether the core enforces it or only records your declaration.
8. Replace `template/api.py`'s one endpoint and `TemplatePlugin.lookup` with
   your own logic; keep every route under `/api/plugins/<your id>/` — the
   core refuses to activate an Add-on whose router escapes that prefix.
9. Replace the Slot component and the view template in
   `frontend/template.js` with your own UI.

Re-run `localbib-addon check .` and `pytest tests` after each step.

## 5. Try it against a running LocalBib

Point a LocalBib installation (source checkout or the packaged app) at this
folder as a **Dev-Suchpfad** — the same mechanism the maintainer uses for
Atlas and Hipster during development:

```bash
# in the LocalBib core's .env, or as an environment variable:
LOCALBIB_PLUGIN_DEV_PATHS=/path/to/this/folder
```

Restart LocalBib (or open the Marketplace and use **Aus Ordner laden** to
point at this folder directly, without an env var). Your Add-on appears in
the Marketplace under **Entwicklung**; consenting to its Berechtigungen
activates it live — its nav entry, view and Slot show up without a reload.

## 6. Build and submit

```bash
localbib-addon build . --out dist
```

This writes a deterministic Zip, its SHA-256 checksum file and an index
snippet (`dist/<id>-<version>.index.json`) — the exact fields the
Marketplace-Index expects. Tag a release `vX.Y.Z` matching `plugin.json`'s
`version`; the build workflow shipped with this repository (added when the
maintainer's export tooling published it, see `.github/workflows/`) builds
the Bundle and attaches the Zip, checksum and snippet to the GitHub Release
automatically — never copy a checksum by hand.

To list your Add-on in the Marketplace, open a pull request against
`localbib-plugins` adding your entry to `index.json`, following its
`PULL_REQUEST_TEMPLATE.md`. Its CI checks the schema, that your release
asset is reachable, its checksum, the Manifest inside the Zip against your
index entry, `localbib-addon check` on the unpacked Bundle, that `license` is
set and that `homepage` links to your source repository. Every Add-on
submitted this way is shown as **Drittanbieter** (third-party), never as
*Offiziell* — the review checks the shape of your submission, not its
behaviour or trustworthiness.

## License

This template is MIT-licensed (see `LICENSE`) so you can license your own
Add-on however you like; while it runs in-process with the AGPL LocalBib
core, AGPL-compatible licensing is recommended.
