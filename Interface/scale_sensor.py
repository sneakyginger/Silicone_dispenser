"""Reusable HX711 weight sensor access for the dispenser.

This intentionally does not import or modify Weight_sensor.py. That file can
stay as a standalone hardware test script.
"""

from hx711 import HX711


DOUT_PIN = 29
PD_SCK_PIN = 31
READING_BYTE_FORMAT = "MSB"
READING_BIT_FORMAT = "MSB"
REFERENCE_UNIT = 2141725 / 165
TARE_SAMPLES = 15
READ_SAMPLES = 3

_hx = None


def init_scale():
    """Initialize and tare the HX711 once, then reuse it for all readings."""
    global _hx
    if _hx is None:
        _hx = HX711(DOUT_PIN, PD_SCK_PIN)
        _hx.set_reading_format(READING_BYTE_FORMAT, READING_BIT_FORMAT)
        _hx.set_reference_unit(REFERENCE_UNIT)
        _hx.reset()
        _hx.tare(TARE_SAMPLES)
    return _hx


def read_weight(samples=READ_SAMPLES):
    """Return the current scale reading in grams."""
    return init_scale().get_weight(samples)


def tare_scale(samples=TARE_SAMPLES):
    """Tare the already initialized scale, or initialize it first."""
    init_scale().tare(samples)
