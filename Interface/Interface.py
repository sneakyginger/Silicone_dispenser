#python -m venv dispenser_venv
#dispenser_venv\Scripts\activate

import pygame
from pygame.locals import *
import time
import threading



def load_image(path, size, location):
    image = pygame.image.load(path)
    image.convert_alpha()
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
        elif location == 4:
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


pygame.init()
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen = pygame.display.set_mode((960, 240))
width, height = screen.get_size()

pygame.display.set_caption('Dispenser Interface')
loci = [(width/5, height/2), (width/5*2, height/2), (width/5*3, height/2), (width/5*4, height/2), (width-50, height-50)]
menu = 0
location = 0
time_frequency, time_duration, time_start_time = [0,0,0], [0,0,0], [0,0,0]
start_time_selection = False

def available_locations(current_location, direction, options):
    if direction == "right":
        while not current_location in options:
            current_location += 1
            if current_location > 4:
                current_location = 0
    elif direction == "left":
        while not current_location in options:
            current_location -= 1
            if current_location < 0:
                current_location = 4
    return current_location

#Maak teks voor tijdens mengen
mengen_bezig, mengen_bezig_rect = create_text("MIXING", (width // 2, height // 2), (255,255,255))
#Text menu 0
menu0_text, menu0_text_rect = create_text("START", (width // 2, 25), (0,0,0))

#Text menu 1
menu1_text, menu1_text_rect = create_text("2 component dispensing", (width // 2, 25), (0,0,0))
#Text menu 2
menu2_text, menu2_text_rect = create_text("4 component dispensing", (width //2, 25), (0,0,0))
#Text menu 3
menu3_text, menu3_text_rect = create_text("4 component dispensing", (width // 2, 25), (0,0,0))
#Text menu 4
menu4_text, menu4_text_rect = create_text("Would you like to start mixing?", (width // 2, 25), (0,0,0))
#Text menu 5
menu5_text, menu5_text_rect = create_text("Settings", (width // 2, 25), (0,0,0))
#Text menu 6
menu6_text, menu6_text_rect = create_text("Mixing Settings", (width // 2, 25), (0,0,0))
#Text menu 7
menu7_text, menu7_text_rect = create_text("Replace cartridge", (width // 2, 25), (0,0,0))
#Text menu 8
menu8_text, menu8_text_rect = create_text("Select hardness of new cartridge", (width // 2, 25), (0,0,0))
#Text menu 9
menu9_text, menu9_text_rect = create_text("Time between mixes", (width // 2, 25), (0,0,0))
#Text menu 10
menu10_text, menu10_text_rect = create_text("Select mixing duration", (width // 2, 25), (0,0,0))
#Text menu 11
menu11_text, menu11_text_rect = create_text("Select mixing start time", (width // 2, 25), (0,0,0))

#menus names text
two_component_text,two_component_text_rect = create_text("2 component", (loci[0][0], loci[0][1]+50), (0,0,0), "small")
four_component_text, four_component_text_rect = create_text("4 component", (loci[1][0], loci[1][1]+50), (0,0,0), "small")
mixing_menu_text, mixing_menu_text_rect = create_text("Mixing", (loci[2][0], loci[2][1]+50), (0,0,0), "small")
settings_text, settings_text_rect = create_text("Settings", (loci[3][0], loci[3][1]+50), (0,0,0), "small")
#Setting options text
mixing_settings_text, mixing_settings_text_rect = create_text("Mixing settings", (loci[1][0], loci[1][1]+50), (0,0,0), "small")
replace_cartridge_text, replace_cartridge_text_rect = create_text("Replace cartridge", (loci[2][0], loci[2][1]+50), (0,0,0), "small")
#mixing settings options text
frequency_text, frequency_text_rect = create_text("Mixing frequency", (loci[0][0], loci[0][1]+50), (0,0,0), "small")
duration_text, duration_text_rect = create_text("Mixing duration", (loci[1][0], loci[1][1]+50), (0,0,0), "small")
mixing_start_time_text, mixing_start_time_text_rect = create_text("Mixing start time", (loci[2][0], loci[2][1]+50), (0,0,0), "small")




#cartridge replacement options text
select_cartridge_text, select_cartridge_text_rect = create_text("Select cartridge that is replaced", (width/2, height/2+50), (0,0,0), "small")

#load in selection sprite
selection_image, selection_image_rect = load_image(r'./Sprites/dispenser.png', (100, 100), loci[0])

#load in settings sprite
settings_image, settings_image_rect = load_image(r'./Sprites/settings.png', (75, 75), loci[3])

#load in return sprite
return_image, return_image_rect = load_image(r'./Sprites/return.png', (75, 75), loci[4])
#load in loading bar sprite
loading_bar_image, loading_bar_image_rect = load_image(r'./Sprites/white.png',(8,150) ,(200, height//2))
loading_progress = 0
loading_bar_width = 8
weight_bar_image, weight_bar_image_rect = load_image(r'./Sprites/black.png',(8,150) ,(200, height//2))
weight_progress = 50
weight_bar_width = 8
hardness_bar_image, hardness_bar_image_rect = load_image(r'./Sprites/black.png',(8,150) ,(200, height//2))
hardness_progress = 25
hardness_bar_width = 8


#load button sprites to test
button1_image, button1_image_rect = load_image(r'./Sprites/button.png', (75, 75), (loci[0]))
button2_image, button2_image_rect = load_image(r'./Sprites/button.png', (75, 75), (loci[1]))
button3_image, button3_image_rect = load_image(r'./Sprites/button.png', (75, 75), (loci[2]))
button4_image, button4_image_rect = load_image(r'./Sprites/button.png', (75, 75), (loci[3]))

#load yes and no sprite
yes_image, yes_image_rect = load_image(r'./Sprites/YES.png', (75, 75), (loci[1]))
no_image, no_image_rect = load_image(r'./Sprites/no.png', (75, 75), (loci[2]))



running = True
while running:
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
                if location == 5:
                    location = 0
                if menu == 1:
                    if weight_progress < 100:
                        location  = 0
                        weight_progress += 1
                    else:
                        weight_progress = 100
                        location = 4

                elif menu == 2:
                    if weight_progress < 100:
                        location  = 0
                        weight_progress += 1
                    else:
                        weight_progress = 100
                        location = 4
                elif menu == 3:
                    if hardness_progress < 50:
                        location  = 0
                        hardness_progress += 1
                    else:
                        hardness_progress = 50
                        location = 4
                elif menu == 4:
                    location = available_locations(location, "right", [1,2,4])
                elif menu == 5:  
                    location = available_locations(location, "right", [1,2,4])
                elif menu == 8:
                    if hardness_progress < 50:
                        location  = 0
                        hardness_progress += 1
                    else:
                        hardness_progress = 50
                        location = 4
                elif menu == 9:
                    location = available_locations(location, "right", [0,1,2,4])
                    if start_time_selection:
                        time_frequency = select_time(time_frequency, "right", time_increment_selection)
                elif menu == 10:
                    location = available_locations(location, "right", [0,1,2,4])
                    if start_time_selection:
                        time_duration = select_time(time_duration, "right", time_increment_selection)
                elif menu == 11:
                    location = available_locations(location, "right", [0,1,2,4])
                    if start_time_selection:
                        time_start_time = select_time(time_start_time, "right", time_increment_selection)


            elif event.key == pygame.K_LEFT:
                location -= 1
                if location == -1:
                    location = 4
                if menu == 1:
                    if weight_progress > 0:
                        location  = 0
                        weight_progress -= 1
                    else:
                        weight_progress = 0
                        location = 4
                elif menu == 2:
                    if weight_progress > 0:
                        location  = 0
                        weight_progress -= 1
                    else:
                        weight_progress = 0
                        location = 4
                elif menu == 3:
                    if hardness_progress > 0:
                        location  = 0
                        hardness_progress -= 1
                    else:
                        hardness_progress = 0
                        location = 4
                elif menu == 4:
                    location = available_locations(location, "left", [1,2,4])
                elif menu == 5:
                    location = available_locations(location, "left", [1,2,4])
                elif menu == 8:
                    if hardness_progress > 0:
                        location  = 0
                        hardness_progress -= 1
                    else:
                        hardness_progress = 0
                        location = 4
                elif menu == 9:
                    location = available_locations(location, "left", [0,1,2,4])
                    if start_time_selection:
                        time_frequency = select_time(time_frequency, "left", time_increment_selection)
                elif menu == 10:
                    location = available_locations(location, "left", [0,1,2,4])
                    if start_time_selection:
                        time_duration = select_time(time_duration, "left", time_increment_selection)
                elif menu == 11:
                    location = available_locations(location, "left", [0,1,2,4])
                    if start_time_selection:
                        time_start_time = select_time(time_start_time, "left", time_increment_selection)

            elif event.key == pygame.K_RETURN: #state machine for menu navigation
                if menu == 0:
                    if location == 0:
                        menu = 1
                        location = 1
                    elif location == 1:
                        menu = 2
                    elif location == 2:
                        menu = 4
                    elif location == 3:
                        menu = 5
                        location = 2
                    elif location == 4:
                        menu = 0
                elif menu == 1:
                    if location == 4:
                        menu = 0
                    else:
                        menu = -1
                elif menu == 2:
                    if location == 4:
                        menu = 0
                    else:
                        menu = 3
                elif menu == 3:
                    if location == 4:
                        menu = 0
                    else:
                        menu = -1
                elif menu == 4:
                    if location == 1:
                        menu = -1
                    elif location == 2:
                        menu = 0
                elif menu == 5:
                    if location == 1:
                        menu = 6
                    elif location == 2:
                        menu = 7
                    elif location == 4:
                        menu = 0
                elif menu == 6:
                    if location == 0:
                        menu = 9
                    elif location == 1:
                        menu = 10
                    elif location == 2:
                        menu = 11
                    elif location == 4:
                        menu = 5
                elif menu == 7:
                    if location == 4:
                        menu = 5
                    else:
                        menu = 8
                elif menu == 8:
                    if location == 4:
                        menu = 7
                    else:
                        menu = -1
                elif menu == 9:
                    if start_time_selection:
                        start_time_selection = False
                        location = time_increment_selection
                    else:
                        if location == 4:
                            menu = 6
                        elif location == 0:
                            time_increment_selection = 0
                            start_time_selection = True
                        elif location == 1:
                            time_increment_selection = 1
                            start_time_selection = True
                        elif location == 2:
                            time_increment_selection = 2
                            start_time_selection = True

                    
                elif menu == 10:
                    if start_time_selection:
                        start_time_selection = False
                        location = time_increment_selection
                    else:
                        if location == 4:
                            menu = 6
                        elif location == 0:
                            time_increment_selection = 0
                            start_time_selection = True
                        elif location == 1:
                            time_increment_selection = 1
                            start_time_selection = True
                        elif location == 2:
                            time_increment_selection = 2
                            start_time_selection = True
                elif menu == 11:
                    if start_time_selection:
                        start_time_selection = False
                        location = time_increment_selection
                    else:
                        if location == 4:
                            menu = 6
                        elif location == 0:
                            time_increment_selection = 0
                            start_time_selection = True
                        elif location == 1:
                            time_increment_selection = 1
                            start_time_selection = True
                        elif location == 2:
                            time_increment_selection = 2
                            start_time_selection = True

    if menu == 0: #draw start menu
        screen.blit(menu0_text, menu0_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(settings_image, settings_image_rect)  # draw settings image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(button1_image, button1_image_rect)  # draw button 1
        screen.blit(two_component_text, two_component_text_rect)  # draw two component text
        screen.blit(button2_image, button2_image_rect)  # draw button 2
        screen.blit(four_component_text, four_component_text_rect)  # draw four component text
        screen.blit(button3_image, button3_image_rect)  # draw button 3
        screen.blit(mixing_menu_text, mixing_menu_text_rect)  # draw mixing menu text
        screen.blit(settings_text, settings_text_rect)  # draw settings text

    if menu == 1: #draw 2 component weight selection menu
        screen.blit(menu1_text, menu1_text_rect)  # draw menu text in the center of the screen
        if location == 4:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        
        weight_bar_width = abs(weight_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Desired weight: {weight_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center


    if menu == 2: #draw 4 component weight selection menu
        screen.blit(menu2_text, menu2_text_rect)  # draw menu text in the center of the screen
        if location == 4:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        weight_bar_width = abs(weight_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Desired weight: {weight_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center


    if menu == 3: #draw 4 component hardness selection menu
        screen.blit(menu3_text, menu3_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == 4:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        hardness_bar_width = abs(hardness_progress)*width/2//50
        hardness_bar_image_use = pygame.transform.scale(hardness_bar_image, (int(hardness_bar_width), 50))  # scale loading bar based on selected weight
        hardness_bar_image_use_rect = hardness_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(hardness_bar_image_use, hardness_bar_image_use_rect)  # draw loading bar
        hardness_text,hardness_rect = create_text(f"Desired hardness: {hardness_progress}", (width // 2, height // 2), (0,0,0))
        screen.blit(hardness_text, hardness_rect)  # draw hardness text in the center

    
    if menu == 4: #draw start mixing confirmation menu
        screen.blit(menu4_text, menu4_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(yes_image, yes_image_rect)  # draw yes image
        screen.blit(no_image, no_image_rect)  # draw no image

    

    if menu == 5: #draw settings menu
        screen.blit(menu5_text, menu5_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner   
        screen.blit(mixing_settings_text, mixing_settings_text_rect)  # draw mixing settings text
        screen.blit(replace_cartridge_text, replace_cartridge_text_rect)  # draw replace cartridge text

    if menu == 6: #draw mixing settings menu
        screen.blit(menu6_text, menu6_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(frequency_text, frequency_text_rect)  # draw frequency text
        screen.blit(duration_text, duration_text_rect)  # draw duration text
        screen.blit(mixing_start_time_text, mixing_start_time_text_rect)  # draw mixing start time text

    if menu == 9: #draw frequency of mixing menu
        screen.blit(menu9_text, menu9_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        display_time_selection(width, height, time_frequency, location, start_time_selection)  # draw time selection

    if menu == 10: #draw duration of mixing menu
        screen.blit(menu10_text, menu10_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        display_time_selection(width, height, time_duration, location, start_time_selection)  # draw time selection

    if menu == 11: #draw start time of mixing menu
        screen.blit(menu11_text, menu11_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        display_time_selection(width, height, time_start_time, location, start_time_selection)  # draw time selection
    

    if menu == 7: #draw cartridge replacement menu
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(select_cartridge_text, select_cartridge_text_rect)  # draw select cartridge text

        screen.blit(button1_image, button1_image_rect)  # draw button 1
        screen.blit(button2_image, button2_image_rect)  # draw button 2
        screen.blit(button3_image, button3_image_rect)  # draw button 3
        screen.blit(button4_image, button4_image_rect)  # draw button 4

    if menu == 8: #Select replacement hardness
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == 4:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        hardness_bar_width = abs(hardness_progress)*width/2//50
        hardness_bar_image_use = pygame.transform.scale(hardness_bar_image, (int(hardness_bar_width), 50))  # scale loading bar based on selected weight
        hardness_bar_image_use_rect = hardness_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(hardness_bar_image_use, hardness_bar_image_use_rect)  # draw loading bar
        cartridge_hardness_text, cartridge_hardness_text_rect = create_text(f"Hardness of new cartridge: {hardness_progress}", (width // 2, height // 2), (0,0,0))
        screen.blit(cartridge_hardness_text, cartridge_hardness_text_rect)  # draw hardness text in the center



    if menu == -1: #draw loading bar
        if threading.active_count() == 1:  # check if the work thread is not already running
            threading.Thread(target=doWork).start()  # start the work in a separate thread
        screen.fill((0,0,0))          # clear screen (black background)
        screen.blit(mengen_bezig, mengen_bezig_rect)  # draw "mengen bezig" text in the center of the screen
        if loading_progress < 100:
            loading_bar_width = loading_progress*width/2//100
            loading_bar_image = pygame.transform.scale(loading_bar_image, (int(loading_bar_width), 50))  # scale loading bar based on progress
            loading_bar_image_rect = loading_bar_image.get_rect(midleft=(200, 3/4*height))  # update loading bar position
            screen.blit(loading_bar_image, loading_bar_image_rect)  # draw loading bar
        elif loading_progress >= 100:
            menu = 0
            location = 0
    pygame.display.flip()           # update display

    

pygame.quit()

