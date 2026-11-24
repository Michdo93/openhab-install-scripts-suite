# Binding-Beispiele beitragen

Jedes Binding erhält einen eigenen Ordner `bindings/<id>/` und ein eigenständiges `install.py`. Gemeinsame Authentifizierung, Dateierzeugung und Prüfbericht gehören nach `src/openhab_install_scripts_suite/`, damit Contributor sie wiederverwenden können.

## Ablauf dokumentieren

1. Add-on-ID prüfen und Installation idempotent überspringen, falls installiert.
2. Discovery für genau dieses Binding starten, sofern es einen Scan unterstützt. Danach die Inbox auf Ergebnisse dieses Bindings begrenzen.
3. Manuelle Schritte und nicht unterstützte Discovery ausdrücklich ausgeben.
4. Erst nach einer Bestätigung Inbox-Einträge übernehmen.
5. Thing-Konfiguration und Channels eines echten Things auslesen. Channel UIDs nicht aus Beispielen als universell gültig annehmen.
6. `<binding>.things`, `<binding>.items` und `<binding>.sitemap` mit den Jinja-Vorlagen erzeugen. Unbekannte geräteabhängige Werte klar als Platzhalter kennzeichnen.
7. Mit `openhab-test-suite` mindestens die Existenz/Erreichbarkeit der erwarteten Things und Items prüfen. Rules nur prüfen, wenn das Beispiel sie anlegt. Befehle an Aktoren benötigen eine separate bewusste Freigabe.

## Pull Requests

Beschreibe openHAB-Version, getestete Binding-Version, erforderliche Hardware, manuelle Schritte und bekannte Grenzen. Niemals Tokens, Passwörter, private URLs oder Kundendaten committen. Änderungen an `generated/` gehören nicht in den Pull Request.

