'''
Created on 13 Aug 2018

@author: Femi
'''
import pygame
from pygame.locals import *

class Button():
    def __init__(self, code, use, image, rect, text, font, values, layer=3, colour=(255, 255, 255), storage=None):
        #For battle uses, code = key and use = action
        self.code = code
        self.use = use #use (0 = menu screens, 1 = army screens)
        """
        self.faction = faction
        self.battlefield = battlefield
        self.deployment = deployment
        """
        self.storage = storage
        sprite1 = GameSprite(image, (rect), layer=layer)
        self.rect = pygame.Rect(rect)
        image2 = font.render(text, True, colour)
        size = image2.get_size()
        x = centre_x(size[0], rect[2], rect[0])
        y = centre_y(size[1], rect[3], rect[1])
        sprite2 = GameSprite(image2, (x, y, size[0], size[1]), layer=layer + 1)
        self.sprites = [sprite1, sprite2]
        values.buttons.append(self)

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, rect, layer=1):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = Rect(rect)
        self._layer = layer
        
def centre_x(objectWidth, fitWidth, fitLeft):
    x = int((fitWidth - objectWidth)/2 + fitLeft)
    
    return x

def centre_y(objectHeight, fitHeight, fitTop):
    y = int((fitHeight - objectHeight)/2 + fitTop)
    
    return y

def get_translucent_sprite(image):
    for row in range(image.get_height()):
        for col in range(image.get_width()):
            image.set_at((row, col), set_alphas(image.get_at((row, col))[:3]))
            
    return image
            
def set_alphas(colour):
    pixel = (colour[0], colour[1], colour[2], 128)
    
    return pixel

def update_typed_text(values, textInput, button):
    
    text = textInput.font.render(textInput.value, True, textInput.color)
    button.sprites[1].image = text
    button.sprites[1].rect.x = centre_x(text.get_width(), button.sprites[0].rect.width, 
                                   button.sprites[0].rect.left)