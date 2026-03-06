#python -m venv dispenser_venv
#dispenser_venv\Scripts\activate

import pygame
from pygame.locals import *
import time


def load_image(path, size, location):
    image = pygame.image.load(path)
    image.convert_alpha()
    image = pygame.transform.scale(image, size)
    image_rect = image.get_rect()
    print(image_rect)
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

pygame.init()
size = (width, height)= (800, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Dispenser Interface')
loci = [(250, height/2), (350, height/2), (450, height/2), (550, height/2), (750, height-50)]
menu = 0
location = 0



#Maak teks voor tijdens mengen
mengen_bezig, mengen_bezig_rect = create_text("Aan het mengen", (width // 2, height // 2), (255,255,255))
#Text menu 0
menu0_text, menu0_text_rect = create_text("START", (width // 2, 100), (255,255,255))
#Text menu 1
menu1_text, menu1_text_rect = create_text("2 component dispensing", (width // 2, 100), (255,255,255))
#Text menu 2
menu2_text, menu2_text_rect = create_text("4 component dispensing", (width //2, 100))
#Text menu 3
menu3_text, menu3_text_rect = create_text("4 component dispensing", (width // 2, 100), (255,255,255))
#Text menu 4
menu4_text, menu4_text_rect = create_text("Mixing", (width // 2, 100), (255,255,255))
#Text menu 5
menu5_text, menu5_text_rect = create_text("Settings", (width // 2, 100), (255,255,255))
#Text menu 6
menu6_text, menu6_text_rect = create_text("Mixing Settings", (width // 2, 100), (255,255,255))
#Text menu 7
menu7_text, menu7_text_rect = create_text("Replace cartridge", (width // 2, 100), (255,255,255))



#load in selection sprite
selection_image, selection_image_rect = load_image(r'./Sprites/dispenser.png', (150, 150), loci[0])

#load in settings sprite
settings_image, settings_image_rect = load_image(r'./Sprites/settings.png', (100, 100), loci[3])

#load in return sprite
return_image, return_image_rect = load_image(r'./Sprites/return.png', (100, 100), loci[4])


running = True

while running:
    selection_image_rect.center = (loci[location]) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT: #changing location
                location += 1
                
                if location == 5:
                    location = 0
                if menu == 5:  
                    if location == 0:
                        location = 1
                    if location == 3:
                        location = 4

            elif event.key == pygame.K_LEFT:
                location -= 1
                
                if location == -1:
                    location = 4
                if menu == 5:  
                    if location == 0:
                        location = 4
                    if location == 3:
                        location = 2

            elif event.key == pygame.K_RETURN: #state machine for menu navigation
                if menu == 0:
                    if location == 0:
                        menu = 1
                    elif location == 1:
                        menu = 2
                    elif location == 2:
                        menu = 4
                    elif location == 3:
                        menu = 5
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
                    if location == 4:
                        menu = 0
                    else:
                        menu = -1
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
        screen.fill((255, 255, 255))          # clear screen (white background)
        screen.blit(menu0_text, menu0_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(settings_image, settings_image_rect)  # draw settings image in top right corner
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 1:
        screen.fill((255, 0, 0))          # clear screen (red background)
        screen.blit(menu1_text, menu1_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 2:
        screen.fill((0, 255, 0))          # clear screen (green background)
        screen.blit(menu2_text, menu2_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 3:
        screen.fill((0, 0, 255))          # clear screen (blue background)
        screen.blit(menu3_text, menu3_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 4:
        screen.fill((255, 255, 0))          # clear screen (yellow background)
        screen.blit(menu4_text, menu4_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 5:
        screen.fill((255, 0, 255))          # clear screen (magenta background)
        screen.blit(menu5_text, menu5_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner    
    if menu == 6:
        screen.fill((0, 255, 255))          # clear screen (cyan background)
        screen.blit(menu6_text, menu6_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == 7:
        screen.fill((128, 128, 128))          # clear screen (gray background)
        screen.blit(menu7_text, menu7_text_rect)  # draw menu text in the center of the screen
        screen.blit(selection_image, selection_image_rect)  # draw image
        screen.blit(return_image, return_image_rect)  # draw return image in bottom right corner
    if menu == -1:
        screen.fill((0, 0, 0))          # clear screen (black background)
        screen.blit(mengen_bezig, mengen_bezig_rect)  # draw "mengen bezig" text in the center of the screen

    pygame.display.flip()           # update display
    if menu == -1:
        time.sleep(1)
        menu = 0

    

pygame.quit()

