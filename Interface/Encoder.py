import RPi.GPIO as GPIO
Pin_left = 17
Pin_right = 27
Pin_click = 22

def encoder_rot(Pin_left, Pin_right):
    pos = 0

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Pin_left, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(Pin_right, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.add_event_detect(Pin_left, GPIO.RISING, callback=encoder_callback)

def encoder_click(Pin_click):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Pin_click, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(Pin_click, GPIO.RISING, callback=encoder_callback)

def encoder_callback(channel):
    if channel == Pin_click:
        return "Click"
    if channel == Pin_left:
        if GPIO.input(Pin_right) == GPIO.HIGH:
            return "Right"
        if GPIO.input(Pin_right) == GPIO.LOW:
            return "Left"
def def_encoder(Pin_left, Pin_right, Pin_click):
    while True:
        print(encoder_rot(Pin_left, Pin_right))
        print(encoder_click(Pin_click))
        #if encoder_click(Pin_click) == "Click":
        #    return "Click"
        #elif encoder_rot(Pin_left, Pin_right) == "Right":
        #    return "Right"
        #elif encoder_rot(Pin_left, Pin_right) == "Left":
        #    return "Left"
