from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from openhab import Addons, Discovery, Inbox, Items, OpenHABClient, Rules, Things
from openhab_test_suite import ItemTester, RuleTester, ThingTester

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Config:
    url: str
    token: str | None
    username: str | None
    password: str | None
    verify: bool | str

    @classmethod
    def from_env(cls) -> "Config":
        load_dotenv()
        url = os.getenv("OPENHAB_URL", "").strip().rstrip("/")
        token = os.getenv("OPENHAB_TOKEN", "").strip() or None
        username = os.getenv("OPENHAB_USERNAME", "").strip() or None
        password = os.getenv("OPENHAB_PASSWORD", "") or None
        verify_raw = os.getenv("OPENHAB_VERIFY", "true").strip()
        verify: bool | str = verify_raw if verify_raw.lower() not in {"", "true", "1", "yes"} else True
        if verify_raw.lower() in {"false", "0", "no"}:
            verify = False
        if not url:
            raise ValueError("OPENHAB_URL is required; copy .env.example to .env and edit it.")
        if token is None and not (username and password):
            raise ValueError("Set OPENHAB_TOKEN or both OPENHAB_USERNAME and OPENHAB_PASSWORD.")
        return cls(url, token, username, password, verify)

    def client(self) -> OpenHABClient:
        kwargs: dict[str, Any] = {"url": self.url, "verify": self.verify}
        if self.token:
            kwargs["token"] = self.token
        else:
            kwargs.update(username=self.username, password=self.password)
        return OpenHABClient(**kwargs)


def binding_installed(addons: Addons, binding_id: str) -> bool:
    addons_data = addons.getAddons()
    if isinstance(addons_data, dict):
        addons_data = addons_data.get("addons", addons_data)
    if isinstance(addons_data, dict):
        addons_data = list(addons_data.values())
    return any(
        addon.get("uid", addon.get("id", addon.get("name", ""))) == binding_id
        and bool(addon.get("installed", addon.get("installedVersion", addon.get("version"))))
        for addon in (addons_data or []) if isinstance(addon, dict)
    )


def ensure_binding(addons: Addons, binding_id: str) -> str:
    if binding_installed(addons, binding_id):
        print(f"[OK] Binding '{binding_id}' ist bereits installiert; übersprungen.")
        return "already-installed"
    addons.installAddon(binding_id)
    print(f"[OK] Installation von Binding '{binding_id}' wurde angefordert.")
    return "install-requested"


def discover(discovery: Discovery, inbox: Inbox, binding_id: str, wait_seconds: int = 20) -> list[dict[str, Any]]:
    bindings = discovery.getDiscoveryBindings()
    if binding_id not in (bindings or []):
        print(f"[HINWEIS] '{binding_id}' meldet keinen Discovery-Scan-Endpunkt; Inbox wird geprüft.")
    else:
        try:
            timeout = discovery.startBindingScan(binding_id)
            wait_seconds = max(wait_seconds, min(int(timeout or 0), 60))
            print(f"[OK] Discovery-Scan für '{binding_id}' gestartet.")
        except Exception as exc:
            print(f"[HINWEIS] Scan nicht gestartet ({exc}); vorhandene Inbox-Ergebnisse werden geprüft.")
    time.sleep(wait_seconds)
    found = [x for x in (inbox.getDiscoveredThings() or []) if x.get("thingUID", "").startswith(binding_id + ":")]
    print(f"[OK] {len(found)} passende Inbox-Einträge gefunden.")
    return found


def slug(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not value or value[0].isdigit():
        value = "Device_" + value
    return value


def generate_files(binding_id: str, things: list[str], items: list[dict[str, str]], sitemap_widgets: list[dict[str, str]]) -> Path:
    output = ROOT / "generated" / binding_id
    output.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)
    (output / f"{binding_id}.things").write_text(env.get_template("things.j2").render(binding=binding_id, things=things), encoding="utf-8")
    (output / f"{binding_id}.items").write_text(env.get_template("items.j2").render(items=items), encoding="utf-8")
    (output / f"{binding_id}.sitemap").write_text(env.get_template("sitemap.j2").render(binding=binding_id, widgets=sitemap_widgets), encoding="utf-8")
    return output


def inspect_configured_things(things_api: Things, uids: list[str]) -> list[dict[str, Any]]:
    records = []
    for uid in uids:
        try:
            thing = things_api.getThing(uid)
            records.append(thing if isinstance(thing, dict) else {})
            channels = (thing or {}).get("channels", [])
            print(f"  {uid}: {len(channels)} Channels")
            for channel in channels:
                print(f"    - {channel.get('uid')} ({channel.get('channelTypeUID', 'unbekannt')})")
        except Exception as exc:
            print(f"[FEHLER] Thing/Channels für {uid} nicht lesbar: {exc}")
    return records


def run_checks(client: OpenHABClient, thing_uids: list[str], item_names: list[str], rule_uids: list[str] | None = None) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    thing_tester, item_tester, rule_tester = ThingTester(client), ItemTester(client), RuleTester(client)
    for uid in thing_uids:
        try:
            ok = bool(thing_tester.isThingOnline(uid))
            results.append({"type": "Thing ONLINE", "name": uid, "ok": ok})
        except Exception as exc:
            results.append({"type": "Thing ONLINE", "name": uid, "ok": False, "detail": str(exc)})
    for name in item_names:
        try:
            ok = bool(item_tester.doesItemExist(name))
            results.append({"type": "Item vorhanden", "name": name, "ok": ok})
        except Exception as exc:
            results.append({"type": "Item vorhanden", "name": name, "ok": False, "detail": str(exc)})
    for uid in rule_uids or []:
        try:
            rules = Rules(client).getRules()
            ok = any(rule.get("uid") == uid for rule in (rules or []))
            results.append({"type": "Rule vorhanden", "name": uid, "ok": ok})
        except Exception as exc:
            results.append({"type": "Rule vorhanden", "name": uid, "ok": False, "detail": str(exc)})
    print("\nPrüfbericht")
    for result in results:
        print(f"[{ 'OK' if result['ok'] else 'FEHLER' }] {result['type']}: {result['name']}" + (f" — {result['detail']}" if result.get("detail") else ""))
    return results


def save_report(binding_id: str, results: list[dict[str, Any]]) -> Path:
    path = ROOT / "generated" / binding_id / "setup-report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

