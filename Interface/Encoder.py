import RPi.GPIO as GPIO
import queue

Pin_left  = 17  # CLK
Pin_right = 27  # DT
Pin_click = 22  # SW

event_queue = queue.Queue()

def encoder_callback(channel):
    if channel == Pin_click:
        if GPIO.input(Pin_click) == GPIO.LOW:
            event_queue.put("Click")
    elif channel == Pin_left:
        clk = GPIO.input(Pin_left)
        dt  = GPIO.input(Pin_right)
        if clk == dt:
            event_queue.put("Right")
        else:
            event_queue.put("Left")

def setup_encoder(pin_left, pin_right, pin_click):
    GPIO.setmode(GPIO.BCM)  # Call once, not per function

    GPIO.setup(pin_left,  GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(pin_right, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(pin_click, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.add_event_detect(pin_left,  GPIO.RISING, callback=encoder_callback, bouncetime=50)
    GPIO.add_event_detect(pin_click, GPIO.BOTH, callback=encoder_callback, bouncetime=200)

def run_encoder(pin_left, pin_right, pin_click):
    setup_encoder(pin_left, pin_right, pin_click)
    try:
        while True:
            event = event_queue.get()  # Blocks here until an event arrives
            print(event)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    run_encoder(Pin_left, Pin_right, Pin_click)