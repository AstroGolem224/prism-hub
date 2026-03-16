# 📷 PRISM Hub — Kamera-Integration

> Setup-Dokumentation für die Reolink IP-Kameras im lokalen Netzwerk.

---

## Übersicht

PRISM Hub bindet zwei Reolink IP-Kameras direkt in die Web-UI ein (`/cameras`).
Snapshots werden serverseitig abgerufen und per HTTP an den Browser ausgeliefert —
keine direkte Browser-zu-Kamera Verbindung nötig.

---

## Kamera-Konfiguration (`server.py`)

```python
CAMERAS = {
    "haustuer": {
        "name":      "Haustür",
        "ip":        "192.168.137.100",
        "auth_mode": "basic",
        "user":      "<cam-user>",
        "password":  "<cam-password>",
    },
    "vorne": {
        "name":      "Vorne",
        "ip":        "192.168.137.166",
        "auth_mode": "token",
        "user":      "<cam-user>",
        "password":  "<cam-password>",
    },
}
```

---

## Auth-Modi

### `basic` — HTTP Basic Auth (Haustür)
Älteres Kamera-Modell, akzeptiert Credentials direkt in der URL:

```
GET http://<ip>/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=abc&user=<user>&password=<password>
```

### `token` — Session Token Auth (Vorne)
Neueres Modell mit HTTPS + Token-Login. Ablauf:

1. **Login** — POST an `https://<ip>/api.cgi` mit Username/Password → erhält `token`
2. **Snapshot** — GET mit Token-Parameter:
   ```
   GET https://<ip>/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=abc&token=<token>
   ```
3. **Token-Cache** — Tokens werden server-seitig gecacht (TTL-basiert), bei 401 automatisch erneuert

---

## SSL — Legacy Support

Neuere Reolink-Modelle nutzen selbst-signierte Zertifikate mit alten TLS-Ciphers.
server.py erstellt dafür einen relaxten SSL-Context:

```python
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE
ctx.set_ciphers('DEFAULT:@SECLEVEL=0')
ctx.minimum_version = ssl.TLSVersion.TLSv1
```

---

## Snapshot-Endpoint (Hub intern)

Der Hub stellt Snapshots unter folgendem Pfad bereit:

```
GET /cam/<cam_id>/snap
```

- Ruft Snapshot von Kamera ab (Reolink CGI API)
- Gibt JPEG-Bild direkt aus
- Query-Param `?t=<timestamp>` verhindert Browser-Caching

---

## UI (`/cameras`)

- Auto-Refresh alle 5 Sekunden per JavaScript
- Klick auf Kamera-Bild → Lightbox / Vollbild
- IP-Badge sichtbar im Kamera-Header
- Nur im internen Hub verfügbar (nicht auf Public Cloudflare-Seite)

---

## Neue Kamera hinzufügen

In `server.py` unter `CAMERAS` eintragen:

```python
"<cam-id>": {
    "name":      "<Anzeigename>",
    "ip":        "<LAN-IP>",
    "auth_mode": "basic",   # oder "token" für HTTPS-Modelle
    "user":      "<cam-user>",
    "password":  "<cam-password>",
},
```

Kein Neustart nötig — Hub liest `CAMERAS` beim Start.

---

*PRISM Hub Cam Setup // Clay Machine Games // 2026 // 🔮*
