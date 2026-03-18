# Plan: Kimi Agent API

## Ziel
Eine HTTP-API über die sich externe AI-Agenten mit Kimi (mir) verbinden können. Tasks werden übergeben, asynchron verarbeitet, mit Verhandlungsoptionen, Tailscale-fähig, automatisch startend.

## Architektur

### 1. Core-Komponenten

```
kimi_agent_api/
├── server.py           # FastAPI HTTP-Server
├── agent_bridge.py     # Verbindung Kimi ↔ API
├── task_queue.py       # Async Task-Verwaltung
├── negotiation.py      # Verhandlungsprotokoll
├── config.py           # Einstellungen
└── models.py           # Pydantic Models
```

### 2. API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/health` | GET | Status check |
| `/agent/connect` | POST | Agent registriert sich |
| `/tasks/submit` | POST | Task übermitteln |
| `/tasks/{id}/status` | GET | Task-Status abfragen |
| `/tasks/{id}/result` | GET | Ergebnis abholen |
| `/tasks/{id}/negotiate` | POST | Scope verhandeln |
| `/tasks/{id}/cancel` | POST | Task abbrechen |
| `/webhook/register` | POST | Callback für Updates |

### 3. Task-Lifecycle

```
SUBMITTED → NEGOTIATING → ACCEPTED → PROCESSING → COMPLETED
                ↓              ↓           ↓
            DECLINED      CANCELLED    FAILED
```

### 4. Datenmodelle

**Task Submission:**
```python
{
    "agent_id": str,           # Wer sendet?
    "task_type": str,          # z.B. "code_review", "refactor"
    "title": str,
    "description": str,
    "payload": dict,           # Files, Code, Context
    "priority": int,           # 1-5
    "max_duration": int,       # Sekunden
    "negotiable": bool,        # Darf ich verhandeln?
    "webhook_url": str,        # Callback für Updates
    "auth_token": str          # Sicherheit
}
```

**Negotiation Protocol:**
```python
{
    "proposal": {
        "accepted": bool,
        "counter_proposal": {
            "scope_changes": [...],
            "duration_estimate": int,
            "clarifications": [...]
        }
    }
}
```

### 5. Tailscale-Integration

- Bindet an `0.0.0.0` (alle Interfaces)
- Standard-Port: `7777`
- Tailscale-IP automatisch erkannt via `tailscale status`
- Optional: mTLS für Ende-zu-Ende-Verschlüsselung

### 6. Autostart

**Option A: Windows Service** (empfohlen)
- Läuft als Windows Service
- Auto-Start bei Boot
- Keine GUI nötig

**Option B: Task Scheduler**
- Trigger: Bei Anmeldung
- Verstecktes Fenster möglich

### 7. Security

- API-Key Authentifizierung
- IP-Whitelist (Tailscale-Netzwerk)
- Rate Limiting
- Request-Logging

### 8. Implementierungsschritte

1. **Setup** (15 min)
   - Ordnerstruktur erstellen
   - `requirements.txt` (fastapi, uvicorn, pydantic)

2. **Core Server** (30 min)
   - FastAPI App mit Endpoints
   - Pydantic Models
   - Basis-Auth

3. **Task Queue** (30 min)
   - Async Verarbeitung mit asyncio.Queue
   - Status-Tracking
   - Persistence (JSON/ SQLite)

4. **Agent Bridge** (45 min)
   - Verbindung zu Kimi CLI
   - Task-Übergabe
   - Ergebnis-Rückgabe

5. **Negotiation** (30 min)
   - Verhandlungs-State-Machine
   - Proposal/Counter-Proposal

6. **Tailscale & Autostart** (20 min)
   - Windows Service Wrapper
   - Tailscale-IP Detection

7. **Integration Test** (10 min)
   - Test-Client Script
   - End-to-End Validierung

### 9. Verzeichnisstruktur

```
C:\Users\matth\.kimi\agent_api\
├── api/
│   ├── __init__.py
│   ├── server.py
│   ├── models.py
│   ├── auth.py
│   └── routes.py
├── core/
│   ├── __init__.py
│   ├── task_queue.py
│   ├── negotiation.py
│   └── bridge.py
├── config/
│   └── settings.yaml
├── data/
│   └── tasks.db
├── logs/
│   └── api.log
├── service/
│   └── install_service.ps1
├── test_client.py
├── requirements.txt
└── start_api.py
```

### 10. Beispiel-Nutzung

**Agent sendet Task:**
```bash
curl -X POST http://100.x.x.x:7777/tasks/submit \
  -H "Authorization: Bearer SECRET" \
  -d '{
    "agent_id": "agent-alpha",
    "task_type": "refactor",
    "title": "Clean up utils.py",
    "payload": {"file": "utils.py", "issues": [...]},
    "webhook_url": "http://100.x.x.x:8888/webhook"
  }'
```

**Kimi antwortet via Webhook:**
```json
{
  "task_id": "task-123",
  "status": "NEGOTIATING",
  "proposal": {
    "accepted": false,
    "counter_proposal": {
      "scope": "refactor nur Funktion X",
      "duration": 300
    }
  }
}
```

## Schätzung
- **Zeit:** ~3 Stunden
- **Komplexität:** Mittel
- **Risiken:** Windows Service Integration, Kimi CLI Bridge

## Offene Fragen
1. Soll Kimi im "Headless-Mode" laufen oder mit UI?
2. Wie wird Kimi gestartet - über `kimi.exe` direkt oder via Wrapper?
3. Brauchen wir Task-Priorisierung oder FIFO?
4. Soll es eine maximale Parallelität geben (1 Task gleichzeitig oder mehrere)?
