"""Diagnostic tests for the dispenser control path.

Run on the Raspberry Pi from the Interface directory:

    python3 test_dispense_code.py servo
    python3 test_dispense_code.py flow

The servo test repeatedly calls the existing dispense.set_servo_positions()
function. The flow test calls dispense.multi_dispense() while replacing the
manual scale prompt with a simulated measurement, so it should not block on
input().
"""

import argparse
import time

import dispense


def test_servos(cycles, pause):
    """Move each servo to dispense and back to mix several times."""
    print("Starting servo repeat test.")
    print("If the first move works but later moves do not, inspect PWM reuse/cleanup.")

    for cycle in range(1, cycles + 1):
        print(f"\nCycle {cycle}/{cycles}")
        for servo_index in range(4):
            positions = [1, 1, 1, 1]
            positions[servo_index] = 0

            print(f"Servo {servo_index + 1}: dispense")
            dispense.set_servo_positions(positions)
            time.sleep(pause)

            print(f"Servo {servo_index + 1}: mix")
            dispense.set_servo_positions([1, 1, 1, 1])
            time.sleep(pause)

    print("\nServo repeat test complete.")


def test_flow(amounts):
    """Run multi_dispense without blocking on manual scale input."""
    print("Starting non-blocking dispense flow test.")
    print("This monkey-patches measure_weight() for this test process only.")
    print("If this continues past the first movement, manual input was likely the blocker.")

    measured_total = 0.0

    def fake_measure_weight():
        return measured_total

    original_measure_weight = dispense.measure_weight
    original_move_motor = dispense.move_motor
    original_manual_sensor = dispense.manual_sensor

    def tracked_move_motor(motor_id, steps):
        nonlocal measured_total
        original_move_motor(motor_id, steps)
        measured_total += steps * dispense.volume_per_step * dispense.density_of_liquid

    try:
        dispense.manual_sensor = False
        dispense.measure_weight = fake_measure_weight
        dispense.move_motor = tracked_move_motor
        result = dispense.multi_dispense(amounts)
    finally:
        dispense.measure_weight = original_measure_weight
        dispense.move_motor = original_move_motor
        dispense.manual_sensor = original_manual_sensor

    print("\nFlow test complete.")
    print(f"Measured result returned by multi_dispense(): {result}")


def main():
    parser = argparse.ArgumentParser(description="Test dispenser servo and dispense code paths.")
    parser.add_argument(
        "mode",
        choices=("servo", "flow"),
        help="servo = repeated servo movements, flow = non-blocking multi_dispense path",
    )
    parser.add_argument("--cycles", type=int, default=2, help="Servo test cycles.")
    parser.add_argument("--pause", type=float, default=0.5, help="Pause between servo commands.")
    parser.add_argument(
        "--amounts",
        type=float,
        nargs=4,
        default=[1.0, 1.0, 0.0, 0.0],
        help="Four component amounts in grams for the flow test.",
    )
    args = parser.parse_args()

    if args.mode == "servo":
        test_servos(args.cycles, args.pause)
    else:
        test_flow(args.amounts)


if __name__ == "__main__":
    main()
