import random
import math
import time

import RPi.GPIO as GPIO


RASPBERRY = True
# GPIO pins [7, 11, 13, 15] -> [26, 23, 33, 10]
#control_pins = [26, 23, 33, 10]  # BOARD pin numbers, one per motor
control_pins = [7, 11, 13, 15]

step_delay = 0.01  # in seconds, delay between each microstep pulse1

servo_pins = [12, 32, 35, 33]  # BOARD pin numbers for servos 1–4 (hardware PWM, RPi 5)

SERVO_ANGLE_DISPENSE = 0   # degrees — change here to recalibrate the dispense position
SERVO_ANGLE_MIX      = 90  # degrees — change here to recalibrate the mix position


comps_dispensed = [0, 0, 0, 0]  # in gram # for testing, to keep track of how much has been dispensed from each motor


# to simulate dispensing, we will add noise to the process
dispensing_noise_factor = 15/100  # in %,  noise in dispensing, for testing purposes

measurement_noise_factor = 0.04  # in g, noise in measurement, for testing purposes


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


def dispense_and_measure(component_id, amount):
    """Dispense a given weight and return the actually measured dispensed amount."""
    before = measure_weight()
    dispense(component_id, amount)
    return measure_weight() - before


def under_tolerance_components(measured_results, amounts, relative_tolerance, target_ratio=1.0):
    """Return list of (index, shortfall) for components below target_ratio * target by more than tolerance.

    target_ratio is the shared ratio all components should reach (e.g. the ratio of the most
    over-dispensed component). Each component's proportional target is amounts[i] * target_ratio,
    so all components are corrected to the same fraction of their individual targets rather than
    to their absolute targets independently.
    """
    return [
        (i, amounts[i] * target_ratio - measured)
        for i, (measured, _) in enumerate(zip(measured_results, amounts))
        if amounts[i] * target_ratio - measured > relative_tolerance
    ]


def biggest_ratio_difference(measured_results, amounts):
    """Return (i, j, ratios, diff_pct) for the pair of components with the biggest % ratio difference."""
    ratios = [measured / target for measured, target in zip(measured_results, amounts)]
    i = max(range(len(ratios)), key=lambda k: ratios[k])
    j = min(range(len(ratios)), key=lambda k: ratios[k])
    diff_pct = (ratios[i] - ratios[j]) * 100
    return i, j, ratios, diff_pct


def multi_dispense(amounts, relative_tolerance=0.1, correction_fraction=0.10, max_iterations=10):
    assert len(amounts) in (2, 4), "Must provide amounts for 2 or 4 motors."

    print("Dispensing multiple components:")
    for i, amount in enumerate(amounts):
        print(f"Component {i+1}: {amount} grams.")
    print("")

    # initial dispense pass
    measured_results = [dispense_and_measure(i + 1, amount) for i, amount in enumerate(amounts)]

    print("Measured weights after dispensing:")
    for i, measured in enumerate(measured_results):
        print(f"Component {i+1}: {measured:.3f} grams.")

    # warn about components whose ratio deviates from the most over-dispensed component
    ratios = [m / t for m, t in zip(measured_results, amounts)]
    max_ratio = max(ratios)
    for i, (measured, target) in enumerate(zip(measured_results, amounts)):
        shortfall_from_ratio = target * max_ratio - measured
        if shortfall_from_ratio > relative_tolerance:
            print(f"Warning: Component {i+1} is behind proportional target. "
                  f"Measured: {measured:.3f}g, Proportional target: {target * max_ratio:.3f}g "
                  f"(ratio {max_ratio:.4f}), shortfall: {shortfall_from_ratio:.3f}g.")

    # correction loop: top up components that are below the fixed target ratio
    # target_ratio is fixed once from the initial dispense — it must NOT be updated inside the loop,
    # otherwise any overshoot caused by noise would raise the target and trigger a runaway chain reaction
    target_ratio = max_ratio
    iterations_used = 0
    for iteration in range(max_iterations):
        to_correct = under_tolerance_components(measured_results, amounts, relative_tolerance, target_ratio=target_ratio)

        if not to_correct:
            print("All components within proportional tolerance.")
            break

        for i, shortfall in to_correct:
            correction = min(shortfall, amounts[i] * correction_fraction)
            print(f"Component {i+1}: shortfall {shortfall:.3f}g from proportional target, correcting by {correction:.3f}g.")
            measured_results[i] += dispense_and_measure(i + 1, correction)

        iterations_used += 1
    else:
        print("Warning: max correction iterations reached. Some components may still be out of proportional tolerance.")

    print(f"Total correction iterations used: {iterations_used}")

    # report biggest ratio difference
    i, j, ratios, max_diff_pct = biggest_ratio_difference(measured_results, amounts)
    print(f"Biggest % difference: Component {i+1} ({ratios[i]*100:.2f}% of target) vs Component {j+1} ({ratios[j]*100:.2f}% of target): {max_diff_pct:.2f}%")


def mix():
    print("Mixing components...")
    set_servo_positions([1, 1, 1, 1])  # set all to mix position
    multi_dispense([1000, 1000, 1000, 1000], relative_tolerance=1000000)  # mix by dispensing small amounts from each motor
    print("Mixing complete.")



def show_dispensed_amounts():
    print("")
    print("Dispensed amounts:")
    for i, amount in enumerate(comps_dispensed):
        print(f"Component {i+1}: {amount:.3f} grams.")


def measure_weight():
    noise = random.uniform(-measurement_noise_factor, measurement_noise_factor)
    return sum(comps_dispensed) + noise  # fixed absolute noise, not % of total


def dispense(component_id, weight):
    amount = weight / density_of_liquid  # convert weight to volume
    print(f"Dispensing component {component_id}, amount: {amount:.4f} ml")
    amount_with_noise = amount * (1 + random.uniform(-dispensing_noise_factor, dispensing_noise_factor))
    move_motor(component_id, amount_with_noise / volume_per_step)


def move_motor(motor_id, steps):
    assert motor_id in [1, 2, 3, 4], "Invalid motor ID. Must be 1, 2, 3, or 4."

    
    positions = [0 if i == motor_id - 1 else 1 for i in range(4)]  # only this motor's servo to dispense
    set_servo_positions(positions)

    microsteps = int(steps * microsteps_per_step)
    pin = control_pins[motor_id - 1]
    print(f"Moving motor {motor_id} on pin {pin}: {microsteps} microsteps.")

    if RASPBERRY:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

        for i in range(microsteps):
            GPIO.output(pin, 1)
            time.sleep(step_delay / 2)
            GPIO.output(pin, 0)
            time.sleep(step_delay / 2)

        GPIO.cleanup(pin)
    else:
        comps_dispensed[motor_id - 1] += steps * volume_per_step * density_of_liquid  # in gram
    
    
    set_servo_positions([1, 1, 1, 1])  # reset all to mix position


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

        GPIO.cleanup()


if __name__ == "__main__":
    main()
