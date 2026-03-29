# QR-Code Generator

Eine macOS Desktop-App zum Erstellen von QR-Codes – für URLs, beliebigen Text und Visitenkarten (vCard).

---

## Features

- **Text & URLs** – beliebiger Text oder Link als QR-Code
- **Mehrere QR-Codes auf einmal** – Eingaben durch Leerzeilen trennen, jeder Block wird ein eigener QR-Code
- **Visitenkarten-Tab** – Formular mit Vor-/Nachname, Firma, Funktion, Telefon, E-Mail, Website → erzeugt einen gültigen vCard 3.0 QR-Code
- **Vorschau** – QR-Codes direkt in der App anzeigen, bevor sie gespeichert werden
- **Speichern als PNG** – Ausgabe auf dem Desktop oder einem beliebigen Ordner
- **Light Theme** – helles, kontrastarmes UI (weiß / light gray)

---

## Voraussetzungen

- macOS (arm64 / Apple Silicon)
- Python 3.12+
- Homebrew empfohlen für `python-tk`

---

## Installation & Erster Start

```bash
# 1. Repository klonen
git clone https://github.com/matthiaslangenberg/qr-code.git
cd qr-code

# 2. Virtuelle Umgebung anlegen und Abhängigkeiten installieren
python3 -m venv .venv
source .venv/bin/activate
pip install qrcode pillow pyinstaller

# 3. App direkt starten (ohne Build)
python3 qr.py
```

---

## macOS App-Bundle bauen

```bash
bash build.sh
```

Das Skript:
1. Aktiviert das venv
2. Führt PyInstaller aus (`qr.spec`)
3. Bereinigt Extended Attributes (Homebrew-Bibliotheken)
4. Signiert das Bundle ad-hoc (`codesign --sign -`)
5. Entfernt das Quarantäne-Flag
6. Öffnet `dist/` im Finder

Die fertige App liegt danach unter `dist/qr.app` und lässt sich per Doppelklick starten.

> **Hinweis:** Die Datei `build/qr/qr.pkg` ist ein internes PyInstaller-Artefakt –  
> nicht zu öffnen. Die App ist ausschließlich `dist/qr.app`.

---

## Projektstruktur

```
qr-code/
├── qr.py        # Anwendungslogik & UI
├── qr.spec      # PyInstaller Build-Konfiguration
├── build.sh     # Build-Skript (inkl. Signing & xattr-Cleanup)
└── dist/
    └── qr.app   # Fertige macOS App
```

---

## Benutzung

### Tab „Text / URL"

Einen oder mehrere QR-Codes aus freiem Text oder URLs erzeugen.

| Eingabe | Ergebnis |
|---|---|
| Eine Zeile / ein URL | 1 QR-Code |
| Mehrere Blöcke, getrennt durch Leerzeile | 1 QR-Code pro Block |

Schaltfläche **+ Block hinzufügen** fügt automatisch einen Trenner ein.  
Der Live-Zähler zeigt die Anzahl erkannter QR-Codes während der Eingabe.

### Tab „Visitenkarte"

Felder ausfüllen → die App erzeugt daraus einen vCard 3.0 QR-Code.  
Das `https://`-Präfix wird bei der Website automatisch ergänzt.

### Speichern

Speicherort unten auswählen (Standard: Desktop), dann **💾 Speichern** klicken.  
Dateinamen werden automatisch aus dem Inhalt abgeleitet.

---

## Abhängigkeiten

| Paket | Zweck |
|---|---|
| `qrcode` | QR-Code-Generierung |
| `Pillow` | Bildverarbeitung & Footer-Text |
| `pyinstaller` | macOS App-Bundle |
