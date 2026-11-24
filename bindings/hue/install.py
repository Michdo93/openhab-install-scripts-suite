"""Hue example: bridge discovery can require a physical button press."""
from __future__ import annotations

from openhab import Addons, Discovery, Inbox, Items, Things

from openhab_install_scripts_suite.common import discover, ensure_binding, generate_files, inspect_configured_things, run_checks, save_report, slug

BINDING = "hue"


def run(client) -> None:
    addons, discovery, inbox, things_api, items_api = Addons(client), Discovery(client), Inbox(client), Things(client), Items(client)
    ensure_binding(addons, BINDING)
    print("Hue-Hinweis: Bridge-Ergebnis ggf. bestätigen und die Taste am Bridge drücken; erst danach werden Geräte entdeckt.")
    found = discover(discovery, inbox, BINDING, wait_seconds=20)
    for result in found:
        print(f"  Inbox: {result.get('thingUID')} — {result.get('label', '')}")
    existing = things_api.getThings() or []
    hue_things = [thing for thing in existing if thing.get("UID", thing.get("uid", "")).startswith("hue:")]
    if hue_things:
        print("\nChannels der bereits hinzugefügten Hue Things:")
        inspect_configured_things(things_api, [t.get("UID", t.get("uid")) for t in hue_things])
    declarations = [f"// Thing {t.get('thingUID')} — zuerst im openHAB UI authentifizieren, dann Dateiangaben ergänzen." for t in found]
    if not declarations:
        declarations = ["// Keine Discovery-Ergebnisse: Bridge zuerst im UI hinzufügen und Taste drücken."]
    item_specs = [
        {"type": "Switch", "name": "Hue_Example_Light", "label": "Hue Beispiel Licht", "icon": "light", "group": "Hue", "channel": "hue:device:bridge:resource:light"},
        {"type": "Dimmer", "name": "Hue_Example_Brightness", "label": "Hue Helligkeit", "icon": "slider", "group": "Hue", "channel": "hue:device:bridge:resource:brightness"},
    ]
    output = generate_files(BINDING, declarations, item_specs, [{"type": "Switch", "item": "Hue_Example_Light", "label": "Hue Licht"}, {"type": "Slider", "item": "Hue_Example_Brightness", "label": "Helligkeit"}])
    configured_uids = [t.get("UID", t.get("uid", "")) for t in hue_things]
    print(f"\n[OK] Beispiel-Dateien erstellt: {output}")
    results = run_checks(client, configured_uids, [item["name"] for item in item_specs])
    print(f"Bericht: {save_report(BINDING, results)}")


if __name__ == "__main__":
    from openhab_install_scripts_suite.cli import main
    main()
