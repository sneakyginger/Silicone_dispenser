"""Background dispensing job state shared between the UI and hardware worker."""

import threading
import time
import inspect

import saved_settings


PROGRESS_UPDATE_SECONDS = 10

_lock = threading.Lock()
_state = {
    "running": False,
    "done": False,
    "error": "",
    "desired": [0.0, 0.0, 0.0, 0.0],
    "dispensed": [0.0, 0.0, 0.0, 0.0],
    "started_at": 0.0,
    "finished_at": 0.0,
}
_thread = None


def snapshot():
    """Return a copy of the current dispensing state for the pygame thread."""
    with _lock:
        return {
            "running": _state["running"],
            "done": _state["done"],
            "error": _state["error"],
            "desired": list(_state["desired"]),
            "dispensed": list(_state["dispensed"]),
            "started_at": _state["started_at"],
            "finished_at": _state["finished_at"],
        }


def is_running():
    """Return True while the physical dispensing worker is active."""
    with _lock:
        return _state["running"]


def reset():
    """Clear a finished job before the next dispense request is prepared."""
    global _thread
    with _lock:
        if _state["running"]:
            return False
        _state["done"] = False
        _state["error"] = ""
        _state["desired"] = [0.0, 0.0, 0.0, 0.0]
        _state["dispensed"] = [0.0, 0.0, 0.0, 0.0]
        _state["started_at"] = 0.0
        _state["finished_at"] = 0.0
        _thread = None
    return True


def start(amounts, dispense_module):
    """Start one physical dispense job, returning False if another is running."""
    global _thread
    desired = [float(amount or 0.0) for amount in amounts]
    with _lock:
        if _state["running"]:
            return False
        _state["running"] = True
        _state["done"] = False
        _state["error"] = ""
        _state["desired"] = desired
        _state["dispensed"] = [0.0, 0.0, 0.0, 0.0]
        _state["started_at"] = time.time()
        _state["finished_at"] = 0.0

    _thread = threading.Thread(target=_run, args=(desired, dispense_module), daemon=True)
    _thread.start()
    return True


def _set_component_progress(component_index, grams):
    if component_index < 0 or component_index >= 4:
        return
    with _lock:
        _state["dispensed"][component_index] = max(0.0, float(grams or 0.0))


def _finish(measured=None, error=""):
    with _lock:
        if measured is not None:
            measured_values = list(measured)[:4]
            while len(measured_values) < 4:
                measured_values.append(0.0)
            for i, grams in enumerate(measured_values):
                _state["dispensed"][i] = max(0.0, float(grams or 0.0))
        _state["error"] = error
        _state["running"] = False
        _state["done"] = True
        _state["finished_at"] = time.time()


def _run(amounts, dispense_module):
    try:
        if hasattr(dispense_module, "keyboard_weight_entry"):
            dispense_module.keyboard_weight_entry = False
        if hasattr(dispense_module, "manual_sensor"):
            dispense_module.manual_sensor = False

        if "progress_callback" in inspect.signature(dispense_module.multi_dispense).parameters:
            measured = dispense_module.multi_dispense(
                amounts,
                progress_callback=_set_component_progress,
                progress_interval=PROGRESS_UPDATE_SECONDS,
            )
        else:
            measured = dispense_module.multi_dispense(amounts)

        if measured is None:
            measured = snapshot()["dispensed"]
        saved_settings.decrement_bucket_volumes(measured, dispense_module.density_of_liquid)
        _finish(measured=measured)
    except Exception as exc:
        _finish(error=str(exc))
