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

def create_text(text, position, color=(255,255,255)):
    surface_text = font.render(text, True, color)
    surface_text_rect = surface_text.get_rect()
    surface_text_rect.center = position
    return surface_text, surface_text_rect
work = 5000000
def doWork():
    global loading_progress
    for ii in range(work):
        loading_progress = int((ii / work) * 100)+1

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
width, height = screen.get_size()
pygame.display.set_caption('Dispenser Interface')
loci = [(100, height/2), (300, height/2), (500, height/2), (700, height/2), (750, height-50)]
menu = 0
location = 0

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
menu0_text, menu0_text_rect = create_text("START", (width // 2, 100), (0,0,0))
#Text menu 1
menu1_text, menu1_text_rect = create_text("2 component dispensing", (width // 2, 100), (0,0,0))
#Text menu 2
menu2_text, menu2_text_rect = create_text("4 component dispensing", (width //2, 100), (0,0,0))
#Text menu 3
menu3_text, menu3_text_rect = create_text("4 component dispensing", (width // 2, 100), (0,0,0))
#Text menu 4
menu4_text, menu4_text_rect = create_text("Would you like to start mixing?", (width // 2, 100), (0,0,0))
#Text menu 5
menu5_text, menu5_text_rect = create_text("Settings", (width // 2, 100), (0,0,0))
#Text menu 6
menu6_text, menu6_text_rect = create_text("Mixing Settings", (width // 2, 100), (0,0,0))
#Text menu 7
menu7_text, menu7_text_rect = create_text("Replace cartridge", (width // 2, 100), (0,0,0))



#load in selection sprite
selection_image, selection_image_rect = load_image(r'./Sprites/dispenser.png', (150, 150), loci[0])

#load in settings sprite
settings_image, settings_image_rect = load_image(r'./Sprites/settings.png', (100, 100), loci[3])

#load in return sprite
return_image, return_image_rect = load_image(r'./Sprites/return.png', (100, 100), loci[4])
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
button1_image, button1_image_rect = load_image(r'./Sprites/button.png', (100, 100), (loci[0]))
button2_image, button2_image_rect = load_image(r'./Sprites/button.png', (100, 100), (loci[1]))
button3_image, button3_image_rect = load_image(r'./Sprites/button.png', (100, 100), (loci[2]))
button4_image, button4_image_rect = load_image(r'./Sprites/button.png', (100, 100), (loci[3]))

#load yes and no sprite
yes_image, yes_image_rect = load_image(r'./Sprites/YES.png', (100, 100), (loci[1]))
no_image, no_image_rect = load_image(r'./Sprites/no.png', (100, 100), (loci[2]))



running = True
while running:
    selection_image_rect.center = (loci[location]) 
    screen.fill((255, 255, 255))          # clear screen (white background)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
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
                    if weight_progress > 50:
                        location  = 0
                        hardness_progress += 1
                    else:
                        hardness_progress = 0
                        location = 4
                elif menu == 4:
                    location = available_locations(location, "right", [1,2,4])
                elif menu == 5:  
                    location = available_locations(location, "right", [1,2,4])


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
                    if weight_progress > 0:
                        location  = 0
                        hardness_progress -= 1
                    else:
                        hardness_progress = 0
                        location = 4
                elif menu == 5:
                    location = available_locations(location, "left", [1,2,4])

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
                    if location == 4:
                        menu = 5
                elif menu == 7:
                    if location == 4:
                        menu = 5

                
    if menu == 0:
        screen.blit(menu0_text, menu0_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(settings_image, settings_image_rect)  # draw settings image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        screen.blit(button1_image, button1_image_rect)  # draw button 1
        screen.blit(button2_image, button2_image_rect)  # draw button 2
        screen.blit(button3_image, button3_image_rect)  # draw button 3
    if menu == 1:
        screen.blit(menu1_text, menu1_text_rect)  # draw menu text in the center of the screen
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
        if location == 4:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        weight_bar_width = abs(weight_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Desired weight: {weight_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center
    if menu == 2:
        screen.blit(menu2_text, menu2_text_rect)  # draw menu text in the center of the screen
        if location == 4:
            screen.blit(selection_image, selection_image_rect)  # draw cursor
        weight_bar_width = abs(weight_progress)*width/2//100
        weight_bar_image_use = pygame.transform.scale(weight_bar_image, (int(weight_bar_width), 50))  # scale loading bar based on selected weight
        weight_bar_image_use_rect = weight_bar_image_use.get_rect(midleft=(200, 3/4*height))  # update loading bar position
        screen.blit(weight_bar_image_use, weight_bar_image_use_rect)  # draw loading bar
        weight_text,weight_rect = create_text(f"Desired weight: {weight_progress} g", (width // 2, height // 2), (0,0,0))
        screen.blit(weight_text, weight_rect)  # draw weight text in the center
    if menu == 3:
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
    if menu == 4:
        screen.blit(menu4_text, menu4_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(yes_image, yes_image_rect)  # draw yes image
        screen.blit(no_image, no_image_rect)  # draw no image
    if menu == 5:
        screen.blit(menu5_text, menu5_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner    
    if menu == 6:
        screen.blit(menu6_text, menu6_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 7:
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw cursor
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == -1:
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

