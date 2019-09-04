'''
Created on 13 Aug 2018

@author: Femi
'''
import pygame
from pygame.locals import *

from twisted.internet import reactor #needed for shutting down the game

from sys import exc_info #needed for error reporting
import sqlite3 #database script
import traceback #needed for error reporting

import army # @UnresolvedImport
import codex # @UnresolvedImport
import misc  # @UnresolvedImport
import screenmanager  # @UnresolvedImport

class Game:
    def __init__(self):
        
        pygame.init() #initiate pygame
        
        #create error variables and set up values and settings
        self.errorRaised = False
        self.reactorStarted = False
        self.values = misc.ValueHolder()
        self.values.settings = misc.GameSettings()
        self.values.armyManager = army.ArmyManager()
        self.values.screenManager = screenmanager.ScreenManager()
        
        #Set up screen
        self.screen = pygame.display.set_mode((self.values.settings.width, self.values.settings.height))
        pygame.display.set_caption('Wargame')
        
        #Set up fonts
        self.values.font20 = pygame.font.Font("Resources/Fonts/NotoSans-Regular.ttf", 10)
        self.values.font30 = pygame.font.Font("Resources/Fonts/NotoSans-Regular.ttf", 20)
        self.values.font60 = pygame.font.Font("Resources\Fonts\Plakette-Serial-Bold.ttf", 60)
        self.values.font90 = pygame.font.Font("Resources\Fonts\Plakette-Serial-Bold.ttf", 90)
        
        #Grab factions from database
        db = sqlite3.connect('Game Data/game database') #connect to database
        cursor = db.cursor()
        
        cursor.execute('''SELECT id, name, description FROM factions''')
        data = cursor.fetchall()
        self.values.factions = []
        
        for entry in data:
            obj = codex.Faction()
            obj.ID = entry[0]
            obj.name = entry[1]
            obj.description = entry[2]
            self.values.factions.append(obj)
        
        self.values.screenManager.update(self.values)
        
    def main_loop(self):
        
        try:
        
            events = pygame.event.get()
            
            for event in events:
                if event.type == QUIT:
                    self.quit_game()
                    
                elif self.values.state == 0:
                    self.values.screenManager.update(self.values, event)  
                    
                elif self.values.state == 1:
                    
                    a = None
                    
                    if self.values.armyManager.typing:
                        a = self.values.armyManager.textInput.update(events)
                    
                    self.values.armyManager.update(self.values, event, a)
                    
                elif self.values.state == 2:
                    self.values.battle.update(self.values, event)          
                    
            if self.values.state == 0:
                
                if not self.values.screenManager.screenSetUp:
                    self.values.screenManager.update(self.values)
                
                if self.values.screenManager.bgImage == None:
                    self.values.screenManager.surface.fill((self.values.screenManager.bgColour))
                else:
                    self.values.screenManager.surface.blit(self.values.screenManager.surface.bgImage, (0, 0))
                    
                self.values.screenManager.group.draw(self.values.screenManager.surface)
                self.values.screenManager.tabGroup.draw(self.values.screenManager.surface)
                self.values.screenManager.textGroup.draw(self.values.screenManager.surface)
            
                self.screen.blit(self.values.screenManager.surface, (0, 0))
                
            elif self.values.state == 1:
                self.values.armyManager.update(self.values)
                if self.values.armyManager.bgImage == None:
                    self.values.armyManager.surface.fill((self.values.armyManager.bgColour))
                else:
                    self.values.armyManager.surface.blit(self.values.armyManager.bgImage, (0, 0))
                    
                self.values.armyManager.group.draw(self.values.armyManager.surface)
                #self.values.armyManager.tabGroup.draw(self.values.armyManager.surface)
                self.values.armyManager.textGroup.draw(self.values.armyManager.surface)
            
                self.screen.blit(self.values.armyManager.camera, (0, 0))
                
            elif self.values.state == 2:
                self.values.battle.update(self.values)
                
                self.values.battle.surface.fill(self.values.colours["Black"])
                
                self.values.battle.backgroundGroup.draw(self.values.battle.surface)
                self.values.battle.terrainGroup.draw(self.values.battle.surface)
                self.values.battle.highlightGroup.draw(self.values.battle.surface)
                if (not self.values.battle.leftPressed and not self.values.battle.rightPressed and
                    not self.values.battle.upPressed and not self.values.battle.downPressed):
                    self.values.battle.squaresGroup.draw(self.values.battle.surface)
                self.values.battle.controlPointGroup.draw(self.values.battle.surface)
                self.values.battle.modelsGroup.draw(self.values.battle.surface)
                self.values.battle.flagsGroup.draw(self.values.battle.surface)
                
                self.screen.blit(self.values.battle.camera, (0, 0))
                
                if not self.values.battle.hideUI:
                    
                    #Blit images to local surfaces
                    self.values.battle.headerSurface.blit(self.values.battle.headerImage, (0, 0))
                    self.values.battle.leftPanelSurface.blit(self.values.battle.leftPanelImage, (0, 0))
                    self.values.battle.rightPanelSurface.blit(self.values.battle.rightPanelImage, (0, 0))
                    self.values.battle.chatLogSurface.blit(self.values.battle.chatLogImage, (0, 0))
                    self.values.battle.eventLogSurface.blit(self.values.battle.eventLogImage, (0, 0))
                    self.values.battle.commandListSurface.blit(self.values.battle.commandListImage, (0, 0))
                    
                    #Draw sprites
                    self.values.battle.headerGroup.draw(self.values.battle.headerSurface)
                    self.values.battle.leftPanelGroup.draw(self.values.battle.leftPanelSurface)
                    self.values.battle.rightPanelGroup.draw(self.values.battle.rightPanelSurface)
                    self.values.battle.chatLogGroup.draw(self.values.battle.chatLogSurface)
                    self.values.battle.eventLogGroup.draw(self.values.battle.eventLogSurface)
                    self.values.battle.commandListGroup.draw(self.values.battle.commandListSurface)
                    
                    #Blit images to screen
                    self.screen.blit(self.values.battle.headerSurface, (0, 0))
                    self.screen.blit(self.values.battle.leftPanelSurface, (0, 32))
                    self.screen.blit(self.values.battle.rightPanelSurface, (1120, 32))
                    self.screen.blit(self.values.battle.blackLine1, (0, 512))
                    self.screen.blit(self.values.battle.chatLogSurface, (0, 520))
                    self.screen.blit(self.values.battle.blackLine2, (420, 520))
                    self.screen.blit(self.values.battle.eventLogSurface, (430, 520))
                    self.screen.blit(self.values.battle.blackLine3, (850, 520))
                    self.screen.blit(self.values.battle.commandListSurface, (860, 520))
            
            pygame.display.update()
                    
        except Exception:
            tb = exc_info() #return error information
            print("Error found in main loop")
            print()
            print("Error type:", tb[0])
            print("Error value:", tb[1])
            l = traceback.format_tb(tb[2])
            for line in l:
                print(line)
            self.errorRaised = True
            if self.reactorStarted:
                self.quit_game() #if reactor has already started, shut down the game
            
    def quit_game(self):
        pygame.quit()
        reactor.stop()