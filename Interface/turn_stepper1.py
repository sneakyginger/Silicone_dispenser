"""Turn stepper 1 by 5000 steps and report the weight difference."""

import dispense_minimal


def main():
    weight_before = dispense_minimal.measure_weight()
    print(f"Weight before: {weight_before:.3f} g")

    dispense_minimal.set_servos([0, 1, 1, 1])
    dispense_minimal.move_stepper(1, 5000)
    dispense_minimal.set_servos([1, 1, 1, 1])

    weight_after = dispense_minimal.measure_weight()
    print(f"Weight after:  {weight_after:.3f} g")

    print(f"Difference:    {weight_after - weight_before:+.3f} g")


if __name__ == "__main__":
    main()
