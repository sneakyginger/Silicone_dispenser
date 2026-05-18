"""Turn one stepper by 5000 steps and report the weight difference."""

import argparse
import dispense_minimal


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

    weight_before = dispense_minimal.measure_weight()
    print(f"Weight before: {weight_before:.3f} g")

    servo_positions = [1, 1, 1, 1]
    servo_positions[args.stepper - 1] = 0
    dispense_minimal.set_servos(servo_positions)
    dispense_minimal.move_stepper(args.stepper, 5000)
    dispense_minimal.set_servos([1, 1, 1, 1])

    weight_after = dispense_minimal.measure_weight()
    print(f"Weight after:  {weight_after:.3f} g")

    print(f"Stepper:       {args.stepper}")
    print(f"Difference:    {weight_after - weight_before:+.3f} g")


if __name__ == "__main__":
    main()
