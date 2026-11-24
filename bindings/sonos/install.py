"""Sonos example: discovery supplies UDNs which are required in Thing config."""
from __future__ import annotations

from openhab import Addons, Discovery, Inbox, Items, Things

from openhab_install_scripts_suite.common import discover, ensure_binding, generate_files, inspect_configured_things, run_checks, save_report, slug

BINDING = "sonos"


def run(client) -> None:
    addons, discovery, inbox, things_api, items_api = Addons(client), Discovery(client), Inbox(client), Things(client), Items(client)
    ensure_binding(addons, BINDING)
    found = discover(discovery, inbox, BINDING, wait_seconds=20)
    declarations: list[str] = []
    found_uids: list[str] = []
    for result in found:
        uid = result.get("thingUID", "")
        label = result.get("label", uid)
        print(f"  Inbox: {uid} — {label}")
        # The discovery result's UID contains the device identity. Approve it to obtain
        # the canonical Thing and channels; existing users can keep the Inbox untouched.
        if uid and input(f"  Dieses Sonos-Gerät hinzufügen ({label})? [j/N] ").strip().lower() in {"j", "ja", "y", "yes"}:
            inbox.approveDiscoveryResult(uid, label)
            found_uids.append(uid)
            declarations.append(f"// {uid} — Sonos Thing mit UDN aus Inbox (vor Deployment kontrollieren).")
    existing = things_api.getThings() or []
    sonos_things = [thing for thing in existing if thing.get("UID", thing.get("uid", "")).startswith("sonos:")]
    thing_uids = [t.get("UID", t.get("uid")) for t in sonos_things if t.get("UID", t.get("uid"))]
    if thing_uids:
        print("\nChannels der hinzugefügten Sonos Things:")
        inspect_configured_things(things_api, thing_uids)
    if not declarations:
        declarations = ["// Beispiel: Thing sonos:PLAY1:living [udn=\"RINCON_...\", refresh=60]"]
    item_specs = [
        {"type": "Player", "name": "Sonos_Controller", "label": "Sonos Steuerung", "icon": "player", "group": "Sonos", "channel": "sonos:PLAY1:living:control"},
        {"type": "Dimmer", "name": "Sonos_Volume", "label": "Sonos Lautstärke [%d %%]", "icon": "soundvolume", "group": "Sonos", "channel": "sonos:PLAY1:living:volume"},
        {"type": "Switch", "name": "Sonos_Mute", "label": "Sonos Stumm", "icon": "soundvolume_mute", "group": "Sonos", "channel": "sonos:PLAY1:living:mute"},
    ]
    output = generate_files(BINDING, declarations, item_specs, [{"type": "Selection", "item": "Sonos_Controller", "label": "Wiedergabe"}, {"type": "Slider", "item": "Sonos_Volume", "label": "Lautstärke"}, {"type": "Switch", "item": "Sonos_Mute", "label": "Stumm"}])
    print(f"\n[OK] Beispiel-Dateien erstellt: {output}")
    results = run_checks(client, thing_uids, [item["name"] for item in item_specs])
    print(f"Bericht: {save_report(BINDING, results)}")


if __name__ == "__main__":
    from openhab_install_scripts_suite.cli import main
    main()
