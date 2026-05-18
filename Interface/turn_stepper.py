"""Turn one stepper by 5000 steps and report the weight difference.

Run with:
    python3 turn_stepper.py <stepper>

Example:
    python3 turn_stepper.py 1
"""

import argparse
import minimal_dispenseN2


def parse_args():
    parser = argparse.ArgumentParser(
        description="Turn one stepper by 5000 steps and report the weight difference."
    )
    parser.add_argument(
        "stepper",
        type=int,
        choices=range(1, 5),
        help="Stepper motor to test (1-4).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    weight_before = minimal_dispenseN2.measure_weight()
    print(f"Weight before: {weight_before:.3f} g")

    servo_positions = [1, 1, 1, 1]
    servo_positions[args.stepper - 1] = 0
    minimal_dispenseN2.set_servos(servo_positions)
    minimal_dispenseN2.move_stepper(args.stepper, 5000)
    minimal_dispenseN2.set_servos([1, 1, 1, 1])

    weight_after = minimal_dispenseN2.measure_weight()
    print(f"Weight after:  {weight_after:.3f} g")

    print(f"Stepper:       {args.stepper}")
    print(f"Difference:    {weight_after - weight_before:+.3f} g")


if __name__ == "__main__":
    main()
