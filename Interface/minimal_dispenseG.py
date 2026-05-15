"""Minimal dispense interface — fill in the body of multi_dispense.

Only the symbols below are referenced by other files (dispensing_job.py,
Interface_rpi.py). Anything beyond this is internal to your implementation.
"""

import time

import RPi.GPIO as GPIO

import scale_sensor


# --- Module attributes read or written by other files -----------------------

density_of_liquid = 1.06  # g/ml — read by dispensing_job and Interface_rpi
                          # (used to convert grams ↔ ml for bucket bookkeeping).

keyboard_weight_entry = False  # dispensing_job sets this to False before each job.
manual_sensor = keyboard_weight_entry  # backwards-compatible alias.


# --- Hardware pins / tuning -------------------------------------------------

STEPPER_PINS = [7, 11, 13, 15]   # BOARD pin per motor (1..4)
MF_PIN = 16                      # microstep-full pin
DIR_PIN = 18                     # direction pin
STEP_DELAY = 0.01                # seconds per microstep pulse

SERVO_PINS = [12, 32, 35, 33]    # BOARD pin per servo (1..4)
SERVO_ANGLE_DISPENSE = 90        # degrees for the "dispense" position
SERVO_ANGLE_MIX = 0              # degrees for the "mix" position


step_delay = 0.001  # in seconds, delay between each microstep pulse1 #max speed 0.000005


# --- Helpers available to your implementation -------------------------------

def measure_weight():
    """Return the current scale reading in grams."""
    if keyboard_weight_entry:
        return float(input("Enter current scale reading (g): "))
    return scale_sensor.read_weight()


def move_stepper(motor_id, microsteps):
    """Pulse stepper `motor_id` (1..4) for `microsteps` steps."""
    pin = STEPPER_PINS[motor_id - 1]
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(MF_PIN, GPIO.OUT); GPIO.output(MF_PIN, 1)
    GPIO.setup(DIR_PIN, GPIO.OUT); GPIO.output(DIR_PIN, 0)
    for _ in range(int(microsteps)):
        GPIO.output(pin, 1); time.sleep(STEP_DELAY / 2)
        GPIO.output(pin, 0); time.sleep(STEP_DELAY / 2)
    GPIO.output(MF_PIN, 0) # Disable steppers


def set_servos(positions):
    """Move the 4 servos. `positions` is a list of 4 ints: 0=dispense, 1=mix."""
    assert len(positions) == 4 and all(p in (0, 1) for p in positions)
    angles = [SERVO_ANGLE_DISPENSE if p == 0 else SERVO_ANGLE_MIX for p in positions]
    GPIO.setmode(GPIO.BOARD)
    pwms = []
    for pin in SERVO_PINS:
        GPIO.setup(pin, GPIO.OUT)
        pwm = GPIO.PWM(pin, 50)  # 50 Hz servo signal
        pwm.start(0)
        pwms.append(pwm)
    for pwm, angle in zip(pwms, angles):
        duty = 2.5 + (angle / 180) * (13.5 - 2.5)
        pwm.ChangeDutyCycle(duty)
    time.sleep(2)  # let servos physically reach their position
    for pwm in pwms:
        pwm.ChangeDutyCycle(0); pwm.stop()


# --- The one function other files call --------------------------------------

def multi_dispense(amounts, progress_callback=None, progress_interval=10):
    measured = [0.0, 0.0, 0.0, 0.0]
    for i in range(len(amounts)):
        if amounts[i] != 0:
            measured[i] = total_dispense_1comp(i + 1, float(amounts[i]), step_delay)
            if progress_callback is not None:
                progress_callback(i, measured[i])
    return measured


def total_dispense_1comp(bucket_id, weight,step_delay = 0.001):
    if weight > 5:
        step_delay = 0.005
    elif weight > 1:
        step_delay = 0.01
    else:
        step_delay = 0.1
    dispensed = dispense_and_measure(bucket_id, weight,step_delay)
    total_dispensed = dispensed
    print(dispensed)
    while(total_dispensed < weight-0.1):
        dispensed = dispense_and_measure(bucket_id, weight - total_dispensed,step_delay)
        total_dispensed += dispensed
        print(total_dispensed)
        if weight > 5:
            step_delay = 0.005
        elif weight > 1:
            step_delay = 0.01
        else:
            step_delay = 0.1
    return total_dispensed

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