# python -m venv dispenser_venv
# dispenser_venv\Scripts\activate
# py dispense.py

# code for on raspberry pi to control stepper motor for dispensing liquid

#import RPi.GPIO as GPIO
import time

RASPBERRY = False
TESTING = True

density_of_liquid = 1.06


tube_inner_diameter = 3  # in mm
tube_cross_section_area = 3.14159265 * (tube_inner_diameter / 2) ** 2  # in mm^2
arm_length = 60  # in mm

microsteps_per_step = 1 # 16
microsteps_per_revolution = 200 * microsteps_per_step  # 200 steps/rev with 16 microsteps


length_per_step = (arm_length * 2 * 3.14159265) / microsteps_per_revolution  # in mm
volume_per_step = length_per_step * tube_cross_section_area / 1000  # in ml

dispense_measure_delay = 3  # in s, time to wait after dispensing before measuring the amount dispensed
dispense_tolerance = 0.1  # in ml, acceptable tolerance for dispensing

max_dispensing_rounds = 3



weight_variable = 0 # for testing



def main():
    dispense(10, 1)  # dispense 10 ml from motor 1
    dispense(20, 2)  # dispense 20 ml from motor 2
    dispense(30, 3)  # dispense 30 ml from motor 3
    dispense(40, 4)  # dispense 40 ml from motor 4

    time.sleep(5)  # wait for 5 seconds before multi dispensing

    print("")
    print("Starting multi dispensing...")
    print("")

    multi_dispense([10, 20, 30, 40])  # dispense 10 ml from motor 1, 20 ml from motor 2, 30 ml from motor 3, and 40 ml from motor 4 simultaneously



def multi_dispense(amounts):
    assert(len(amounts) == 4), "Must provide amounts for all 4 motors."

    amounts_dispensed = [0, 0, 0, 0]  # initialize amounts dispensed for each motor
    done = False
    too_much_factor = 1

    for round in range(max_dispensing_rounds):
        if not done:
            for i, amount in enumerate(amounts):
                amounts_dispensed[i] += dispense(amount, i+1)  # dispense from motor i+1
                done = True
                if amounts_dispensed[i] > amount + dispense_tolerance or amounts_dispensed[i] < amount - dispense_tolerance:
                    done = False
                    too_much_now_factor = amounts_dispensed[i] / amount
                    if too_much_now_factor > too_much_factor:
                        too_much_factor = too_much_now_factor
                    amounts = [amount * too_much_factor for amount in amounts]  # adjust amounts for next round based on how much was dispensed in this round
                
        

def dispense(amount, motor_id):
    print(f"Dispensing {amount} ml of product {motor_id}.")
    dispense_speed = 1  # ml/s


    amount_dispensed = 0

    while amount_dispensed < amount - dispense_tolerance:
        measured_weight = measure_weight()
        steps_needed = int(amount / volume_per_step)
        time_needed = amount / dispense_speed  # in seconds
        move_motor(steps_needed, time_needed, motor_id)  # move motor for the required time to dispense the required amount
        time.sleep(dispense_measure_delay)

        amount_dispensed += measure_weight() - measured_weight  # update the amount dispensed based on weight measurement
        print(f"Amount dispensed: {amount_dispensed:.2f} ml")

    return amount_dispensed


def measure_weight():
    return weight_variable  # in grams, placeholder for actual weight measurement code


def move_motor(steps, time_used, motor_id):
    assert(motor_id in [1, 2, 3, 4]), "Invalid motor ID. Must be 1, 2, 3, or 4."
    print(f"Moving motor {steps} steps over {time_used} seconds.")
    # use microstepping
    microsteps = steps * microsteps_per_step
    time_per_step = time_used / microsteps
    print(f"Microstepping: {microsteps} microsteps.")



    if RASPBERRY:
        GPIO.setmode(GPIO.BOARD)
    control_pins = [7,11,13,15]
    for pin in control_pins:
        if RASPBERRY:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)



    
    if RASPBERRY:
        for i in range(microsteps):
            if RASPBERRY:
                GPIO.output(control_pins[motor_id-1], 1)
            else:
                print(f"Step motor on pin {control_pins[motor_id-1]} {i+1}/{microsteps}")
            time.sleep(time_per_step/2)
            if RASPBERRY:
                GPIO.output(control_pins[motor_id-1], 0)
            else:
                print(f"Step motor on pin {control_pins[motor_id-1]} {i+1}/{microsteps}")
            time.sleep(time_per_step/2)
    else:
        print(f"Step motor on pin {control_pins[motor_id-1]} {microsteps} times")
    
    if RASPBERRY:
        GPIO.cleanup()


    if TESTING:
        global weight_variable
        weight_variable += steps * volume_per_step * density_of_liquid




if __name__ == "__main__":
    main()