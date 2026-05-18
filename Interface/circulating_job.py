"""Background circulation job state shared between the UI and hardware worker."""

import inspect
import threading
import time

import saved_settings


PROGRESS_UPDATE_SECONDS = 1

_lock = threading.Lock()
_state = {
    "running": False,
    "done": False,
    "error": "",
    "active": [False, False, False, False],
    "duration_seconds": 0.0,
    "elapsed": [0.0, 0.0, 0.0, 0.0],
    "started_at": 0.0,
    "finished_at": 0.0,
}
_thread = None


def snapshot():
    """Return a copy of the current circulation state for the pygame thread."""
    with _lock:
        return {
            "running": _state["running"],
            "done": _state["done"],
            "error": _state["error"],
            "active": list(_state["active"]),
            "duration_seconds": _state["duration_seconds"],
            "elapsed": list(_state["elapsed"]),
            "started_at": _state["started_at"],
            "finished_at": _state["finished_at"],
        }


def reset():
    """Clear a finished job before the next circulation request is prepared."""
    global _thread
    with _lock:
        if _state["running"]:
            return False
        _state["done"] = False
        _state["error"] = ""
        _state["active"] = [False, False, False, False]
        _state["duration_seconds"] = 0.0
        _state["elapsed"] = [0.0, 0.0, 0.0, 0.0]
        _state["started_at"] = 0.0
        _state["finished_at"] = 0.0
        _thread = None
    return True


def start(circulate_module):
    """Start one circulation job, returning False if another is running."""
    global _thread
    if not hasattr(circulate_module, "circulate"):
        return False

    density = getattr(circulate_module, "density_of_liquid", 1.0)
    active = [saved_settings.bucket_volume(i) * density > 0 for i in range(4)]
    duration_seconds = saved_settings.mixing_settings()["duration_minutes"] * 60

    with _lock:
        if _state["running"]:
            return False
        _state["running"] = True
        _state["done"] = False
        _state["error"] = ""
        _state["active"] = active
        _state["duration_seconds"] = float(duration_seconds)
        _state["elapsed"] = [0.0, 0.0, 0.0, 0.0]
        _state["started_at"] = time.time()
        _state["finished_at"] = 0.0

    _thread = threading.Thread(target=_run, args=(circulate_module,), daemon=True)
    _thread.start()
    return True


def _set_bucket_progress(bucket_index, elapsed_seconds):
    if bucket_index < 0 or bucket_index >= 4:
        return
    with _lock:
        _state["elapsed"][bucket_index] = max(0.0, float(elapsed_seconds or 0.0))


def _finish(error=""):
    with _lock:
        _state["error"] = error
        _state["running"] = False
        _state["done"] = True
        _state["finished_at"] = time.time()


def _run(circulate_module):
    try:
        if "progress_callback" in inspect.signature(circulate_module.circulate).parameters:
            circulate_module.circulate(
                progress_callback=_set_bucket_progress,
                progress_interval=PROGRESS_UPDATE_SECONDS,
            )
        else:
            circulate_module.circulate()
        _finish()
    except Exception as exc:
        _finish(error=str(exc))
