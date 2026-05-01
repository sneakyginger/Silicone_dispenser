import RPi.GPIO as GPIO
import time

pin = 7  # BOARD pin 12 = GPIO18, hardware PWM

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

pwm = GPIO.PWM(pin, 50)  # 50Hz = standard servo frequency
pwm.start(0)

def set_angle(angle):
    min_duty = 2.5   # duty cycle at 0°  → increase if servo doesn't reach full left
    max_duty = 12.5  # duty cycle at 180° → increase if servo doesn't reach full right
    duty = min_duty + (angle / 180) * (max_duty - min_duty)
    pwm.ChangeDutyCycle(duty)
    time.sleep(2)
    pwm.ChangeDutyCycle(0)


while True:
	print("heen")
	set_angle(0)
	time.sleep(1)
	print("weer")
	#set_angle(180)
	time.sleep(1)
