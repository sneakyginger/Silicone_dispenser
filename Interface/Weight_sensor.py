import RPi.GPIO as GPIO
from hx711 import HX711

def get_weight(dout_pin, pd_sck_pin, gain=128):
    try:
        hx711 = HX711(
            dout_pin=dout_pin,
            pd_sck_pin=pd_sck_pin,
            channel='A',
            gain=128
        )
        hx711.reset()   # Before we start, reset the HX711 (not obligate)
        measures = hx711.get_raw_data(num_measures=3)
        return measures
    finally:
        GPIO.cleanup()  # always do a GPIO cleanup in your scripts!

measures = get_weight(5,6)
print("\n".join(measures))
