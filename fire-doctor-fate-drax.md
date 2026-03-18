# Kimi Agent API — Technische Spezifikation

> **Autor:** Kimi (Entwurf) / PRISM (Review & Erweiterung)  
> **Stand:** 2026-03-18  
> **Status:** Planung / RFC  
> **Zweck:** HTTP-API damit externe AI-Agenten (PRISM, UMBRA, Forge, zukünftige Agents) Tasks an Kimi übergeben, verhandeln und Ergebnisse asynchron abholen können.

---

## Kontext & Einordnung

Kimi läuft auf Druids Windows-Rechner (Tailscale-Netzwerk). PRISM, UMBRA und andere CMG-Agenten laufen auf Mac/Linux. Diese API ist die Brücke — sie macht Kimi zu einem **adressierbaren, asynchronen Task-Worker** im CMG-Agenten-Ökosystem.

**Verhältnis zu UAP (UMBRA Agent Protocol):**  
UAP regelt Status-Heartbeats der Agenten. Die Kimi Agent API ergänzt UAP als **Task-Delegation-Layer** — UAP sagt "ich lebe", diese API sagt "hier ist Arbeit für dich".

---

## Architektur

```
CMG Agent Network (Tailscale)
┌─────────────────────────────────────────────┐
│  PRISM (Mac)  ──────────────────────────────┤
│  UMBRA (Mac)  ─→  Kimi Agent API :7777  ──→ │ Kimi (Windows)
│  Forge (Mac)  ──────────────────────────────┤
└─────────────────────────────────────────────┘
         HTTP/REST          Bridge
         + Webhook          (kimi_bridge.py)
```

### Dateistruktur

```
kimi_agent_api/
├── api/
│   ├── server.py           # FastAPI App, Middleware, CORS
│   ├── routes.py           # Endpoint-Definitionen
│   ├── models.py           # Pydantic Request/Response Models
│   └── auth.py             # Token-Validierung, IP-Whitelist
├── core/
│   ├── task_queue.py       # asyncio.Queue + SQLite-Persistenz
│   ├── negotiation.py      # Verhandlungs-State-Machine
│   └── bridge.py           # Kimi CLI / Headless-Mode Wrapper
├── config/
│   └── settings.yaml       # Port, Token, Tailscale-Config
├── data/
│   └── tasks.db            # SQLite (Tasks, Status, History)
├── logs/
│   └── api.log
├── service/
│   └── install_service.ps1 # Windows Service Installer
├── test_client.py          # End-to-End Testskript
├── requirements.txt
└── start_api.py            # Entrypoint
```

---

## API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/health` | GET | Liveness check + Kimi-Status |
| `/agent/connect` | POST | Agent registriert sich (bekommt Session-Token) |
| `/tasks/submit` | POST | Task einreichen |
| `/tasks/{id}/status` | GET | Aktuellen Status abfragen |
| `/tasks/{id}/result` | GET | Fertiges Ergebnis abholen |
| `/tasks/{id}/negotiate` | POST | Scope/Umfang verhandeln |
| `/tasks/{id}/cancel` | DELETE | Task abbrechen |
| `/webhook/register` | POST | Callback-URL für Push-Updates |
| `/tasks` | GET | Alle Tasks (mit Filter: status, agent_id) |

### WebSocket (empfohlen für Live-Updates)

```
ws://100.x.x.x:7777/ws/tasks/{id}
```

Sendet Events bei jedem Status-Wechsel — vermeidet Polling. Fällt auf HTTP-Polling zurück wenn WebSocket nicht verfügbar.

---

## Task-Lifecycle

```
SUBMITTED
    │
    ▼
NEGOTIATING ──(abgelehnt)──→ DECLINED
    │
    ▼ (angenommen / nicht verhandelbar)
ACCEPTED
    │
    ▼
PROCESSING
    │
    ├──→ COMPLETED  ✅
    ├──→ FAILED     ❌
    └──→ CANCELLED  🚫 (via /cancel)
```

**Timeout-Verhalten:**
- Keine Antwort auf Negotiation in 60s → automatisch `DECLINED`
- Processing überschreitet `max_duration` → `FAILED` mit Reason

---

## Datenmodelle

### Task Submission

```python
class TaskSubmission(BaseModel):
    agent_id: str           # z.B. "prism", "forge", "umbra"
    task_type: str          # "code_review" | "refactor" | "research" | "generate" | "custom"
    title: str
    description: str
    payload: dict           # Frei — Files, Code, Context, URLs
    priority: int = 3       # 1 (niedrig) bis 5 (kritisch)
    max_duration: int = 300 # Sekunden
    negotiable: bool = True # Darf Kimi Gegenvorschlag machen?
    webhook_url: str | None = None
    tags: list[str] = []    # z.B. ["mmc", "godot", "urgent"]
```

### Negotiation

```python
class NegotiationProposal(BaseModel):
    task_id: str
    accepted: bool
    counter_proposal: dict | None = None
    # Wenn nicht accepted:
    # counter_proposal = {
    #   "scope_reduction": "Nur Funktion X statt ganzes Modul",
    #   "duration_estimate": 480,
    #   "clarifications_needed": ["Welche Python-Version?"],
    #   "alternative_approach": "Könnte stattdessen Y machen"
    # }
```

### Task Result

```python
class TaskResult(BaseModel):
    task_id: str
    status: str
    result: dict            # task_type-spezifisch
    duration_seconds: float
    tokens_used: int | None = None
    completed_at: str       # ISO timestamp
```

---

## Kimi Bridge — Offene Fragen beantwortet

**Frage 1: Headless oder mit UI?**  
→ **Headless-Mode** via `kimi.exe --headless` oder Wrapper-Script. UI nur für manuelles Debugging. Die API soll 24/7 im Hintergrund laufen.

**Frage 2: Wie wird Kimi gestartet?**  
→ `bridge.py` spawnt Kimi als Subprocess mit stdin/stdout-Pipe. Alternativ: Kimi selbst öffnet eine lokale Socket-Verbindung zur API (bevorzugt wenn Kimi bereits läuft).

```python
# Option A: Subprocess
proc = subprocess.Popen(["kimi.exe", "--headless", "--api-mode"],
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)

# Option B: Kimi verbindet sich selbst (stabiler)
# Kimi → POST /internal/register → bekommt Task-Stream
```

**Frage 3: Task-Priorisierung oder FIFO?**  
→ **Priority Queue**: Tasks mit Priority 5 werden sofort vorgezogen. Priority 1-4 FIFO innerhalb der Prioritätsstufe. Max 1 Task gleichzeitig (Kimi ist single-threaded).

**Frage 4: Maximale Parallelität?**  
→ **1 Task gleichzeitig** — Kimi soll fokussiert arbeiten. Weitere Tasks warten in der Queue. Queue-Tiefe: max 20 (danach `503 Queue Full`).

---

## Security

```yaml
# settings.yaml
auth:
  token: "umbra-kimi-2026"      # Shared Secret (ändern!)
  ip_whitelist:                  # Nur Tailscale-IPs
    - "100.0.0.0/8"
  rate_limit: 30                 # Requests/Minute pro Agent

server:
  port: 7777
  host: "0.0.0.0"
  tailscale_only: true           # Bindet NUR an Tailscale-Interface (sicherer)
```

**Empfehlung:** Tailscale ACLs so setzen dass Port 7777 nur von bekannten Nodes erreichbar ist.

---

## Autostart (Windows)

**Empfohlen: Windows Service via NSSM**

```powershell
# install_service.ps1
$nssm = "C:\tools\nssm.exe"
& $nssm install KimiAgentAPI python start_api.py
& $nssm set KimiAgentAPI AppDirectory "C:\Users\matth\.kimi\agent_api"
& $nssm set KimiAgentAPI Start SERVICE_AUTO_START
& $nssm start KimiAgentAPI
```

Alternativ: Task Scheduler bei Login, verstecktes Fenster (`pythonw start_api.py`).

---

## Integration mit PRISM

PRISM (Mac) kann Kimi so beauftragen:

```python
# In PRISM-Scripts oder Cron-Jobs
import requests

def delegate_to_kimi(task_type, title, description, payload):
    r = requests.post("http://100.x.x.x:7777/tasks/submit",
        headers={"Authorization": "Bearer umbra-kimi-2026"},
        json={
            "agent_id": "prism",
            "task_type": task_type,
            "title": title,
            "description": description,
            "payload": payload,
            "priority": 3,
            "negotiable": True,
            "webhook_url": "http://100.98.137.48:5678/webhook/kimi-result"
        })
    return r.json()["task_id"]

# Beispiel: Code-Review an Kimi delegieren
task_id = delegate_to_kimi(
    "code_review",
    "Review: character_manager.gd",
    "Prüfe auf Godot 4 Best Practices und Performance-Issues",
    {"file_content": open("character_manager.gd").read(), "context": "MMC"}
)
```

---

## Implementierungsplan

| Schritt | Inhalt | Aufwand |
|---------|--------|---------|
| 1. Setup | Ordnerstruktur, venv, requirements.txt | 15 min |
| 2. Models & Auth | Pydantic Models, Token-Check, IP-Filter | 20 min |
| 3. Core Server | FastAPI App, Endpoints (ohne Bridge) | 30 min |
| 4. Task Queue | asyncio.Queue + SQLite-Persistenz | 30 min |
| 5. Bridge | Kimi-Subprocess oder Socket-Verbindung | 45 min |
| 6. Negotiation | State Machine, Proposal/Counter | 25 min |
| 7. WebSocket | Live-Status-Updates | 20 min |
| 8. Autostart | Windows Service via NSSM | 15 min |
| 9. Test | test_client.py, End-to-End mit PRISM | 20 min |
| **Total** | | **~3.5h** |

### requirements.txt

```
fastapi>=0.110
uvicorn[standard]>=0.27
pydantic>=2.0
aiosqlite>=0.20
websockets>=12.0
PyYAML>=6.0
requests>=2.31
```

---

## Nächste Schritte

- [ ] Kimi: `bridge.py` implementieren (Headless-Subprocess)
- [ ] PRISM: `delegate_to_kimi()` Helper in `scripts/` ablegen
- [ ] Tailscale ACL für Port 7777 einrichten
- [ ] UMBRA: Kimi-Status als Panel in der UI anzeigen (via `/health`)
- [ ] UAP erweitern: Kimi als registrierten Agent eintragen

---

*Dokument: `fire-doctor-fate-drax.md` | Repo: AstroGolem224/prism-hub*
