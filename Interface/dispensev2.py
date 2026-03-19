import random


comps_dispensed = [0, 0, 0, 0]  # in gram # for testing, to keep track of how much has been dispensed from each motor


# to simulate dispensing, we will add noise to the process
dispensing_noise_factor = 0.10  # 5% noise in dispensing, for testing purposes

measurement_noise_factor = 0.03  # 1% noise in measurement, for testing purposes


density_of_liquid = 1.06 # in g/ml, density of the liquid being dispensed


tube_inner_diameter = 3  # in mm
tube_cross_section_area = 3.14159265 * (tube_inner_diameter / 2) ** 2  # in mm^2
arm_length = 60  # in mm

microsteps_per_step = 1 # 16
microsteps_per_revolution = 200 * microsteps_per_step  # 200 steps/rev with 16 microsteps


length_per_step = (arm_length * 2 * 3.14159265) / microsteps_per_revolution  # in mm
volume_per_step = length_per_step * tube_cross_section_area / 1000  # in ml


def main():

    print("")
    print("Starting multi dispensing...")
    print("")

    multi_dispense([10, 20, 30, 40])  # dispense 10 grams from motor 1, 20 grams from motor 2, 30 grams from motor 3, and 40 grams from motor 4 simultaneously
    show_dispensed_amounts()



def multi_dispense(amounts, relative_tolerance=0.1):
    assert(len(amounts) == 4 or len(amounts) == 2), "Must provide amounts for all 4 motors or 2 motors."

    print("Dispensing multiple components:")
    for i, amount in enumerate(amounts):
        print(f"Component {i+1}: {amount} grams.")
    print("")

    measured_results = [0, 0, 0, 0] # measured weight of each component
    last_measurement = 0

    for i, amount in enumerate(amounts):
        last_measurement = measure_weight()  # measure weight before dispensing
        dispense(i+1, amount)  # dispense from motor i+1
        measured_results[i] = measure_weight() - last_measurement  # measure weight of each component seperately
    
    print("Measured weights after dispensing:")
    for i, measured in enumerate(measured_results):
        print(f"Component {i+1}: {measured} grams.")


    # check if the measured weights are within the relative tolerance of the target amounts
    for i, (measured, target) in enumerate(zip(measured_results, amounts)):
        if abs(measured - target) > relative_tolerance:
            print(f"Warning: Component {i+1} is outside the relative tolerance of {relative_tolerance}g. Measured: {measured} grams, Target: {target} grams.")

    # correction loop: top up under-dispensed components until all are within tolerance
    correction_fraction = 0.10  # add at most 10% of the original target per correction step
    max_iterations = 10

    iterations_used = 0
    for iteration in range(max_iterations):
        components_to_correct = [
            (i, target - measured)
            for i, (measured, target) in enumerate(zip(measured_results, amounts))
            if target - measured > relative_tolerance
        ]

        if not components_to_correct:
            print("All components within tolerance.")
            break

        for i, shortfall in components_to_correct:
            correction = min(shortfall, amounts[i] * correction_fraction)
            print(f"Component {i+1}: shortfall {shortfall:.3f}g, correcting by {correction:.3f}g.")
            last_measurement = measure_weight()
            dispense(i + 1, correction)
            measured_results[i] += measure_weight() - last_measurement

        iterations_used += 1

    else:
        print("Warning: max correction iterations reached. Some components may still be out of tolerance.")

    print(f"Total correction iterations used: {iterations_used}")

    # find the biggest % difference between 2 components (measured/target ratio)
    ratios = [measured / target for measured, target in zip(measured_results, amounts)]
    max_diff_pct = 0
    max_pair = (0, 1)
    for i in range(len(ratios)):
        for j in range(i + 1, len(ratios)):
            diff_pct = abs(ratios[i] - ratios[j]) * 100
            if diff_pct > max_diff_pct:
                max_diff_pct = diff_pct
                max_pair = (i, j)
    i, j = max_pair
    print(f"Biggest % difference: Component {i+1} ({ratios[i]*100:.2f}% of target) vs Component {j+1} ({ratios[j]*100:.2f}% of target): {max_diff_pct:.2f}%")


def show_dispensed_amounts():
    print("")
    print("Dispensed amounts:")
    for i, amount in enumerate(comps_dispensed):
        print(f"Component {i+1}: {amount} grams.")


def measure_weight():
    noise = random.uniform(-measurement_noise_factor, measurement_noise_factor)
    measurement = sum(comps_dispensed) * (1 + noise)  # in gram, total weight dispensed with noise
    return measurement  # for testing, return the total amount dispensed from all motors as the measured weight




def dispense(component_id, weight):
    amount = weight / density_of_liquid  # convert weight to volume
    print(f"Dispensing component {component_id}, amount: {amount}")


    # using random number to simulate noise in dispensing, for testing purposes

    amount_with_noise = amount * (1 + random.uniform(-dispensing_noise_factor, dispensing_noise_factor))
    move_motor(component_id, amount_with_noise / volume_per_step)




def move_motor(motor_id, steps):
    print(f"Moving motor {motor_id} by {steps} steps.")
    comps_dispensed[motor_id - 1] += steps * volume_per_step * density_of_liquid # in gram  # for testing, update the amount dispensed for this motor


if __name__ == "__main__":
    main()
