"""Reusable HX711 weight sensor access for the dispenser.

This intentionally does not import or modify Weight_sensor.py. That file can
stay as a standalone hardware test script.
"""
import numpy as np
from hx711 import HX711

grams  = [55.85,35.543, 22.245, 66.604+28.887]
counts = [880400, 560400,350800, 1505000]

slope, intercept = np.polyfit(counts, grams, 1)

print(f"Scale factor: {1/slope:,.1f} counts/g")
print(f"Zero offset:  {intercept:.4f}g")

DOUT_PIN = 29
PD_SCK_PIN = 31
READING_BYTE_FORMAT = "MSB"
READING_BIT_FORMAT = "MSB"
REFERENCE_UNIT = 1/slope
TARE_SAMPLES = 31
READ_SAMPLES = 31

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
