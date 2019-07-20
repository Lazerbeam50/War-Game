'''
Created on 13 Aug 2018

@author: Femi
'''
#Import pygame
import pygame
import os

#Load primary background function
def load_primary_background(name):
    fullname = os.path.join('Resources\Backgrounds\Primary', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error:
        print("Cannot load image:", fullname)
        input("Press enter to exit")
        raise Exception

    return image

#Load secondary background function
def load_secondary_background(name):
    fullname = os.path.join('Resources\Backgrounds\Secondary', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error:
        print("Cannot load image:", fullname)
        input("Press enter to exit")
        raise Exception

    return image

#Load secondary music function
def load_secondary_music(name):
    fullname = os.path.join('Resources\Music\Secondary', name)
    try:
        music = pygame.mixer.music.load(fullname)
    except pygame.error:
        print("Cannot load music:", fullname)
        input("Press enter to exit")
        raise Exception

#Load secondary sound function
def load_secondary_sound(name):
    fullname = os.path.join('Resources\Sounds\Secondary', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print("Cannot load sound:", fullname)
        input("Press enter to exit")
        raise Exception

    return sound

#Load primary sprite function
def load_primary_sprite(name):
    fullname = os.path.join('Resources\Sprites\Primary', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error:
        print("Cannot load image:", fullname)
        input("Press enter to exit")
        raise Exception
    return image

#Load secondary sprite function
def load_secondary_sprite(name):
    fullname = os.path.join('Resources\Sprites\Secondary', name)
    try:
        image = pygame.image.load(fullname).convert_alpha()
    except pygame.error:
        print("Cannot load image:", fullname)
        input("Press enter to exit")
        raise Exception
    return image

def load_text_file(name):
    a = os.path.dirname(__file__)
    filename = os.path.join(a, 'Resources\\Text\\', name)
    try:
        text = open(filename)
    except PermissionError:
        print("Cannot load text file:", filename, "Exception: PermissionError.")
        input("Press enter to exit")
        raise Exception
    except FileNotFoundError:
        print("Cannot load text file:", filename, "Exception: FileNotFoundError.")
        input("Press enter to exit")
        raise Exception
    return text