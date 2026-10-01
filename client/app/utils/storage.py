import json
from pathlib import Path

STATE_FILE = Path.home() / ".mystoreapp.json"


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_worker():
    return load_state().get("worker")


def set_worker(worker):
    s = load_state()
    s["worker"] = worker
    save_state(s)


def clear_worker():
    s = load_state()
    s.pop("worker", None)
    save_state(s)
