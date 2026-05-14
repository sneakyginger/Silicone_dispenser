import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711
print("Starting...")
def cleanAndExit():
    print("Cleaning...")
        
    print("Bye!")
    sys.exit()

hx = HX711(29, 31)
#hx = HX711(5, 6) #BCM

'''
I've found out that, for some reason, the order of the bytes is not always the same between versions of python,
and the hx711 itself. I still need to figure out why.

If you're experiencing super random values, change these values to MSB or LSB until you get more stable values.
There is some code below to debug and log the order of the bits and the bytes.

The first parameter is the order in which the bytes are used to build the "long" value. The second paramter is
the order of the bits inside each byte. According to the HX711 Datasheet, the second parameter is MSB so you
shouldn't need to modify it.
'''
hx.set_reading_format("MSB", "MSB")

'''
# HOW TO CALCULATE THE REFFERENCE UNIT
1. Set the reference unit to 1 and make sure the offset value is set.
2. Load you sensor with 1kg or with anything you know exactly how much it weights.
3. Write down the 'long' value you're getting. Make sure you're getting somewhat consistent values.
    - This values might be in the order of millions, varying by hundreds or thousands and it's ok.
4. To get the wright in grams, calculate the reference unit using the following formula:
        
    referenceUnit = longValueWithOffset / 1000
        
In my case, the longValueWithOffset was around 114000 so my reference unit is 114,
because if I used the 114000, I'd be getting milligrams instead of grams.
'''
referenceUnit = 1

#referenceUnit = 93801/5.92 ref 5.92g
#referenceUnit = 398500/25.099 ref 25.099g
#referenceUnit = 589420/37.111 ref 37.111g
#referenceUnit = 868650/54.681 ref 54.681g
#referenceUnit = 979700/61.71 ref 61.71g
#referenceUnit = 1255451/79.030 ref 79.030g
#referenceUnit = 1544000/97.4 ref 97.4g
#referenceUnit = 2044000/128.9 ref 128.9g
#referenceUnit = 2541125/160.0 ref 160.0g
referenceUnit = 15,870

hx.set_reference_unit(referenceUnit)

print("reset")
hx.reset()
time.sleep(2)
#the argument is the amount of times to measure before taring
hx.tare(31)

print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()
loop_count = 0
while True:
    try:
        loop_count += 1
     
        
        # Prints the weight. the argument is the avaraging
        val = hx.get_weight(3)
        print(val)

        #hx.power_down()
        #hx.power_up()
        #time.sleep(0.4)
        #if loop_count == 50 and val <1:
        #    loop_count = 0
        #    hx.tare(15)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
