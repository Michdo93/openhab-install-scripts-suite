# openhab-install-scripts-suite

Eine offene Sammlung von Python-Beispielen, mit denen Techniker openHAB-Bindings einrichten, Konfiguration vorbereiten und das Ergebnis verständlich prüfen können. Jedes Binding hat einen eigenen Ordner. Das Repo ist als Lern- und Community-Projekt gedacht: Ein Binding-Beispiel darf Besonderheiten erklären, statt eine universelle automatische Einrichtung zu versprechen.

## Loslegen

Voraussetzung: openHAB ist bereits installiert und eingerichtet. Die REST API muss erreichbar sein. Verwende entweder einen API-Token oder Basic Authentication (Basic Auth muss in openHAB ausdrücklich aktiviert sein).

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item .env.example .env
```

Bearbeite `.env` und trage die vollständige Basis-URL ein, einschließlich Schema und gegebenenfalls Port oder Proxy-Pfad, zum Beispiel `https://openhab.example.net:8443`. Trage entweder `OPENHAB_TOKEN` oder beide `OPENHAB_USERNAME` und `OPENHAB_PASSWORD` ein. `.env` wird von Git ignoriert. Bei privatem HTTPS-Zertifikat kannst du `OPENHAB_VERIFY` auf einen CA-Bundle-Pfad setzen. Zertifikatsprüfung sollte aktiv bleiben.

```powershell
oh-suite hue
oh-suite sonos
```

Die Skripte prüfen zunächst die Add-on-Liste, installieren bei Bedarf das Binding, starten einen Discovery-Scan, listen Inbox-Funde und vorhandene Channels auf und prüfen den verfügbaren Zustand. Beispiel-Dateien landen in `generated/<binding>/` mit den Binding-Namen `hue.things`, `hue.items`, `hue.sitemap` bzw. `sonos.*`. Bitte die dortigen Kommentare und Beispiel-UIDs/Channels anhand der eigenen Installation prüfen, bevor Dateien nach `conf/things`, `conf/items` und `conf/sitemaps` kopiert werden. Textdateien in diesen Ordnern werden von der REST API nicht automatisch als openHAB-Dateien installiert. `generated/` ist absichtlich lokal und wird nicht eingecheckt.

Am Ende erscheint ein Prüfbericht auf der Konsole und als `setup-report.json`. Der Bericht unterscheidet fehlende Einträge von erreichbaren Things; ohne passende Hardware oder nach noch nicht bestätigter Discovery sind Fehler ein erwartbares und hilfreiches Ergebnis.

## Was die Beispiele zeigen

### Hue

Die Hue Bridge wird über mDNS gefunden. Nach dem Hinzufügen muss die physische Taste auf der Bridge gedrückt werden; erst nach der Autorisierung legt das Binding Geräte in der Inbox ab. Das Skript wartet auf Inbox-Einträge und listet Channels von bereits hinzugefügten Hue Things. Verwende danach die echten `thingUID`s, Ressourcen-IDs und Channel-IDs aus deiner Installation. Das Beispiel führt keinen Schreibbefehl an eine Lampe aus.

### Sonos

Das Skript zeigt Inbox-Funde und fragt vor dem Hinzufügen einzeln nach. Das Sonos Thing benötigt die UDN des Players. Channel-IDs hängen von Thing UID und Gerät ab. Das Beispiel listet die tatsächlich vorhandenen Channels und zeigt Player, Lautstärke und Mute als Items; es sendet keine Wiedergabebefehle.

## Aufbau

```text
bindings/<binding>/install.py   Einstiegspunkt und binding-spezifische Schritte
src/openhab_install_scripts_suite/ gemeinsame Konfiguration, REST-Helfer und Prüfbericht
templates/                      Jinja 3 Vorlagen für Things, Items und Sitemap
docs/                           Contributor- und Erweiterungshinweise
```

Die gemeinsamen Schritte sind: Binding-Status prüfen und nötigenfalls installieren; Discovery starten, soweit unterstützt; Inbox und Thing-Informationen anzeigen; Channels auslesen; Konfigurationsbeispiele erzeugen; abschließend Items/Things/optionale Rules über `openhab-test-suite` prüfen. Ein aktiver Schalt- oder Lautstärketest kann Geräte beeinflussen und gehört deshalb in ein binding-spezifisches, ausdrücklich aktiviertes Beispiel.

## Rules, Transformationen und Individualprojekte

Binding-spezifische Transformationen und Rules DSL, openHAB Python (GraalPy) oder JavaScript (GraalJS) gehören in klar gekennzeichnete optionale Beispiele. Nicht jedes Binding braucht sie. Dieses Grundgerüst installiert solche Regeln noch nicht automatisch. Firmen können ihre Kundenanpassungen in einem separaten privaten Projekt ablegen und Vorlagen/Helfer aus dieser Suite übernehmen.

## Mitmachen

Bitte lies [docs/contributing.md](docs/contributing.md). Ein neuer Beitrag sollte die eigene Discovery-Grenze, manuelle Voraussetzungen, benötigte Konfiguration und prüfbare Erfolgskriterien nennen. Binding-Dokumentation ist die Quelle für konkrete Channel- und Konfigurationsangaben.

## Lizenz

MIT. Siehe [LICENSE](LICENSE).

