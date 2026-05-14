"""Simple live test for the shared scale_sensor implementation."""

import time

import scale_sensor


def main():
    print("Scale sensor test")
    print("Keep the scale empty. Taring...")
    scale_sensor.tare_scale()
    print("Tare done. Add/remove weight. Press Ctrl+C to stop.")

    while True:
        print(f"{scale_sensor.read_weight():.2f} g")
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")
