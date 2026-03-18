# Bridge Fix — _run_kimi_with_task

## Problem
`_run_kimi_with_task` returned immediately with `{"status": "pending_kimi"}`.
Tasks got stuck in `processing` forever because nobody waited for the result file.

## Fix
Replace `_run_kimi_with_task` — add a polling loop that waits for `result_{task_id}.json`:

```python
async def _run_kimi_with_task(self, task_file, task_data):
    max_duration = task_data.get('max_duration', 300)
    task_id = task_data.get('id', task_file.stem.replace('task_', ''))

    # ... (keep existing pending_tasks.json write code) ...

    # ADDED: Poll for result file
    result_file = self.work_dir / ".kimi" / "agent_api" / "data" / f"result_{task_id}.json"
    deadline = asyncio.get_event_loop().time() + max_duration

    while asyncio.get_event_loop().time() < deadline:
        await asyncio.sleep(2)
        if result_file.exists():
            with open(result_file, 'r', encoding='utf-8') as f:
                result_data = json.load(f)
            result_file.unlink()  # cleanup
            return result_data.get('result', result_data)

    raise TimeoutError(f"Task {task_id} not completed within {max_duration}s")
```

## How results get written
Kimi must call `await bridge.submit_result(task_id, result_dict)` — OR —
write directly to `data/result_{task_id}.json`:

```json
{
  "task_id": "task-abc123",
  "result": {
    "summary": "Done",
    "output": "..."
  },
  "completed_at": "2026-03-18T22:00:00"
}
```

## Kimi's workflow
1. GET `/internal/next-task` → bekommt Task + Prompt
2. Task bearbeiten
3. Ergebnis schreiben nach `data/result_{task_id}.json`
4. Bridge erkennt die Datei automatisch (polling alle 2s)
5. Task → `completed` ✅
