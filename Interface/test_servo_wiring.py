"""Standalone servo wiring test.

This script does not import any dispenser code. It only uses RPi.GPIO to move
one servo back and forth, so it is useful for checking power, ground, signal
wiring, and the selected BOARD pin.

Run on the Raspberry Pi:

    python3 test_servo_wiring.py
    python3 test_servo_wiring.py --pin 12
"""

import argparse
import time

import RPi.GPIO as GPIO


def angle_to_duty(angle):
    min_duty = 2.5
    max_duty = 12.5
    return min_duty + (angle / 180.0) * (max_duty - min_duty)


def move_servo(pwm, angle, hold_time):
    print(f"Moving to {angle} degrees")
    pwm.ChangeDutyCycle(angle_to_duty(angle))
    time.sleep(hold_time)
    pwm.ChangeDutyCycle(0)


def main():
    parser = argparse.ArgumentParser(description="Move one servo back and forth.")
    parser.add_argument("--pin", type=int, default=12, help="BOARD pin connected to servo signal.")
    parser.add_argument("--cycles", type=int, default=5, help="Number of back-and-forth cycles.")
    parser.add_argument("--hold", type=float, default=1.0, help="Seconds to hold each position.")
    args = parser.parse_args()

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(args.pin, GPIO.OUT)
    pwm = GPIO.PWM(args.pin, 50)

    try:
        pwm.start(0)
        for cycle in range(1, args.cycles + 1):
            print(f"Cycle {cycle}/{args.cycles}")
            move_servo(pwm, 0, args.hold)
            time.sleep(0.3)
            move_servo(pwm, 90, args.hold)
            time.sleep(0.3)
            move_servo(pwm, 180, args.hold)
            time.sleep(0.3)
            move_servo(pwm, 90, args.hold)
            time.sleep(0.3)
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("Done. GPIO cleaned up.")


if __name__ == "__main__":
    main()
