import RPI.GPIO as GPIO
from hx711 import HX711
GPIO.setmode(GPIO.BOARD)
hx = HX711(29, 31)
while True:
    print(hx.get_raw_data_mean())