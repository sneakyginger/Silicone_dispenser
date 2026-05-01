import RPi.GPIO as GPIO
import queue

Pin_left  = 17  # CLK
Pin_right = 27  # DT
Pin_click = 22  # SW

event_queue = queue.Queue()
last_state = None  # Stores previous (CLK, DT) pair

def encoder_callback(channel):
    global last_state

    if channel == Pin_click:
        if GPIO.input(Pin_click) == GPIO.LOW:
            event_queue.put("Click")
        return

    # Read BOTH pins immediately together
    clk = GPIO.input(Pin_left)
    dt  = GPIO.input(Pin_right)
    state = (clk, dt)

    if state == last_state:
        return  # No real change, ignore

    # Direction logic: compare against previous state
    if last_state is not None:
        prev_clk, prev_dt = last_state
        if prev_clk == 1 and prev_dt == 0 and clk == 1 and dt == 1:
            event_queue.put("Right")
        elif prev_clk == 0 and prev_dt == 1 and clk == 1 and dt == 1:
            event_queue.put("Left")

    last_state = state

def setup_encoder(pin_left, pin_right, pin_click):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_left,  GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(pin_click, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Detect ALL edges on both encoder pins — no bouncetime
    GPIO.add_event_detect(pin_left,  GPIO.BOTH, callback=encoder_callback)
    GPIO.add_event_detect(pin_right, GPIO.BOTH, callback=encoder_callback)
    GPIO.add_event_detect(pin_click, GPIO.BOTH, callback=encoder_callback, bouncetime=200)

def run_encoder(pin_left, pin_right, pin_click):
    setup_encoder(pin_left, pin_right, pin_click)
    try:
        while True:
            event = event_queue.get()
            print(event)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()

_setup_done = False

def def_encoder(pin_left, pin_right, pin_click):
    global _setup_done
    if not _setup_done:
        setup_encoder(pin_left, pin_right, pin_click)
        _setup_done = True
    try:
        return event_queue.get_nowait()
    except queue.Empty:
        return None

if __name__ == "__main__":
    run_encoder(Pin_left, Pin_right, Pin_click)