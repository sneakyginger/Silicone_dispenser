import time
import RPi.GPIO as GPIO
pin = 11
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

while True:
	print(0)
	GPIO.output(pin, 0)
	time.sleep(0.001)
	print(1)
	GPIO.output(pin, 1)
	time.sleep(0.001)
