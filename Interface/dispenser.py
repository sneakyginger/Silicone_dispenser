import math
import time
import numpy as np

import RPi.GPIO as GPIO

import scale_sensor
GPIO.setmode(GPIO.BOARD)

control_pins = [7, 11, 13, 15]
MF_pin = 16  # BOARD pin number for the MF input input (RPi 4)
DIR_pin = 18  # BOARD pin number for the DIR input (RPi 4)

step_delay = 0.001  # in seconds, delay between each microstep pulse1 #max speed 0.000005

servo_pins = [12, 32, 35, 33]  # BOARD pin numbers for servos 1–4 (hardware PWM, RPi 5)

SERVO_ANGLE_DISPENSE = 90   # degrees — change here to recalibrate the dispense position
SERVO_ANGLE_MIX      = 0  # degrees — change here to recalibrate the mix position


comps_dispensed = [0, 0, 0, 0]  # in gram # for testing, to keep track of how much has been dispensed from each motor

density_of_liquid = 1.06  # in g/ml, density of the liquid being dispensed

tube_inner_diameter = 5  # in mm
tube_cross_section_area = math.pi * (tube_inner_diameter / 2) ** 2  # in mm^2
arm_length = 30  # in mm

microsteps_per_step = 1 
microsteps_per_revolution = 200 * microsteps_per_step  # 200 steps/rev with 16 microsteps

length_per_step = (arm_length * 2 * math.pi) / microsteps_per_revolution  # in mm
volume_per_step = length_per_step * tube_cross_section_area / 1000  # in ml


def total_dispense_1comp(bucket_id, weight,step_delay = 0.001):
    step_delay = np.interp(weight, [0, 100], [1, 0.0005])
    dispensed = dispense_and_measure(bucket_id, weight,step_delay)
    while(dispensed < weight-0.1):
        step_delay = np.interp(weight - dispensed, [0, 100], [1, 0.0005])
        dispensed = dispense_and_measure(bucket_id, weight - dispensed)
    return dispensed

def multi_dispense(amounts, progress_callback=None, progress_interval=10):
    measured = [0.0, 0.0, 0.0, 0.0]
    for i in range(len(amounts)):
        if amounts[i] != 0:
            measured[i] = total_dispense_1comp(i + 1, float(amounts[i]), step_delay)
            if progress_callback is not None:
                progress_callback(i, measured[i])
    return measured

def dispense_and_measure(bucket_id, weight,step_delay):
    tare_weight = scale_sensor.read_weight()
    dispense(bucket_id, weight,step_delay)
    time.sleep(5)
    measured_weight = scale_sensor.read_weight()
    net_weight = measured_weight - tare_weight
    return net_weight

def dispense(bucket_id, weight,step_delay):
    amount = weight / density_of_liquid  # convert weight to volume
    print(f"Dispensing bucket {bucket_id}, amount: {amount:.4f} ml")

    positions = [0 if i == bucket_id - 1 else 1 for i in range(4)]  # only this bucket's servo to dispense
    set_servo_positions(positions)

    move_motor(bucket_id, amount / volume_per_step, step_delay)

    set_servo_positions([1, 1, 1, 1])  # return all servos to mix position after dispensing

def move_motor(motor_id, steps, step_delay=0.001):
    assert motor_id in [1, 2, 3, 4], "Invalid motor ID. Must be 1, 2, 3, or 4."

    microsteps = int(steps * microsteps_per_step)
    pin = control_pins[motor_id - 1]
    print(f"Moving motor {motor_id} on pin {pin}: {microsteps} microsteps.")
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)
    GPIO.setup(MF_pin, GPIO.OUT)
    GPIO.output(MF_pin, 1)  # set MF high for microstepping
    GPIO.setup(DIR_pin, GPIO.OUT)
    GPIO.output(DIR_pin, 0)  # set direction (1 or 0 depending on desired direction)

    for i in range(microsteps):
        GPIO.output(pin, 1)
        time.sleep(step_delay / 2)
        GPIO.output(pin, 0)
        time.sleep(step_delay / 2)

def _angle_to_duty(angle):
    """Convert a servo angle in degrees to a PWM duty cycle percentage (for 50 Hz signal).
    """
    min_duty = 2.5   # duty cycle at 0°  → increase if servo doesn't reach full left
    max_duty = 13.5  # duty cycle at 180° → increase if servo doesn't reach full right
    return min_duty + (angle / 180) * (max_duty - min_duty)

def set_servo_positions(positions):
    assert len(positions) == 4, "Must provide exactly 4 positions."
    assert all(p in (0, 1) for p in positions), "Each position must be 0 (dispense) or 1 (mix)."


    angles = [SERVO_ANGLE_DISPENSE if p == 0 else SERVO_ANGLE_MIX for p in positions]

    for i, (pin, angle) in enumerate(zip(servo_pins, angles)):
        label = "dispense" if positions[i] == 0 else "mix"
        print(f"Servo {i+1} on pin {pin}: {label} ({angle}°)")

    GPIO.setmode(GPIO.BOARD)
    pwms = []
    for pin in servo_pins:
        GPIO.setup(pin, GPIO.OUT)
        pwm = GPIO.PWM(pin, 50)  # 50 Hz — standard servo frequency
        pwm.start(0)
        pwms.append(pwm)

    for pwm, angle in zip(pwms, angles):
        pwm.ChangeDutyCycle(_angle_to_duty(angle))

    time.sleep(2)  # allow servos to physically reach their position

    for pwm in pwms:
        pwm.ChangeDutyCycle(0)  # stop PWM signal to prevent jitter
        pwm.stop()