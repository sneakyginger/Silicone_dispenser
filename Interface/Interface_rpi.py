#python -m venv dispenser_venv
#dispenser_venv\Scripts\activate

import sys
import pygame
from pygame.locals import *
import pygame.gfxdraw
import time
import threading
import random
import saved_settings

use_dispenser2 = "-d2" in sys.argv[1:]
use_minimal_g = "-g" in sys.argv[1:]
use_minimal_n = "-n" in sys.argv[1:]
if use_minimal_g and use_minimal_n:
    sys.exit("Choose only one of -g or -n.")
import dispensing_job
import dispensing_progress_view
import mixing_settings_form
import top_bar
import theme
#import Weight_sensor

TEXT_COLOR = theme.BLACK
BACKGROUND_COLOR = theme.WHITE
DISPENSING_BACKGROUND_COLOR = theme.BLACK
DISPENSING_TEXT_COLOR = theme.WHITE
SELECTION_BAR_TRACK_COLOR = theme.SELECTION_BAR_TRACK  # Selection bar UI: background color behind adjustable weight, hardness, and refill bars.

is_rpi = False
try:
    with open("/proc/device-tree/model", "r"):
        is_rpi = True
except FileNotFoundError:
    is_rpi = False

def is_raspberry_pi():
    return is_rpi

#PINS
Pin_left, Pin_right, Pin_click = 36, 40, 38

if is_raspberry_pi():
    if use_minimal_g:
        import minimal_dispenseG as dispense
    elif use_minimal_n:
        import minimal_dispenseN as dispense
    elif use_dispenser2:
        import dispenser as dispense
    else:
        import dispense
    import Encoder
    import RPi.GPIO as GPIO
    GPIO.cleanup()
else:
    class _DispenseStub:
        density_of_liquid = 1.06
        sim_update_seconds = 0.5  # Laptop dispensing sim: seconds between fake weight-sensor progress updates.
        sim_seconds_per_gram = 0.08  # Laptop dispensing sim: scales fake dispense duration with requested component weight.
        sim_min_component_seconds = 1.0  # Laptop dispensing sim: minimum visible time for each active component.
        sim_max_component_seconds = 8.0  # Laptop dispensing sim: maximum visible time for each active component.
        sim_measurement_noise_fraction = 0.03  # Laptop dispensing sim: random final measured over/under-shoot per component.

        @staticmethod
        def multi_dispense(amounts, progress_callback=None, progress_interval=10):
            print(f"[laptop sim] multi_dispense({amounts})")
            measured = [0.0, 0.0, 0.0, 0.0]  # Laptop dispensing sim: fake measured grams returned after the simulated dispense.
            for i, target in enumerate(amounts):
                target = float(target or 0.0)  # Laptop dispensing sim: requested grams for the active simulated component.
                if target <= 0:
                    continue

                duration = min(  # Laptop dispensing sim: visible component dispense duration, capped for practical testing.
                    _DispenseStub.sim_max_component_seconds,
                    max(_DispenseStub.sim_min_component_seconds, target * _DispenseStub.sim_seconds_per_gram),
                )
                final_measured = target * random.uniform(  # Laptop dispensing sim: final fake scale reading with small dosing error.
                    1.0 - _DispenseStub.sim_measurement_noise_fraction,
                    1.0 + _DispenseStub.sim_measurement_noise_fraction,
                )
                started_at = time.time()  # Laptop dispensing sim: start time for interpolating fake scale progress.
                while True:
                    elapsed = time.time() - started_at  # Laptop dispensing sim: elapsed seconds for this fake component.
                    fraction = min(1.0, elapsed / duration)  # Laptop dispensing sim: progress fraction of the active component.
                    current = final_measured * fraction  # Laptop dispensing sim: fake current component scale delta in grams.
                    if progress_callback is not None:
                        progress_callback(i, current)
                    if fraction >= 1.0:
                        break
                    time.sleep(_DispenseStub.sim_update_seconds)
                measured[i] = final_measured
            return measured
    dispense = _DispenseStub()
    Encoder = None

def dispense_and_track_volume(amounts):
    """Run multi_dispense and decrement each bucket's volume by its measured grams."""
    measured = dispense.multi_dispense(amounts)
    if measured is None:
        return
    saved_settings.decrement_bucket_volumes(measured, dispense.density_of_liquid)


# Menu constants
MENU_START = 0
MENU_2COMPONENT_WEIGHT = 1
MENU_4COMPONENT_WEIGHT = 2
MENU_4COMPONENT_HARDNESS = 3
MENU_MIX_CONFIRM = 4
MENU_SETTINGS = 5
MENU_MIXING_SETTINGS = 6
MENU_REPLACE_CARTRIDGE = 7
MENU_REPLACE_WEIGHT = 8
MENU_MIXING_FREQUENCY = 9
MENU_MIXING_DURATION = 10
MENU_MIXING_START_TIME = 11
MENU_1COMPONENT_SELECT = 12
MENU_1COMPONENT_WEIGHT = 13
MENU_DISPENSING = -1
MENU_2COMPONENT_SELECTION = 15

max_weight_1component = 100
max_weight_2component = 100
max_weight_4component = 100
max_volume_replacement = 500  # Refilling UI: visual full-scale point for the refill bar, not a refill limit.
volume_replacement_step = 10.0  # Refilling UI: refill volume changes by 10 ml for each encoder step.
min_hardness_4component, max_hardness_4component = saved_settings.hardness_limits()
components_amount = -1
component = -1
weight = -1
hardness = -1
bucket_being_replaced = -1  # 0=bucket 1, 1=bucket 2, 2=bucket 3, 3=bucket 4


def load_image(path, size, location):
    image = pygame.image.load(path)
    image = pygame.Surface.convert_alpha(image)
    image = pygame.transform.scale(image, size)
    image_rect = image.get_rect()
    image_rect.center = location
    return image, image_rect

pygame.font.init()

# Create a font (font name, size) - None uses the default font
font = pygame.font.SysFont(theme.DEFAULT_FONT, theme.FONT_SIZE_NORMAL)
font_small = pygame.font.SysFont(theme.DEFAULT_FONT, theme.FONT_SIZE_SMALL)
font_big = pygame.font.SysFont(theme.DEFAULT_FONT, theme.FONT_SIZE_BIG)

def create_text(text, position, color=theme.WHITE, font_type="normal"):
    if font_type == "small":
        surface_text = font_small.render(text, True, color)
        surface_text = font_small.render(text, True, color)
    elif font_type == "normal":
        surface_text = font.render(text, True, color)
        surface_text = font.render(text, True, color)
    elif font_type == "big":
        surface_text = font_big.render(text, True, color)
        surface_text = font_big.render(text, True, color)
    surface_text_rect = surface_text.get_rect()
    surface_text_rect.center = position
    return surface_text, surface_text_rect

def select_time(selected_time,direction,selection):
    day = selected_time[0]
    hour = selected_time[1]
    minute = selected_time[2]
    if selection == 0:
        if direction == "left":
            if day > 0:
                day -= 1
            elif day == 0:
                day = 30
        elif direction == "right":
            if day < 30:
                day += 1
            elif day == 30:
                day = 0

    elif selection == 1:
        if direction == "left":
            if hour > 0:
                hour -= 1
            elif hour == 0:
                hour = 24
        elif direction == "right":
            if hour < 24:
                hour += 1
            elif hour == 24:
                hour = 0

    elif selection == 2:
        if direction == "left":
            if minute > 0:
                minute -= 1
            elif minute == 0:
                minute = 60
        elif direction == "right":
            if minute < 60:
                minute += 1
            elif minute == 60:
                minute = 0
    
    return [day, hour, minute]

def display_time_selection(width, height,selected_time, location, time_selecting ):
    day = selected_time[0]
    hour = selected_time[1]
    minute = selected_time[2]
    if not time_selecting:
        if location == 0:
            selection_image_rect.center = (width /6, height // 2)
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        elif location == 1:
            selection_image_rect.center = (width/6*3, height // 2)
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        elif location == 2:
            selection_image_rect.center = (width /6*5, height // 2)
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        elif location == 3:
            return_selection_image_rect.center = (width-50, height-50)
            screen.blit(return_selection_image, return_selection_image_rect)  # draw cursor
    #draw days hours and minutes
    day_text, day_text_rect = create_text(f"{day}", (width /6, height // 2+25), TEXT_COLOR, "big")
    screen.blit(day_text, day_text_rect)  # draw days
    hour_text, hour_text_rect = create_text(f"{hour}", (width/6*3, height // 2+25), TEXT_COLOR, "big")
    screen.blit(hour_text, hour_text_rect)  # draw hours
    minute_text, minute_text_rect = create_text(f"{minute}", (width /6*5, height // 2+25), TEXT_COLOR, "big")
    screen.blit(minute_text, minute_text_rect)  # draw minutes
    partition_text, partition_text_rect = create_text(":", (width/6*2, height // 2+25), TEXT_COLOR, "big")
    screen.blit(partition_text, partition_text_rect)  # draw :
    partition_text, partition_text_rect = create_text(":", (width/6*4, height // 2+25), TEXT_COLOR, "big")
    screen.blit(partition_text, partition_text_rect)  # draw :
    # annotate days hours and minutes
    day_annotate_text, day_annotate_text_rect = create_text("DAYS", (width /6, height // 2-25), TEXT_COLOR, "small")
    screen.blit(day_annotate_text, day_annotate_text_rect)  # draw annotation day
    hour_annotate_text, hour_annotate_text_rect = create_text("HOURS", (width/6*3, height // 2-25), TEXT_COLOR, "small")
    screen.blit(hour_annotate_text, hour_annotate_text_rect)  # draw annotation hour
    minute_annotate_text, minute_annotate_text_rect = create_text("MINUTES", (width /6*5, height // 2-25), TEXT_COLOR, "small")
    screen.blit(minute_annotate_text, minute_annotate_text_rect)  # draw annotation minute
    return
work = 5000000
def doWork():
    global loading_progress
    for ii in range(work):
        loading_progress = int((ii / work) * 100)+1
def locus(amount_sprites):
    loci = []
    for i in range(amount_sprites):
        loci.append((width/(amount_sprites+1)*(i+1), height/2))
    loci.append((width-50, height-50)) #return sprite location
    return loci
def available_locations(current_location, direction, options):
    if direction == "right":
        if current_location >= options+1:
            current_location = 0
    elif direction == "left":
        if current_location < 0:
            current_location = options
    return current_location

def menu_has_return_button(menu):
    return menu not in (MENU_START, MENU_MIX_CONFIRM, MENU_DISPENSING)

def available_menu_locations(menu, sprites):
    if menu_has_return_button(menu):
        return sprites
    return sprites - 1

pygame.init()
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((800, 480))
width, height = screen.get_size()

pygame.display.set_caption('Dispenser Interface')
menu = MENU_START
location = 0
time_frequency, time_duration, time_start_time = [0,0,0], [0,0,0], [0,0,0]
mixing_settings_form_state = mixing_settings_form.default_state()  # Mixing settings UI: stores the selected row, edit mode, and saved schedule values.
start_time_selection = False
sprites = 4
previous_menu = MENU_START
button_size = (75,75)


def get_click_target(mouse_pos, menu, sprites, loci):
    """Map a mouse click position to the location index it activates, or None."""
    if menu == MENU_DISPENSING:
        return None

    return_rect = pygame.Rect(0, 0, 120, 120)
    return_rect.center = (width - 50, height - 50)

    if menu in (MENU_MIXING_FREQUENCY, MENU_MIXING_DURATION, MENU_MIXING_START_TIME):
        time_centers = [(width / 6, height / 2),
                        (width / 6 * 3, height / 2),
                        (width / 6 * 5, height / 2)]
        for i, c in enumerate(time_centers):
            r = pygame.Rect(0, 0, 160, 160)
            r.center = c
            if r.collidepoint(mouse_pos):
                return i
        if return_rect.collidepoint(mouse_pos):
            return sprites
        return None

    # Weight/hardness slider menus have only a return button — the bar itself
    # is adjusted by the rotary encoder.
    if menu in (MENU_2COMPONENT_WEIGHT, MENU_4COMPONENT_WEIGHT, MENU_4COMPONENT_HARDNESS,
                MENU_REPLACE_WEIGHT, MENU_1COMPONENT_WEIGHT):
        if return_rect.collidepoint(mouse_pos):
            return sprites
        return None

    for i in range(sprites):
        r = pygame.Rect(0, 0, 180, 180)
        r.center = loci[i]
        if r.collidepoint(mouse_pos):
            return i
    if menu_has_return_button(menu) and return_rect.collidepoint(mouse_pos):
        return sprites
    return None



#Maak teks voor tijdens mengen
mengen_bezig, mengen_bezig_rect = create_text("MIXING", (width // 2, height // 2), DISPENSING_TEXT_COLOR)
#Text menu MENU_START
menu0_text, menu0_text_rect = create_text("START", (width // 2, 25), TEXT_COLOR)

#Text menu MENU_2COMPONENT_WEIGHT
menu1_text, menu1_text_rect = create_text("2 component dispensing", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_4COMPONENT_WEIGHT
menu2_text, menu2_text_rect = create_text("4 component dispensing", (width //2, 25), TEXT_COLOR)
#Text menu MENU_4COMPONENT_HARDNESS
menu3_text, menu3_text_rect = create_text("4 component dispensing", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_MIX_CONFIRM
menu4_text, menu4_text_rect = create_text("Would you like to start mixing?", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_SETTINGS
menu5_text, menu5_text_rect = create_text("Settings", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_MIXING_SETTINGS
menu6_text, menu6_text_rect = create_text("Mixing Settings", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_REPLACE_CARTRIDGE
menu7_text, menu7_text_rect = create_text("Refill bucket", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_REPLACE_WEIGHT
menu8_text, menu8_text_rect = create_text("Select hardness of new cartridge", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_MIXING_FREQUENCY
menu9_text, menu9_text_rect = create_text("Time between mixes", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_MIXING_DURATION
menu10_text, menu10_text_rect = create_text("Select mixing duration", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_MIXING_START_TIME
menu11_text, menu11_text_rect = create_text("Select time until next mix", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_1COMPONENT_SELECT
menu12_text, menu12_text_rect = create_text("Select component to dispense", (width // 2, 25), TEXT_COLOR)
#Text menu MENU_1COMPONENT_WEIGHT
menu13_text, menu13_text_rect = create_text("Select desired weight", (width // 2, 25), TEXT_COLOR)
#text return
return_, return_rect = create_text("Return to previous menu", (width // 2, height // 2), TEXT_COLOR, "normal")


loci = locus(4)
#menus names text
two_component_text,two_component_text_rect = create_text("2 component", (loci[0][0], loci[0][1]+90), TEXT_COLOR, "small")
four_component_text, four_component_text_rect = create_text("4 component", (loci[1][0], loci[1][1]+90), TEXT_COLOR, "small")
mixing_menu_text, mixing_menu_text_rect = create_text("Mixing", (loci[2][0], loci[2][1]+90), TEXT_COLOR, "small")
settings_text, settings_text_rect = create_text("Settings", (loci[3][0], loci[3][1]+90), TEXT_COLOR, "small")

loci = locus(3)
#Setting options text
mixing_settings_text, mixing_settings_text_rect = create_text("Mixing settings", (loci[0][0], loci[0][1]+90), TEXT_COLOR, "small")
replace_cartridge_text, replace_cartridge_text_rect = create_text("Refill bucket", (loci[1][0], loci[1][1]+90), TEXT_COLOR, "small")
one_component_dispensing_text, one_component_dispensing_text_rect = create_text("One component", (loci[2][0], loci[2][1]+90), TEXT_COLOR, "small")
one_component_dispensing_line2_text, one_component_dispensing_line2_text_rect = create_text("dispensing", (loci[2][0], loci[2][1]+115), TEXT_COLOR, "small")

loci = locus(3)
#mixing settings options text
frequency_text, frequency_text_rect = create_text("Mixing frequency", (loci[0][0], loci[0][1]+90), TEXT_COLOR, "small")
duration_text, duration_text_rect = create_text("Mixing duration", (loci[1][0], loci[1][1]+90), TEXT_COLOR, "small")
mixing_start_time_text, mixing_start_time_text_rect = create_text("Time until", (loci[2][0], loci[2][1]+90), TEXT_COLOR, "small")
mixing_start_time_line2_text, mixing_start_time_line2_text_rect = create_text("next mix", (loci[2][0], loci[2][1]+115), TEXT_COLOR, "small")


#cartridge replacement options text
select_cartridge_text, select_cartridge_text_rect = create_text("Select bucket to refill", (width/2, loci[0][1]+90), TEXT_COLOR, "small")

loci = locus(4)
#load in selection sprite
selection_image, selection_image_rect = load_image(r'./Sprites/rond.png', (145, 145), loci[0])
return_selection_image, return_selection_image_rect = load_image(r'./Sprites/rond.png', (100, 100), loci[-1])  # Return button UI: default-size selector used when the back button is selected.

#loud in 2 component mixing sprite
two_component_image, two_component_image_rect = load_image(r'./Sprites/button_2comp_1.png',(175,175),loci[0])

#loud in 4 component mixing sprite
four_component_image, four_component_image_rect = load_image(r'./Sprites/button_4comp.png',(175,175),loci[1])

#load in settings sprite
settings_image, settings_image_rect = load_image(r'./Sprites/settings.png', button_size, loci[3])

#load in return sprite
return_image, return_image_rect = load_image(r'./Sprites/return.png', button_size, loci[-1])

#load in loading bar sprite
loading_bar_image, loading_bar_image_rect = load_image(r'./Sprites/white.png',(8,150) ,(200, height//2))
loading_progress = 0
loading_bar_width = 8


weight_1component_progress = max_weight_1component//2
weight_2component_progress = max_weight_2component//2
weight_4component_progress = max_weight_4component//2
volume_replacement_progress = max_volume_replacement / 2  # Refilling UI: keep math as float; display converts to int.

scaling_weight_1 = width/2//max_weight_1component
scaling_weight_2 = width/2//max_weight_2component
scaling_weight_4 = width/2//max_weight_4component
scaling_volume_replacement = (width / 2) / max_volume_replacement  # Refilling UI: pixels per ml; real division avoids rounding to 0.

x_bar_weight_1 = width/2-max_weight_1component*scaling_weight_1/2
x_bar_weight_2 = width/2-max_weight_2component*scaling_weight_2/2
x_bar_weight_4 = width/2-max_weight_4component*scaling_weight_4/2
x_bar_volume_re = width/2-max_volume_replacement*scaling_volume_replacement/2

weight_bar_width = 8
weight_bar_image, weight_bar_image_rect = load_image(r'./Sprites/black.png',(weight_bar_width, 50) ,(200, height//2))

hardness_4component_progress = (min_hardness_4component + max_hardness_4component) // 2
hardness_4component_span = max_hardness_4component - min_hardness_4component
scaling_hardness_4 = width/2//hardness_4component_span

x_bar_har_4 = width/2-hardness_4component_span*scaling_hardness_4/2
hardness_bar_width = 8
hardness_bar_image, hardness_bar_image_rect = load_image(r'./Sprites/black.png',(hardness_bar_width, 50) ,(200, height//2))


#load button sprites to test
button1_image, button1_image_rect = load_image(r'./Sprites/button.png', button_size, (loci[0]))
button2_image, button2_image_rect = load_image(r'./Sprites/button.png', button_size, (loci[1]))
button3_image, button3_image_rect = load_image(r'./Sprites/button.png', button_size, (loci[2]))
button4_image, button4_image_rect = load_image(r'./Sprites/button.png', button_size, (loci[3]))

bottle_img_size = (116,626)
bottle_img_size = (bottle_img_size[0]//4,bottle_img_size[1]//4)
button_bottle_a_image, button_bottle_a_image_rect = load_image(r'./Sprites/button_bottle_a.png', bottle_img_size, (loci[0]))
button_bottle_b_image, button_bottle_b_image_rect = load_image(r'./Sprites/button_bottle_b.png', bottle_img_size, (loci[1]))
button_bottle_c_image, button_bottle_c_image_rect = load_image(r'./Sprites/button_bottle_c.png', bottle_img_size, (loci[2]))
button_bottle_d_image, button_bottle_d_image_rect = load_image(r'./Sprites/button_bottle_c.png', bottle_img_size, (loci[3]))

loci = locus(2)
#load yes and no sprite
yes_image, yes_image_rect = load_image(r'./Sprites/yes.png', button_size, (loci[0]))
no_image, no_image_rect = load_image(r'./Sprites/no.png', button_size, (loci[1]))

button_bottle_ab_image, button_bottle_ab_image_rect = load_image(r'./Sprites/button_2comp_1.png', bottle_img_size, (loci[0]))
button_bottle_cd_image, button_bottle_cd_image_rect = load_image(r'./Sprites/button_2comp_2.png', bottle_img_size, (loci[1]))


def draw_selection_cursor():
    if location == sprites and menu_has_return_button(menu):
        screen.blit(return_selection_image, return_selection_image_rect)  # draw cursor
    else:
        screen.blit(selection_image, selection_image_rect)  # draw cursor

def draw_bar_track(x, y, bar_width):
    """Draw the selection-bar background used behind adjustable bar menus."""
    pygame.draw.rect(screen, SELECTION_BAR_TRACK_COLOR, pygame.Rect(x, y, int(bar_width), 50))

dispense_started = False
dispense_warning_message = ""
LOW_VOLUME_THRESHOLD_ML = 20
running = True
while running:
    loci = locus(sprites)
    selection_image_rect.center = (loci[location]) 
    return_selection_image_rect.center = (loci[location])
    screen.fill(BACKGROUND_COLOR)# clear screen

    if is_raspberry_pi():
        encoder = Encoder.def_encoder(Pin_left, Pin_right, Pin_click)
    else:
        encoder = None

    mouse_click_pos = None
    right_click = False
    wheel_direction = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click_pos = event.pos
            elif event.button == 3:
                right_click = True
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                wheel_direction = "Right"
            elif event.y < 0:
                wheel_direction = "Left"

    if mouse_click_pos is not None and encoder not in ("Left", "Right", "Click"):
        target = get_click_target(mouse_click_pos, menu, sprites, loci)
        if target is not None:
            location = target
            encoder = "Click"

    if right_click and encoder not in ("Left", "Right", "Click"):
        encoder = "Click"

    if wheel_direction is not None and encoder not in ("Left", "Right", "Click"):
        encoder = wheel_direction

    location_before_encoder = location  # Mixing settings UI: keeps the selected form row steady while an edited value changes.

    if encoder == "Right": #changing location
        location += 1
        location = available_locations(location, "right", available_menu_locations(menu, sprites))
        if menu == MENU_2COMPONENT_WEIGHT:
            if weight_2component_progress < max_weight_2component:
                location  = 0
                weight_2component_progress += 1
            else:
                weight_2component_progress = max_weight_2component+1
                location = sprites

        elif menu == MENU_4COMPONENT_WEIGHT:
            if weight_4component_progress < max_weight_4component:
                location  = 0
                weight_4component_progress += 1
            else:
                weight_4component_progress = max_weight_4component+1
                location = sprites
        elif menu == MENU_4COMPONENT_HARDNESS:
            if hardness_4component_progress < max_hardness_4component:
                location  = 0
                hardness_4component_progress += 1
            else:
                hardness_4component_progress = max_hardness_4component
                location = sprites
        elif menu == MENU_MIX_CONFIRM:
            if location == 2:
                location = 0
        elif menu == MENU_REPLACE_WEIGHT:
            location  = 0
            volume_replacement_progress = round(volume_replacement_progress,-1)
            volume_replacement_progress += volume_replacement_step
        elif menu == MENU_MIXING_FREQUENCY:
            if start_time_selection:
                time_frequency = select_time(time_frequency, "right", time_increment_selection)
        elif menu == MENU_MIXING_DURATION:
            if start_time_selection:
                time_duration = select_time(time_duration, "right", time_increment_selection)
        elif menu == MENU_MIXING_START_TIME:
            if start_time_selection:
                time_start_time = select_time(time_start_time, "right", time_increment_selection)
        elif menu == MENU_MIXING_SETTINGS:
            form_location = location_before_encoder if mixing_settings_form_state["editing"] else location  # Mixing settings UI: chooses whether encoder movement edits a value or moves between rows.
            mixing_settings_form_state = mixing_settings_form.handle_turn(mixing_settings_form_state, "right", form_location)
            location = mixing_settings_form_state["location"]
        elif menu == MENU_1COMPONENT_WEIGHT:
            if weight_1component_progress < max_weight_1component:
                location  = 0
                weight_1component_progress += 1
            else:
                weight_1component_progress = max_weight_1component+1
                location = sprites

    elif encoder == "Left":
        location -= 1
        location = available_locations(location, "left", available_menu_locations(menu, sprites))
        if menu == MENU_2COMPONENT_WEIGHT:
            if weight_2component_progress > 0:
                location  = 0
                weight_2component_progress -= 1
            else:
                weight_2component_progress = 0
                location = sprites
        elif menu == MENU_4COMPONENT_WEIGHT:
            if weight_4component_progress > 0:
                location  = 0
                weight_4component_progress -= 1
            else:
                weight_4component_progress = 0
                location = sprites
        elif menu == MENU_4COMPONENT_HARDNESS:
            if hardness_4component_progress > min_hardness_4component:
                location  = 0
                hardness_4component_progress -= 1
            else:
                hardness_4component_progress = min_hardness_4component
                location = sprites
        elif menu == MENU_MIX_CONFIRM:
            if location == 2:
                location = 1
        elif menu == MENU_REPLACE_WEIGHT:
            volume_replacement_progress = round(volume_replacement_progress,-1)
            if volume_replacement_progress > 0:
                location  = 0
                volume_replacement_progress = max(0.0, volume_replacement_progress - volume_replacement_step)
            else:
                volume_replacement_progress = 0.0
                location = sprites
        elif menu == MENU_MIXING_FREQUENCY:
            location = available_locations(location, "left", 4)
            if start_time_selection:
                time_frequency = select_time(time_frequency, "left", time_increment_selection)
        elif menu == MENU_MIXING_DURATION:
            location = available_locations(location, "left", 4)
            if start_time_selection:
                time_duration = select_time(time_duration, "left", time_increment_selection)
        elif menu == MENU_MIXING_START_TIME:
            location = available_locations(location, "left", 4)
            if start_time_selection:
                time_start_time = select_time(time_start_time, "left", time_increment_selection)
        elif menu == MENU_MIXING_SETTINGS:
            form_location = location_before_encoder if mixing_settings_form_state["editing"] else location  # Mixing settings UI: chooses whether encoder movement edits a value or moves between rows.
            mixing_settings_form_state = mixing_settings_form.handle_turn(mixing_settings_form_state, "left", form_location)
            location = mixing_settings_form_state["location"]
        elif menu == MENU_1COMPONENT_WEIGHT:
            if weight_1component_progress > 0:
                location  = 0
                weight_1component_progress -= 1
            else:
                weight_1component_progress = 0
                location = sprites

    elif encoder == "Click": #state machine for menu navigation
        if menu == MENU_START:
            dispense_warning_message = ""
            if location == 0:
                menu = MENU_2COMPONENT_SELECTION
                location = 1
            elif location == 1:
                menu = MENU_4COMPONENT_WEIGHT
            elif location == 2:
                components_amount = -1
                menu = MENU_MIX_CONFIRM
            elif location == 3:
                menu = MENU_SETTINGS
                location = 2


        elif menu == MENU_2COMPONENT_SELECTION:
            if location == 0:
                component = 0
                menu = MENU_2COMPONENT_WEIGHT
            elif location == 1:
                component = 1
                menu = MENU_2COMPONENT_WEIGHT
            elif location == sprites:
                menu = MENU_START

        elif menu == MENU_2COMPONENT_WEIGHT:
            if location == sprites:
                menu = MENU_START
            elif weight_2component_progress > 0:
                components_amount = 2
                weight = weight_2component_progress
                menu = MENU_DISPENSING

        elif menu == MENU_4COMPONENT_WEIGHT:
            if location == sprites:
                menu = MENU_START
            elif weight_4component_progress > 0:
                weight = weight_4component_progress
                components_amount = 4
                menu = MENU_4COMPONENT_HARDNESS

        elif menu == MENU_4COMPONENT_HARDNESS:
            if location == sprites:
                menu = MENU_START
            else:
                hardness = hardness_4component_progress
                menu = MENU_DISPENSING


        elif menu == MENU_MIX_CONFIRM:
            if location == 0:
                menu = MENU_DISPENSING
            elif location == 1:
                menu = MENU_START


        elif menu == MENU_SETTINGS:
            if location == 0:
                menu = MENU_MIXING_SETTINGS
            elif location == 1:
                menu = MENU_REPLACE_CARTRIDGE
            elif location == 2:
                menu = MENU_1COMPONENT_SELECT
            elif location == sprites:
                menu = MENU_START


        elif menu == MENU_MIXING_SETTINGS:
            mixing_settings_form_state, exit_mixing_settings = mixing_settings_form.handle_click(mixing_settings_form_state, location)  # Mixing settings UI: click enters editing, advances fields, or returns to settings.
            location = mixing_settings_form_state["location"]
            if exit_mixing_settings:
                menu = MENU_SETTINGS


        elif menu == MENU_REPLACE_CARTRIDGE:
            if location == sprites:
                menu = MENU_SETTINGS
            else:
                bucket_being_replaced = location  # 0=bucket 1, 1=bucket 2, 2=bucket 3, 3=bucket 4
                volume_replacement_progress = float(saved_settings.bucket_volume(location))
                menu = MENU_REPLACE_WEIGHT

        elif menu == MENU_REPLACE_WEIGHT:
            if location == sprites:
                menu = MENU_REPLACE_CARTRIDGE
            else:
                saved_settings.set_bucket_volume(bucket_being_replaced, volume_replacement_progress)
                saved_settings.save_settings(saved_settings.cartridge_config)
                menu = MENU_START


        elif menu == MENU_MIXING_FREQUENCY:
            if start_time_selection:
                start_time_selection = False
                location = time_increment_selection
            else:
                if location == sprites:
                    menu = MENU_MIXING_SETTINGS
                elif location == 0:
                    time_increment_selection = 0
                    start_time_selection = True
                elif location == 1:
                    time_increment_selection = 1
                    start_time_selection = True
                elif location == 2:
                    time_increment_selection = 2
                    start_time_selection = True

            
        elif menu == MENU_MIXING_DURATION:
            if start_time_selection:
                start_time_selection = False
                location = time_increment_selection
            else:
                if location == sprites:
                    menu = MENU_MIXING_SETTINGS
                elif location == 0:
                    time_increment_selection = 0
                    start_time_selection = True
                elif location == 1:
                    time_increment_selection = 1
                    start_time_selection = True
                elif location == 2:
                    time_increment_selection = 2
                    start_time_selection = True


        elif menu == MENU_MIXING_START_TIME:
            if start_time_selection:
                start_time_selection = False
                location = time_increment_selection
            else:
                if location == sprites:
                    menu = MENU_MIXING_SETTINGS
                elif location == 0:
                    time_increment_selection = 0
                    start_time_selection = True
                elif location == 1:
                    time_increment_selection = 1
                    start_time_selection = True
                elif location == 2:
                    time_increment_selection = 2
                    start_time_selection = True


        elif menu == MENU_1COMPONENT_SELECT:
            if location == sprites:
                menu = MENU_SETTINGS
            else:
                components_amount = 1
                component = location
                menu = MENU_1COMPONENT_WEIGHT
                component = location
        elif menu == MENU_1COMPONENT_WEIGHT:
            if location == sprites:
                menu = MENU_1COMPONENT_SELECT
            elif weight_1component_progress > 0:
                weight = weight_1component_progress
                menu = MENU_DISPENSING
        location = 0
        if menu == MENU_MIXING_SETTINGS:
            location = mixing_settings_form_state["location"]


    if menu == MENU_START: #draw start menu
        sprites = 4
        screen.blit(menu0_text, menu0_text_rect)  # draw menu text in the center of the screen
        draw_selection_cursor()
        screen.blit(settings_image, settings_image_rect)  # draw settings image
        screen.blit(two_component_image, two_component_image_rect)  # draw button 1
        screen.blit(two_component_text, two_component_text_rect)  # draw two component text
        screen.blit(four_component_image, four_component_image_rect)  # draw button 2
        screen.blit(four_component_text, four_component_text_rect)  # draw four component text
        screen.blit(button3_image, button3_image_rect)  # draw button 3
        screen.blit(mixing_menu_text, mixing_menu_text_rect)  # draw mixing menu text
        screen.blit(settings_text, settings_text_rect)  # draw settings text

        if dispense_warning_message:
            warn_text, warn_rect = create_text(dispense_warning_message, (width // 2, 130), theme.WARNING, "small")
            screen.blit(warn_text, warn_rect)
        low_buckets = [str(i + 1) for i in range(4)
                       if saved_settings.bucket_volume(i) < LOW_VOLUME_THRESHOLD_ML]
        if low_buckets:
            low_text_str = "Low bucket volume: " + ", ".join(low_buckets)
            low_text, low_rect = create_text(low_text_str, (width // 2, height - 30), theme.CAUTION, "small")
            screen.blit(low_text, low_rect)

    if menu == MENU_2COMPONENT_SELECTION: #draw 2 component selection menu
        sprites = 2
        screen.blit(menu1_text, menu1_text_rect)  # draw menu text in the center of the screen
        draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(button_bottle_ab_image, button_bottle_ab_image_rect)  # draw component A image
        screen.blit(button_bottle_cd_image, button_bottle_cd_image_rect)  # draw component B image

    if menu == MENU_2COMPONENT_WEIGHT: #draw 2 component weight selection menu
        sprites = 1
        screen.blit(menu1_text, menu1_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        weight_bar_width = abs(weight_2component_progress)*scaling_weight_2
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(x_bar_weight_2, 3/4*height))  # update loading bar position
        if weight_2component_progress <= max_weight_2component and weight_2component_progress >= 0:
            draw_bar_track(x_bar_weight_2, weight_bar_image_use_rect.y, max_weight_2component*scaling_weight_2)
            screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
            weight_text,weight_rect = create_text(f"Desired weight: {weight_2component_progress} g", (width // 2, height // 2), TEXT_COLOR)
            screen.blit(weight_text, weight_rect)  # draw weight text in the center
        else:
            screen.blit(return_,return_rect)

    if menu == MENU_4COMPONENT_WEIGHT: #draw 4 component weight selection menu
        sprites = 1
        screen.blit(menu2_text, menu2_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

        weight_bar_width = abs(weight_4component_progress)*scaling_weight_4
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(x_bar_weight_4, 3/4*height))  # update loading bar position
        if weight_4component_progress <= max_weight_4component and weight_4component_progress >= 0:
            draw_bar_track(x_bar_weight_4, weight_bar_image_use_rect.y, max_weight_4component*scaling_weight_4)
            screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
            weight_text,weight_rect = create_text(f"Total desired weight: {weight_4component_progress} g", (width // 2, height // 2), TEXT_COLOR)
            screen.blit(weight_text, weight_rect)  # draw weight text in the center
        else:
            screen.blit(return_,return_rect)

    if menu == MENU_4COMPONENT_HARDNESS: #draw 4 component hardness selection menu
        sprites = 1
        screen.blit(menu3_text, menu3_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

        hardness_bar_width = (hardness_4component_progress - min_hardness_4component)*scaling_hardness_4
        hardness_bar_image_use = pygame.transform.scale(hardness_bar_image, (max(int(hardness_bar_width), 1), 50))  # scale loading bar based on selected weight
        hardness_bar_image_use_rect = hardness_bar_image_use.get_rect(midleft=(x_bar_har_4, 3/4*height))  # update loading bar position
        if min_hardness_4component <= hardness_4component_progress <= max_hardness_4component:
            draw_bar_track(x_bar_har_4, hardness_bar_image_use_rect.y, hardness_4component_span*scaling_hardness_4)
            screen.blit(hardness_bar_image_use, hardness_bar_image_use_rect)  # draw loading bar
            hardness_text,hardness_rect = create_text(f"Desired hardness: {hardness_4component_progress} shore", (width // 2, height // 2), TEXT_COLOR)
            screen.blit(hardness_text, hardness_rect)  # draw hardness text in the center
        else:
            screen.blit(return_,return_rect)

        

    
    if menu == MENU_MIX_CONFIRM: #draw start mixing confirmation menu
        if location == 2:
            location = 1
        sprites = 2
        screen.blit(menu4_text, menu4_text_rect)  # draw menu text in the center of the screen
        draw_selection_cursor()
        screen.blit(yes_image, yes_image_rect)  # draw yes image
        screen.blit(no_image, no_image_rect)  # draw no image


    if menu == MENU_SETTINGS: #draw settings menu
        sprites = 3
        screen.blit(menu5_text, menu5_text_rect)  # draw menu text in the center of the screen
        draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner   
        screen.blit(mixing_settings_text, mixing_settings_text_rect)  # draw mixing settings text
        screen.blit(replace_cartridge_text, replace_cartridge_text_rect)  # draw replace cartridge text
        screen.blit(one_component_dispensing_text, one_component_dispensing_text_rect)  # draw settings image
        screen.blit(one_component_dispensing_line2_text, one_component_dispensing_line2_text_rect)  # draw settings image

    if menu == MENU_MIXING_SETTINGS: #draw mixing settings menu
        sprites = 3
        screen.blit(menu6_text, menu6_text_rect)  # draw menu text in the center of the screen
        mixing_settings_form.draw(screen, width, height, mixing_settings_form_state, create_text)
        if location == sprites:
            draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner


    if menu == MENU_MIXING_FREQUENCY: #draw frequency of mixing menu
        sprites = 3
        screen.blit(menu9_text, menu9_text_rect)  # draw menu text in the center of the screen
        display_time_selection(width, height, time_frequency, location, start_time_selection)  # draw time selection
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

    if menu == MENU_MIXING_DURATION: #draw duration of mixing menu
        sprites = 3
        screen.blit(menu10_text, menu10_text_rect)  # draw menu text in the center of the screen
        display_time_selection(width, height, time_duration, location, start_time_selection)  # draw time selection
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner


    if menu == MENU_MIXING_START_TIME: #draw start time of mixing menu
        sprites = 3
        screen.blit(menu11_text, menu11_text_rect)  # draw menu text in the center of the screen
        display_time_selection(width, height, time_start_time, location, start_time_selection)  # draw time selection
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    

    if menu == MENU_REPLACE_CARTRIDGE: #draw cartridge replacement menu (pick which bucket)
        sprites = 4
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(select_cartridge_text, select_cartridge_text_rect)  # draw select bucket text

        screen.blit(button_bottle_a_image, button_bottle_a_image_rect)  # bucket 1
        screen.blit(button_bottle_b_image, button_bottle_b_image_rect)  # bucket 2
        screen.blit(button_bottle_c_image, button_bottle_c_image_rect)  # bucket 3
        screen.blit(button_bottle_d_image, button_bottle_d_image_rect)  # bucket 4

    if menu == MENU_REPLACE_WEIGHT: #Select replacement volume
        sprites = 1
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

        volume_bar_progress = min(max(volume_replacement_progress, 0.0), max_volume_replacement)
        volume_bar_track_width = max_volume_replacement*scaling_volume_replacement
        volume_bar_width = volume_bar_progress*scaling_volume_replacement
        volume_bar_image_use = pygame.transform.scale(weight_bar_image, (max(int(volume_bar_width), 1), 50))  # scale loading bar based on selected volume
        volume_bar_image_use_rect = volume_bar_image_use.get_rect(midleft=(x_bar_volume_re, 3/4*height))  # update loading bar position
        volume_bar_track_rect = pygame.Rect(x_bar_volume_re, volume_bar_image_use_rect.y, int(volume_bar_track_width), 50)
        cartridge_volume_text, cartridge_volume_text_rect = create_text(f"Total bucket volume: {int(volume_replacement_progress)} ml", (width // 2, height // 2), TEXT_COLOR)
        screen.blit(cartridge_volume_text, cartridge_volume_text_rect)  # draw volume text in the center
        draw_bar_track(volume_bar_track_rect.x, volume_bar_track_rect.y, volume_bar_track_rect.width)
        screen.blit(volume_bar_image_use, volume_bar_image_use_rect)  # draw loading bar

    if menu == MENU_1COMPONENT_SELECT: #draw one component component selection menu
        sprites = 4
        screen.blit(menu12_text, menu12_text_rect)  # draw menu text in the center of the screen
        draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

        screen.blit(button_bottle_a_image, button_bottle_a_image_rect)  # draw button 1
        screen.blit(button_bottle_b_image, button_bottle_b_image_rect)  # draw button 2
        screen.blit(button_bottle_c_image, button_bottle_c_image_rect)  # draw button 3
        screen.blit(button_bottle_d_image, button_bottle_d_image_rect)  # draw button 4

    if menu == MENU_1COMPONENT_WEIGHT: #draw one component dispensing amount selection menu
        sprites = 1
        screen.blit(menu13_text, menu13_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            draw_selection_cursor()
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

        weight_bar_width = abs(weight_1component_progress)*scaling_weight_1
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(x_bar_weight_1, 3/4*height))  # update loading bar position
        if weight_1component_progress <= max_weight_1component and weight_1component_progress >= 0:
            draw_bar_track(x_bar_weight_1, weight_bar_image_use_rect.y, max_weight_1component*scaling_weight_1)
            screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
            weight_text,weight_rect = create_text(f"Desired weight: {weight_1component_progress} g", (width // 2, height // 2), TEXT_COLOR)
            screen.blit(weight_text, weight_rect)  # draw weight text in the center
        else:
            screen.blit(return_,return_rect)
    
    if menu == MENU_DISPENSING: #draw loading bar
        sprites = 4
        if not dispense_started:
            multi_components = [0,0,0,0]  # Dispensing screen UI: desired grams per component prepared before starting the worker thread.
            if(components_amount == 1):
                print(weight,component)
                multi_components[component] = weight
            elif(components_amount == 2):
                print(weight,component)
                multi_components[component*2] = weight/2
                multi_components[component*2+1] = weight/2
            elif(components_amount == 4):
                multi_components = saved_settings.component_amounts_for_hardness(weight, hardness)
                print(weight, hardness, saved_settings.hardness_to_ratio(hardness), multi_components)
            else:
                dispense_warning_message = "No dispense amount selected"
                menu = MENU_START
                location = 0

            if menu == MENU_DISPENSING:
                requested_ml = [multi_components[i] / dispense.density_of_liquid for i in range(4)]  # Dispensing screen UI: requested component volume used for bucket volume checks.
                short = [str(i + 1) for i in range(4) if requested_ml[i] > saved_settings.bucket_volume(i)]  # Dispensing screen UI: bucket numbers that do not have enough volume.
                if short:
                    dispense_warning_message = "Insufficient bucket volume (" + ", ".join(short) + ") — refill before dispensing"
                    print(dispense_warning_message)
                    for i in range(4):
                        print(f"  Bucket {i + 1} needs {requested_ml[i]:.1f} ml, has {saved_settings.bucket_volume(i)} ml")
                    menu = MENU_START
                    location = 0
                elif not dispensing_job.start(multi_components, dispense):
                    dispense_warning_message = "Dispensing is already running"
                    menu = MENU_START
                    location = 0
                else:
                    dispense_started = True
        if dispense_started:
            dispense_snapshot = dispensing_job.snapshot()  # Dispensing screen UI: thread-safe copy of worker progress for drawing.
            dispensing_progress_view.draw(screen, dispense_snapshot)
            if dispense_snapshot["done"]:
                if dispense_snapshot["error"]:
                    dispense_warning_message = "Dispensing error: " + dispense_snapshot["error"]
                dispensing_job.reset()
                menu = MENU_START
                location = 0
                dispense_started = False
                loading_progress = 0
            #resetting variables for next mixing session
            weight_1component_progress = max_weight_1component//2
            weight_2component_progress = max_weight_2component//2
            weight_4component_progress = max_weight_4component//2
            hardness_4component_progress = (min_hardness_4component + max_hardness_4component) // 2

    if menu != previous_menu:
        if menu != MENU_MIX_CONFIRM:
            location = 0
        else: 
            location = 1

        previous_menu = menu
    top_bar.draw(screen)
    pygame.display.flip()           # update display
pygame.quit()
