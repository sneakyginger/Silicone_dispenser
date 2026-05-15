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
STEP_DELAY = 0.003                # seconds per microstep pulse
MICROSTEPS_PER_GRAM = 82.47      # calibrated: 5000 steps → 60.627 g
MIN_STEPS = 40                   # minimum microsteps per pulse to overcome pump backlash

SERVO_PINS = [12, 32, 35, 33]    # BOARD pin per servo (1..4)
SERVO_ANGLE_DISPENSE = 90        # degrees for the "dispense" position
SERVO_ANGLE_MIX = 0              # degrees for the "mix" position


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


_servo_pwms = None

def set_servos(positions):
    """Move the 4 servos. `positions` is a list of 4 ints: 0=dispense, 1=mix."""
    assert len(positions) == 4 and all(p in (0, 1) for p in positions)
    angles = [SERVO_ANGLE_DISPENSE if p == 0 else SERVO_ANGLE_MIX for p in positions]
    global _servo_pwms
    if _servo_pwms is None:
        GPIO.setmode(GPIO.BOARD)
        _servo_pwms = []
        for pin in SERVO_PINS:
            GPIO.setup(pin, GPIO.OUT)
            _servo_pwms.append(GPIO.PWM(pin, 50))  # 50 Hz servo signal
    for i, (pwm, angle, p) in enumerate(zip(_servo_pwms, angles, positions), start=1):
        duty = 2.5 + (angle / 180) * (13.5 - 2.5)
        pwm.start(duty)
        action = "opening (dispense)" if p == 0 else "closing (mix)"
    time.sleep(2)  # let servos physically reach their position
    for pwm in _servo_pwms:
        pwm.stop()  # fully halt PWM thread; restarted next call via .start()


# --- The one function other files call --------------------------------------

def multi_dispense(amounts, progress_callback=None, progress_interval=10):
    # Report progress to the UI by calling, at most once per `progress_interval` seconds:
    #     progress_callback(component_index, grams_dispensed_so_far)
    for i, amount in enumerate(amounts):
        if amount > 0:
            dispense_1comp(i + 1, amount, progress_callback)
        else:
            print(f"    (skipping bucket {i + 1}, amount={amount})")


def dispense_1comp(bucket_id, amount, progress_callback=None, progress_interval=10):
    # First pulse dispenses ~50% of `amount` using the default calibration,
    # then we recompute steps-per-gram from the actual delta and use that
    # for the rest of this call.
    print(f"\n>>> dispense_1comp called: bucket={bucket_id}, amount={amount} g")

    start_weight = measure_weight()
    target = start_weight + amount
    last_report = 0.0
    print(f"    start_weight={start_weight:.3f} g, target={target:.3f} g")

    positions = [1, 1, 1, 1]
    positions[bucket_id - 1] = 0
    set_servos(positions)

    # --- Calibration pulse: dispense ~50% using the default rate ---
    cal_steps = max(MIN_STEPS, int(amount * 0.5 * MICROSTEPS_PER_GRAM))
    print(f"calibration pulse: motor {bucket_id} for {cal_steps} microsteps (~50% of {amount:.2f} g)")
    move_stepper(bucket_id, cal_steps)

    positions = [1, 1, 1, 1]
    set_servos(positions)
    after_cal = measure_weight()
    positions[bucket_id - 1] = 0
    set_servos(positions)

    delta = after_cal - start_weight
    if delta > 0.01:
        steps_per_gram = cal_steps / delta
        print(f"    calibrated: {delta:.3f} g in {cal_steps} steps -> {steps_per_gram:.2f} steps/g (default {MICROSTEPS_PER_GRAM})")
    else:
        steps_per_gram = MICROSTEPS_PER_GRAM
        print(f"    calibration pulse dispensed too little ({delta:.3f} g); falling back to default {MICROSTEPS_PER_GRAM} steps/g")

    while True:
        positions = [1, 1, 1, 1]
        set_servos(positions)
        current = measure_weight()
        positions[bucket_id - 1] = 0
        set_servos(positions)
        remaining = target - current
        if remaining <= 0.05:
            positions = [1, 1, 1, 1]
            set_servos(positions)
            print(f"Finished dispensing component {bucket_id}: target={target:.2f} g, actual={current:.2f} g")
            break
        steps = max(MIN_STEPS, int(remaining * 0.8 * steps_per_gram))
        print(f"moving motor {bucket_id} for {steps} microsteps (remaining: {remaining:.2f} g)")
        move_stepper(bucket_id, steps)

        now = time.monotonic()
        if progress_callback and (now - last_report) >= progress_interval:
            progress_callback(bucket_id - 1, current - start_weight)
            last_report = now

    if progress_callback:
        progress_callback(bucket_id - 1, measure_weight() - start_weight)