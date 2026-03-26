#python -m venv dispenser_venv
#dispenser_venv\Scripts\activate

import pygame
from pygame.locals import *
import pygame.gfxdraw
import time
import threading

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
MENU_REPLACE_HARDNESS = 14
MENU_DISPENSING = -1


def load_image(path, size, location):
    image = pygame.image.load(path)
    image = pygame.Surface.convert_alpha(image)
    image = pygame.transform.scale(image, size)
    image_rect = image.get_rect()
    image_rect.center = location
    return image, image_rect

pygame.font.init()

# Create a font (font name, size) - None uses the default font
font = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)
font_big = pygame.font.SysFont(None, 72)

def create_text(text, position, color=(255,255,255), font_type="normal"):
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
            selection_image_rect.center = (width-50, height-50)
            screen.blit(selection_image, selection_image_rect)  # draw cursor
    #draw days hours and minutes
    day_text, day_text_rect = create_text(f"{day}", (width /6, height // 2+25), (0,0,0),"big")
    screen.blit(day_text, day_text_rect)  # draw days
    hour_text, hour_text_rect = create_text(f"{hour}", (width/6*3, height // 2+25), (0,0,0),"big")
    screen.blit(hour_text, hour_text_rect)  # draw hours
    minute_text, minute_text_rect = create_text(f"{minute}", (width /6*5, height // 2+25), (0,0,0),"big")
    screen.blit(minute_text, minute_text_rect)  # draw minutes
    partition_text, partition_text_rect = create_text(":", (width/6*2, height // 2+25), (0,0,0),"big")
    screen.blit(partition_text, partition_text_rect)  # draw :
    partition_text, partition_text_rect = create_text(":", (width/6*4, height // 2+25), (0,0,0),"big")
    screen.blit(partition_text, partition_text_rect)  # draw :
    # annotate days hours and minutes
    day_annotate_text, day_annotate_text_rect = create_text("DAYS", (width /6, height // 2-25), (0,0,0),"small")
    screen.blit(day_annotate_text, day_annotate_text_rect)  # draw annotation day
    hour_annotate_text, hour_annotate_text_rect = create_text("HOURS", (width/6*3, height // 2-25), (0,0,0),"small")
    screen.blit(hour_annotate_text, hour_annotate_text_rect)  # draw annotation hour
    minute_annotate_text, minute_annotate_text_rect = create_text("MINUTES", (width /6*5, height // 2-25), (0,0,0),"small")
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

pygame.init()
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((960, 240))
width, height = screen.get_size()

pygame.display.set_caption('Dispenser Interface')
menu = MENU_START
location = 0
time_frequency, time_duration, time_start_time = [0,0,0], [0,0,0], [0,0,0]
start_time_selection = False
sprites = 4
previous_menu = MENU_START
button_size = (75,75)



#Maak teks voor tijdens mengen
mengen_bezig, mengen_bezig_rect = create_text("MIXING", (width // 2, height // 2), (255,255,255))
#Text menu MENU_START
menu0_text, menu0_text_rect = create_text("START", (width // 2, 25), (0,0,0))

#Text menu MENU_2COMPONENT_WEIGHT
menu1_text, menu1_text_rect = create_text("2 component dispensing", (width // 2, 25), (0,0,0))
#Text menu MENU_4COMPONENT_WEIGHT
menu2_text, menu2_text_rect = create_text("4 component dispensing", (width //2, 25), (0,0,0))
#Text menu MENU_4COMPONENT_HARDNESS
menu3_text, menu3_text_rect = create_text("4 component dispensing", (width // 2, 25), (0,0,0))
#Text menu MENU_MIX_CONFIRM
menu4_text, menu4_text_rect = create_text("Would you like to start mixing?", (width // 2, 25), (0,0,0))
#Text menu MENU_SETTINGS
menu5_text, menu5_text_rect = create_text("Settings", (width // 2, 25), (0,0,0))
#Text menu MENU_MIXING_SETTINGS
menu6_text, menu6_text_rect = create_text("Mixing Settings", (width // 2, 25), (0,0,0))
#Text menu MENU_REPLACE_CARTRIDGE
menu7_text, menu7_text_rect = create_text("Replace cartridge", (width // 2, 25), (0,0,0))
#Text menu MENU_REPLACE_WEIGHT
menu8_text, menu8_text_rect = create_text("Select hardness of new cartridge", (width // 2, 25), (0,0,0))
#Text menu MENU_MIXING_FREQUENCY
menu9_text, menu9_text_rect = create_text("Time between mixes", (width // 2, 25), (0,0,0))
#Text menu MENU_MIXING_DURATION
menu10_text, menu10_text_rect = create_text("Select mixing duration", (width // 2, 25), (0,0,0))
#Text menu MENU_MIXING_START_TIME
menu11_text, menu11_text_rect = create_text("Select time until next mix", (width // 2, 25), (0,0,0))
#Text menu MENU_1COMPONENT_SELECT
menu12_text, menu12_text_rect = create_text("Select component to dispense", (width // 2, 25), (0,0,0))
#Text menu MENU_1COMPONENT_WEIGHT
menu13_text, menu13_text_rect = create_text("Select desired weight", (width // 2, 25), (0,0,0))

loci = locus(4)
#menus names text
two_component_text,two_component_text_rect = create_text("2 component", (loci[0][0], loci[0][1]+50), (0,0,0), "small")
four_component_text, four_component_text_rect = create_text("4 component", (loci[1][0], loci[1][1]+50), (0,0,0), "small")
mixing_menu_text, mixing_menu_text_rect = create_text("Mixing", (loci[2][0], loci[2][1]+50), (0,0,0), "small")
settings_text, settings_text_rect = create_text("Settings", (loci[3][0], loci[3][1]+50), (0,0,0), "small")

loci = locus(3)
#Setting options text
mixing_settings_text, mixing_settings_text_rect = create_text("Mixing settings", (loci[0][0], loci[0][1]+50), (0,0,0), "small")
replace_cartridge_text, replace_cartridge_text_rect = create_text("Replace cartridge", (loci[1][0], loci[1][1]+50), (0,0,0), "small")
one_component_dispensing_text, one_component_dispensing_text_rect = create_text("One component", (loci[2][0], loci[2][1]+50), (0,0,0), "small")
one_component_dispensing_line2_text, one_component_dispensing_line2_text_rect = create_text("dispensing", (loci[2][0], loci[2][1]+75), (0,0,0), "small")

loci = locus(3)
#mixing settings options text
frequency_text, frequency_text_rect = create_text("Mixing frequency", (loci[0][0], loci[0][1]+50), (0,0,0), "small")
duration_text, duration_text_rect = create_text("Mixing duration", (loci[1][0], loci[1][1]+50), (0,0,0), "small")
mixing_start_time_text, mixing_start_time_text_rect = create_text("Time until", (loci[2][0], loci[2][1]+50), (0,0,0), "small")
mixing_start_time_line2_text, mixing_start_time_line2_text_rect = create_text("next mix", (loci[2][0], loci[2][1]+75), (0,0,0), "small")


#cartridge replacement options text
select_cartridge_text, select_cartridge_text_rect = create_text("Select cartridge that is replaced", (width/2, height/2+50), (0,0,0), "small")

loci = locus(4)
#load in selection sprite
selection_image, selection_image_rect = load_image(r'./Sprites/rond.png', (100, 100), loci[0])

#loud in 2 component mixing sprite
two_component_image, two_component_image_rect = load_image(r'./Sprites/button_2comp.png',(175,175),loci[0])

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
weight_1component_progress = 50
weight_2component_progress = 50
weight_4component_progress = 50
weight_replacement_progress = 50
weight_bar_width = 8
weight_bar_image, weight_bar_image_rect = load_image(r'./Sprites/black.png',(weight_bar_width,weight_1component_progress) ,(200, height//2))
hardness_4component_progress = 25
hardness_replacement_progress = 25
hardness_bar_width = 8
hardness_bar_image, hardness_bar_image_rect = load_image(r'./Sprites/black.png',(hardness_bar_width,hardness_4component_progress) ,(200, height//2))



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
button_bottle_d_image, button_bottle_d_image_rect = load_image(r'./Sprites/button_bottle_d.png', bottle_img_size, (loci[3]))

loci = locus(2)
#load yes and no sprite
yes_image, yes_image_rect = load_image(r'./Sprites/YES.png', button_size, (loci[0]))
no_image, no_image_rect = load_image(r'./Sprites/no.png', button_size, (loci[1]))



running = True
while running:
    loci = locus(sprites)
    selection_image_rect.center = (loci[location]) 

    screen.fill((255, 255, 255))          # clear screen (white background)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_RIGHT: #changing location
                location += 1
                location = available_locations(location, "right", sprites)
                if menu == MENU_2COMPONENT_WEIGHT:
                    if weight_2component_progress < 100:
                        location  = 0
                        weight_2component_progress += 1
                    else:
                        weight_2component_progress = 100
                        location = sprites

                elif menu == MENU_4COMPONENT_WEIGHT:
                    if weight_4component_progress < 100:
                        location  = 0
                        weight_4component_progress += 1
                    else:
                        weight_4component_progress = 100
                        location = sprites
                elif menu == MENU_4COMPONENT_HARDNESS:
                    if hardness_4component_progress < 50:
                        location  = 0
                        hardness_4component_progress += 1
                    else:
                        hardness_4component_progress = 50
                        location = sprites
                elif menu == MENU_MIX_CONFIRM:
                    if location == 2:
                        location = 0
                elif menu == MENU_REPLACE_WEIGHT:
                    if weight_replacement_progress < 100:
                        location  = 0
                        weight_replacement_progress += 1
                    else:
                        weight_replacement_progress = 100
                        location = sprites
                elif menu == MENU_REPLACE_HARDNESS:
                    if hardness_replacement_progress < 50:
                        location  = 0
                        hardness_replacement_progress += 1
                    else:
                        hardness_replacement_progress = 50
                        location = sprites
                elif menu == MENU_MIXING_FREQUENCY:
                    if start_time_selection:
                        time_frequency = select_time(time_frequency, "right", time_increment_selection)
                elif menu == MENU_MIXING_DURATION:
                    if start_time_selection:
                        time_duration = select_time(time_duration, "right", time_increment_selection)
                elif menu == MENU_MIXING_START_TIME:
                    if start_time_selection:
                        time_start_time = select_time(time_start_time, "right", time_increment_selection)
                elif menu == MENU_1COMPONENT_WEIGHT:
                    if weight_1component_progress < 100:
                        location  = 0
                        weight_1component_progress += 1
                    else:
                        weight_1component_progress = 100
                        location = sprites

            elif event.key == pygame.K_LEFT:
                location -= 1
                location = available_locations(location, "left", sprites)
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
                    if hardness_4component_progress > 0:
                        location  = 0
                        hardness_4component_progress -= 1
                    else:
                        hardness_4component_progress = 0
                        location = sprites
                elif menu == MENU_MIX_CONFIRM:
                    if location == 2:
                        location = 1
                elif menu == MENU_REPLACE_WEIGHT:
                    if weight_replacement_progress > 0:
                        location  = 0
                        weight_replacement_progress -= 1
                    else:
                        weight_replacement_progress = 0
                        location = sprites
                elif menu == MENU_REPLACE_HARDNESS:
                    if hardness_replacement_progress > 0:
                        location  = 0
                        hardness_replacement_progress -= 1
                    else:
                        hardness_replacement_progress = 0
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
                elif menu == MENU_1COMPONENT_WEIGHT:
                    if weight_1component_progress > 0:
                        location  = 0
                        weight_1component_progress -= 1
                    else:
                        weight_1component_progress = 0
                        location = sprites

            elif event.key == pygame.K_RETURN: #state machine for menu navigation
                if menu == MENU_START:
                    if location == 0:
                        menu = MENU_2COMPONENT_WEIGHT
                        location = 1
                    elif location == 1:
                        menu = MENU_4COMPONENT_WEIGHT
                    elif location == 2:
                        menu = MENU_MIX_CONFIRM
                    elif location == 3:
                        menu = MENU_SETTINGS
                        location = 2
                    elif location == sprites:
                        menu = MENU_START
                elif menu == MENU_2COMPONENT_WEIGHT:
                    if location == 4:
                        menu = MENU_START
                    else:
                        menu = MENU_DISPENSING
                elif menu == MENU_4COMPONENT_WEIGHT:
                    if location == sprites:
                        menu = MENU_START
                    else:
                        menu = MENU_4COMPONENT_HARDNESS
                elif menu == MENU_4COMPONENT_HARDNESS:
                    if location == sprites:
                        menu = MENU_START
                    else:
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
                    if location == 0:
                        menu = MENU_MIXING_FREQUENCY
                    elif location == 1:
                        menu = MENU_MIXING_DURATION
                    elif location == 2:
                        menu = MENU_MIXING_START_TIME
                    elif location == sprites:
                        menu = MENU_SETTINGS
                elif menu == MENU_REPLACE_CARTRIDGE:
                    if location == sprites:
                        menu = MENU_SETTINGS
                    else:
                        menu = MENU_REPLACE_WEIGHT
                elif menu == MENU_REPLACE_WEIGHT:
                    if location == sprites:
                        menu = MENU_REPLACE_CARTRIDGE
                    else:
                        menu = MENU_REPLACE_HARDNESS
                elif menu == MENU_REPLACE_HARDNESS:
                    if location == sprites:
                        menu = MENU_REPLACE_WEIGHT
                    else:
                        menu = MENU_DISPENSING
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
                        menu = MENU_1COMPONENT_WEIGHT
                elif menu == MENU_1COMPONENT_WEIGHT:
                    if location == sprites:
                        menu = MENU_1COMPONENT_SELECT
                    else:
                        menu = MENU_DISPENSING

    if menu == MENU_START: #draw start menu
        sprites = 4
        screen.blit(menu0_text, menu0_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(settings_image, settings_image_rect)  # draw settings image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(two_component_image, two_component_image_rect)  # draw button 1
        screen.blit(two_component_text, two_component_text_rect)  # draw two component text
        screen.blit(four_component_image, four_component_image_rect)  # draw button 2
        screen.blit(four_component_text, four_component_text_rect)  # draw four component text
        screen.blit(button3_image, button3_image_rect)  # draw button 3
        screen.blit(mixing_menu_text, mixing_menu_text_rect)  # draw mixing menu text
        screen.blit(settings_text, settings_text_rect)  # draw settings text

    if menu == MENU_2COMPONENT_WEIGHT: #draw 2 component weight selection menu
        sprites = 1
        screen.blit(menu1_text, menu1_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        weight_bar_width = abs(weight_2component_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Desired weight: {weight_2component_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center

    if menu == MENU_4COMPONENT_WEIGHT: #draw 4 component weight selection menu
        sprites = 1
        screen.blit(menu2_text, menu2_text_rect)  # draw menu text in the center of the screen
        if location == sprites:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        weight_bar_width = abs(weight_4component_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Total desired weight: {weight_4component_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center

    if menu == MENU_4COMPONENT_HARDNESS: #draw 4 component hardness selection menu
        sprites = 1
        screen.blit(menu3_text, menu3_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == sprites:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        hardness_bar_width = abs(hardness_4component_progress)*width/2//50
        hardness_bar_image_use = pygame.transform.scale(hardness_bar_image, (int(hardness_bar_width), 50))  # scale loading bar based on selected weight
        hardness_bar_image_use_rect = hardness_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(hardness_bar_image_use, hardness_bar_image_use_rect)  # draw loading bar
        hardness_text,hardness_rect = create_text(f"Desired hardness: {hardness_4component_progress}", (width // 2, height // 2), (0,0,0))
        screen.blit(hardness_text, hardness_rect)  # draw hardness text in the center

    
    if menu == MENU_MIX_CONFIRM: #draw start mixing confirmation menu
        if location == 2:
            location = 1
        sprites = 2
        screen.blit(menu4_text, menu4_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(yes_image, yes_image_rect)  # draw yes image
        screen.blit(no_image, no_image_rect)  # draw no image


    if menu == MENU_SETTINGS: #draw settings menu
        sprites = 3
        screen.blit(menu5_text, menu5_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner   
        screen.blit(mixing_settings_text, mixing_settings_text_rect)  # draw mixing settings text
        screen.blit(replace_cartridge_text, replace_cartridge_text_rect)  # draw replace cartridge text
        screen.blit(one_component_dispensing_text, one_component_dispensing_text_rect)  # draw settings image
        screen.blit(one_component_dispensing_line2_text, one_component_dispensing_line2_text_rect)  # draw settings image

    if menu == MENU_MIXING_SETTINGS: #draw mixing settings menu
        sprites = 3
        screen.blit(menu6_text, menu6_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(frequency_text, frequency_text_rect)  # draw frequency text
        screen.blit(duration_text, duration_text_rect)  # draw duration text
        screen.blit(mixing_start_time_text, mixing_start_time_text_rect)  # draw mixing start time text
        screen.blit(mixing_start_time_line2_text, mixing_start_time_line2_text_rect)  # draw mixing start time text


    if menu == MENU_MIXING_FREQUENCY: #draw frequency of mixing menu
        sprites = 3
        screen.blit(menu9_text, menu9_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        display_time_selection(width, height, time_frequency, location, start_time_selection)  # draw time selection

    if menu == MENU_MIXING_DURATION: #draw duration of mixing menu
        sprites = 3
        screen.blit(menu10_text, menu10_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        display_time_selection(width, height, time_duration, location, start_time_selection)  # draw time selection

    if menu == MENU_MIXING_START_TIME: #draw start time of mixing menu
        sprites = 3
        screen.blit(menu11_text, menu11_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        display_time_selection(width, height, time_start_time, location, start_time_selection)  # draw time selection
    

    if menu == MENU_REPLACE_CARTRIDGE: #draw cartridge replacement menu
        sprites = 4
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(select_cartridge_text, select_cartridge_text_rect)  # draw select cartridge text

        screen.blit(button_bottle_a_image, button_bottle_a_image_rect)  # draw button 1
        screen.blit(button_bottle_b_image, button_bottle_b_image_rect)  # draw button 2
        screen.blit(button_bottle_c_image, button_bottle_c_image_rect)  # draw button 3
        screen.blit(button_bottle_d_image, button_bottle_d_image_rect)  # draw button 4

    if menu == MENU_REPLACE_WEIGHT: #Select replacement weight
        sprites = 1
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == sprites:
            screen.blit(selection_image, selection_image_rect)  # draw cursor

        weight_bar_width = abs(weight_replacement_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        cartridge_weight_text, cartridge_weight_text_rect = create_text(f"Weight of new cartridge: {weight_replacement_progress}", (width // 2, height // 2), (0,0,0))
        screen.blit(cartridge_weight_text, cartridge_weight_text_rect)  # draw hardness text in the center

    if menu == MENU_REPLACE_HARDNESS: #Select replacement hardness
        sprites = 1
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == sprites:
            screen.blit(selection_image, selection_image_rect)  # draw cursor

        hardness_bar_width = abs(hardness_replacement_progress)*width/2//50
        hardness_bar_image_use = pygame.transform.scale(hardness_bar_image, (int(hardness_bar_width), 50))  # scale loading bar based on selected weight
        hardness_bar_image_use_rect = hardness_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(hardness_bar_image_use, hardness_bar_image_use_rect)  # draw loading bar
        cartridge_hardness_text, cartridge_hardness_text_rect = create_text(f"Hardness of new cartridge: {hardness_replacement_progress}", (width // 2, height // 2), (0,0,0))
        screen.blit(cartridge_hardness_text, cartridge_hardness_text_rect)  # draw hardness text in the center

    if menu == MENU_1COMPONENT_SELECT: #draw one component component selection menu
        sprites = 4
        screen.blit(menu12_text, menu12_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner

        screen.blit(button_bottle_a_image, button_bottle_a_image_rect)  # draw button 1
        screen.blit(button_bottle_b_image, button_bottle_b_image_rect)  # draw button 2
        screen.blit(button_bottle_c_image, button_bottle_c_image_rect)  # draw button 3
        screen.blit(button_bottle_d_image, button_bottle_d_image_rect)  # draw button 4

    if menu == MENU_1COMPONENT_WEIGHT: #draw one component dispensing amount selection menu
        sprites = 1
        screen.blit(menu13_text, menu13_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == sprites:
            screen.blit(selection_image, selection_image_rect)  # draw cursor

        weight_bar_width = abs(weight_1component_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Desired weight: {weight_1component_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center
    
    if menu == MENU_DISPENSING: #draw loading bar
        sprites = 4
        if threading.active_count() == 1:  # check if the work thread is not already running
            threading.Thread(target=doWork).start()  # start the work in a separate thread
        screen.fill((0,0,0))          # clear screen (black background)
        screen.blit(mengen_bezig, mengen_bezig_rect)  # draw "mengen bezig" text in the center of the screen
        #progress bar for loading
        if loading_progress < 100:
            loading_bar_width = loading_progress*width/2//100
            loading_bar_image = pygame.transform.scale(loading_bar_image, (int(loading_bar_width), 50))  # scale loading bar based on progress
            loading_bar_image_rect = loading_bar_image.get_rect(midleft=(200, 3/4*height))  # update loading bar position
            screen.blit(loading_bar_image, loading_bar_image_rect)  # draw loading bar
        elif loading_progress >= 100:
            menu = MENU_START
            location = 0
        #resetting variables for next mixing session
        weight_1component_progress = 50
        weight_2component_progress = 50
        weight_4component_progress = 50
        hardness_4component_progress = 25

    if menu != previous_menu:
        if menu != MENU_MIX_CONFIRM:
            location = 0
        else: 
            location = 1

        previous_menu = menu
    pygame.display.flip()           # update display
pygame.quit()
