import RPi.GPIO as GPIO
import time

pin = 7 # BOARD pin 12 = GPIO18, hardware PWM

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.OUT)

pwm = GPIO.PWM(pin, 50)  # 50Hz standard servo frequency
pwm.start(0)

def set_angle(angle):
    min_duty = 2.5
    max_duty = 12.0
    duty = min_duty + (angle / 180.0) * (max_duty - min_duty)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)

try:
    while True:
        print("heen")
        set_angle(0)
        time.sleep(1)
        print("weer")
        set_angle(180)
        time.sleep(1)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()