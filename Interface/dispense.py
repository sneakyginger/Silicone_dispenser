import random
import math
import time

import RPi.GPIO as GPIO

import scale_sensor


RASPBERRY = True
# GPIO pins [7, 11, 13, 15] -> [26, 23, 33, 10]
#control_pins = [26, 23, 33, 10]  # BOARD pin numbers, one per motor
control_pins = [7, 11, 13, 15]
MF_pin = 16  # BOARD pin number for the MF input input (RPi 4)
DIR_pin = 18  # BOARD pin number for the DIR input (RPi 4)

step_delay = 0.01  # in seconds, delay between each microstep pulse1

servo_pins = [12, 32, 35, 33]  # BOARD pin numbers for servos 1–4 (hardware PWM, RPi 5)

SERVO_ANGLE_DISPENSE = 90   # degrees — change here to recalibrate the dispense position
SERVO_ANGLE_MIX      = 0  # degrees — change here to recalibrate the mix position


comps_dispensed = [0, 0, 0, 0]  # in gram # for testing, to keep track of how much has been dispensed from each motor

keyboard_weight_entry = False  # if True, prompts the user to enter the scale reading manually in the CLI

manual_sensor = keyboard_weight_entry  # backwards-compatible alias for tests and older scripts

# to simulate dispensing, we will add noise to the process
dispensing_noise_factor = 0*15/100  # in %,  noise in dispensing, for testing purposes

measurement_noise_factor = 0*0.04  # in g, noise in measurement, for testing purposes


density_of_liquid = 1.06  # in g/ml, density of the liquid being dispensed


tube_inner_diameter = 3  # in mm
tube_cross_section_area = math.pi * (tube_inner_diameter / 2) ** 2  # in mm^2
arm_length = 60  # in mm

microsteps_per_step = 1  # 16
microsteps_per_revolution = 200 * microsteps_per_step  # 200 steps/rev with 16 microsteps


length_per_step = (arm_length * 2 * math.pi) / microsteps_per_revolution  # in mm
volume_per_step = length_per_step * tube_cross_section_area / 1000  # in ml


def main():

    print("")
    print("Starting multi dispensing...")
    print("")

    multi_dispense([10, 20, 30, 40])  # dispense 10g from motor 1, 20g from motor 2, 30g from motor 3, 40g from motor 4
    #multi_dispense([100, 100, 100, 100]) 
    show_dispensed_amounts()


def dispense_and_measure(bucket_id, amount, progress_callback=None, progress_interval=10):
    """Dispense a given weight and return the actually measured dispensed amount."""
    before = measure_weight()
    last_progress_at = 0

    def report_progress():
        nonlocal last_progress_at
        now = time.time()
        if now - last_progress_at < progress_interval:
            return
        last_progress_at = now
        if progress_callback is None:
            return
        try:
            progress_callback(bucket_id - 1, measure_weight() - before)
        except Exception as exc:
            print(f"Warning: progress weight read failed for bucket {bucket_id}: {exc}")

    dispense(bucket_id, amount, progress_callback=report_progress)
    time.sleep(2)
    measured = measure_weight() - before
    if progress_callback is not None:
        progress_callback(bucket_id - 1, measured)
    return measured


def biggest_ratio_difference(measured_results, amounts):
    """Return (i, j, ratios, diff_pct) for the pair of active buckets with the biggest % ratio difference.

    Buckets with amounts == 0 are excluded. Returns None if fewer than two buckets were active.
    """
    active = [(k, m / t) for k, (m, t) in enumerate(zip(measured_results, amounts)) if t > 0]
    if len(active) < 2:
        return None
    ratios_by_index = dict(active)
    i = max(ratios_by_index, key=ratios_by_index.get)
    j = min(ratios_by_index, key=ratios_by_index.get)
    diff_pct = (ratios_by_index[i] - ratios_by_index[j]) * 100
    return i, j, ratios_by_index, diff_pct


def multi_dispense(amounts, relative_tolerance=0.1, safety_factor=0.95, max_iterations=10,
                   progress_callback=None, progress_interval=10):
    assert len(amounts) in (2, 4), "Must provide amounts for 2 or 4 motors."

    active = [i for i, a in enumerate(amounts) if a > 0]
    if not active:
        print("No buckets requested — nothing to dispense.")
        return [0.0] * len(amounts)

    print("Dispensing multiple buckets:")
    for i in active:
        print(f"Bucket {i+1}: {amounts[i]} grams.")
    print("")

    measured = [0.0] * len(amounts)
    for i in active:
        measured[i] = dispense_and_measure(
            i + 1,
            amounts[i],
            progress_callback=progress_callback,
            progress_interval=progress_interval,
        )

    print("Measured weights after initial dispense:")
    for i in active:
        print(f"Bucket {i+1}: {measured[i]:.3f} g (ratio {measured[i]/amounts[i]:.4f})")

    iterations_used = 0
    for iterations_used in range(1, max_iterations + 1):
        target_ratio = max(measured[i] / amounts[i] for i in active)

        to_correct = [
            (i, amounts[i] * target_ratio - measured[i])
            for i in active
            if amounts[i] * target_ratio - measured[i] > relative_tolerance
        ]
        if not to_correct:
            print(f"All buckets within proportional tolerance after {iterations_used - 1} correction pass(es).")
            break

        for i, shortfall in to_correct:
            # safety_factor < 1 biases toward slight undershoot, so an overshoot from noise
            # only nudges target_ratio up by ~noise size — no runaway chain reaction.
            correction = shortfall * safety_factor
            print(f"Bucket {i+1}: shortfall {shortfall:.3f}g (target ratio {target_ratio:.4f}), "
                  f"correcting by {correction:.3f}g.")
            measured_before_correction = measured[i]

            def report_correction_progress(bucket_index, grams, _before=measured_before_correction):
                if progress_callback is not None:
                    progress_callback(bucket_index, _before + grams)

            measured[i] += dispense_and_measure(
                i + 1,
                correction,
                progress_callback=report_correction_progress,
                progress_interval=progress_interval,
            )
            if progress_callback is not None:
                progress_callback(i, measured[i])
    else:
        print("Warning: max correction iterations reached. Some buckets may still be out of proportional tolerance.")

    print(f"Total correction iterations used: {iterations_used}")

    result = biggest_ratio_difference(measured, amounts)
    if result is not None:
        i, j, ratios, max_diff_pct = result
        print(f"Biggest % difference: Bucket {i+1} ({ratios[i]*100:.2f}% of target) vs "
              f"Bucket {j+1} ({ratios[j]*100:.2f}% of target): {max_diff_pct:.2f}%")

    return measured


def mix(rotations=10):
    """Run all motors in mix position for a given number of rotations."""
    print("Mixing components...")
    set_servo_positions([1, 1, 1, 1])  # all servos in mix position — stays throughout
    steps = rotations * microsteps_per_revolution
    for motor_id in range(1, 5):
        move_motor(motor_id, steps)  # move_motor is servo-agnostic, servos stay in mix
    print("Mixing complete.")



def show_dispensed_amounts():
    print("")
    print("Dispensed amounts:")
    for i, amount in enumerate(comps_dispensed):
        print(f"Bucket {i+1}: {amount:.3f} grams.")


def measure_weight():
    if keyboard_weight_entry:
        return float(input("Enter current scale reading (g): "))
    return scale_sensor.read_weight()


def dispense(bucket_id, weight, progress_callback=None):
    amount = weight / density_of_liquid  # convert weight to volume
    print(f"Dispensing bucket {bucket_id}, amount: {amount:.4f} ml")

    positions = [0 if i == bucket_id - 1 else 1 for i in range(4)]  # only this bucket's servo to dispense
    set_servo_positions(positions)

    amount_with_noise = amount * (1 + random.uniform(-dispensing_noise_factor, dispensing_noise_factor))
    try:
        move_motor(bucket_id, amount_with_noise / volume_per_step, progress_callback=progress_callback)
    finally:
        set_servo_positions([1, 1, 1, 1])  # return all servos to mix position after dispensing


def move_motor(motor_id, steps, progress_callback=None):
    assert motor_id in [1, 2, 3, 4], "Invalid motor ID. Must be 1, 2, 3, or 4."

    microsteps = int(steps * microsteps_per_step)
    pin = control_pins[motor_id - 1]
    print(f"Moving motor {motor_id} on pin {pin}: {microsteps} microsteps.")

    if RASPBERRY:
        GPIO.setmode(GPIO.BOARD)
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
            if progress_callback is not None:
                progress_callback()

    else:
        comps_dispensed[motor_id - 1] += steps * volume_per_step * density_of_liquid  # in gram
        if progress_callback is not None:
            progress_callback()


def _angle_to_duty(angle):
    """Convert a servo angle in degrees to a PWM duty cycle percentage (for 50 Hz signal).

    Standard mapping: 2.5% = 0°, 7.5% = 90°, 12.5% = 180°.
    Adjust min_duty/max_duty here if the servo doesn't reach its physical limits.
    """
    min_duty = 2.5   # duty cycle at 0°  → increase if servo doesn't reach full left
    max_duty = 12.5  # duty cycle at 180° → increase if servo doesn't reach full right
    return min_duty + (angle / 180) * (max_duty - min_duty)


def set_servo_positions(positions):
    """
    Move all 4 servos to the requested positions.

    Each servo can be in one of two positions:
        0 — dispense: routes liquid toward the dispensing outlet
        1 — mix:      routes liquid toward the mixing chamber

    The angles used for each position are defined by the module-level constants
    SERVO_ANGLE_DISPENSE and SERVO_ANGLE_MIX and can be adjusted there to
    recalibrate the physical positions without changing this function.

    Parameters
    ----------
    positions : list[int]
        A list of exactly 4 integers (0 or 1), one per servo, in order:
        [servo_1, servo_2, servo_3, servo_4].

    Raises
    ------
    AssertionError
        If the list does not contain exactly 4 elements, or if any element
        is not 0 or 1.

    Example
    -------
        set_servo_positions([0, 1, 0, 1])
        # Servo 1 → dispense, Servo 2 → mix,
        # Servo 3 → dispense, Servo 4 → mix
    """
    assert len(positions) == 4, "Must provide exactly 4 positions."
    assert all(p in (0, 1) for p in positions), "Each position must be 0 (dispense) or 1 (mix)."


    angles = [SERVO_ANGLE_DISPENSE if p == 0 else SERVO_ANGLE_MIX for p in positions]

    for i, (pin, angle) in enumerate(zip(servo_pins, angles)):
        label = "dispense" if positions[i] == 0 else "mix"
        print(f"Servo {i+1} on pin {pin}: {label} ({angle}°)")

    if RASPBERRY:
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



if __name__ == "__main__":
    main()
