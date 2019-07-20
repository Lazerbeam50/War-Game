'''
Created on 15 Aug 2018

@author: Femi
'''

import pygame
from pygame.locals import *

import sqlite3 #database script

import army # @UnresolvedImport
import battle # @UnresolvedImport
import battlefields  # @UnresolvedImport
import misc  # @UnresolvedImport
import resources  # @UnresolvedImport
import sprites  # @UnresolvedImport

class MissionSettings:
    def __init__(self):
        self.currentBattlefield = None
        self.player1Army = None
        self.player2Army = None
        self.pointCap = 20000 #1250
        self.turnDuration = 0
        self.turnTimeLimit = False

class ScreenManager:
    def __init__(self):
        self.armies = []
        self.battlefieldsList = []
        self.bgColour = None
        self.bgImage = None
        self.currentArmy = None
        self.gameSetup = False
        self.group = pygame.sprite.Group()
        self.missionsList = []
        self.missionSettings = MissionSettings()
        self.screenSetUp = False
        self.selectedPlayer = None
        self.state = 0 #0 = main menu, #1 = play menu, #2 = mission setup (missions tab), #3-5 = other mission tabs
        self.surface = pygame.Surface((1280, 720))
        self.tabGroup = pygame.sprite.Group()
        self.textGroup = pygame.sprite.Group()
        
    def update(self, values, event=None):
        
        if self.screenSetUp:
            if event != None:
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        clicked = False
                        for button in values.buttons[:]:
                            clicked = misc.is_point_inside_rect(pos[0], pos[1], button.rect)
                            if clicked:
                                if button.code == 0:
                                    values.settings.mode = 0
                                    self.state = 1
                                    self.screenSetUp = False
                                elif button.code == 5:
                                    raise Exception
                                
                                #Create game
                                elif button.code == 6:
                                    self.state = 2
                                    self.screenSetUp = False
                                    
                                #Army builder selected
                                elif button.code == 7:
                                    values.state = 1
                                    self.screenSetUp = False
                                    
                                elif button.code == 9:
                                    self.state = 0
                                    self.screenSetUp = False
                                elif button.code == 11:
                                    self.tabGroup.empty()
                                    self.textGroup.empty()
                                    for button in values.buttons[:]:
                                        if button.code >= 16:
                                            values.buttons.remove(button)
                                    self.set_up_battlefield_tab(values)
                                    
                                #Selecting Armies tab
                                elif button.code == 12:
                                    self.tabGroup.empty()
                                    self.textGroup.empty()
                                    for button in values.buttons[:]:
                                        if button.code >= 16:
                                            values.buttons.remove(button)
                                    self.set_up_armies_tab(values)
                                        
                                #Start game button
                                elif button.code == 14:
                                    """
                                    if (self.missionSettings.currentBattlefield != None and
                                        self.missionSettings.currentDeployment != None):
                                        values.state = 1
                                        self.state = 1
                                        self.tabGroup.empty()
                                        self.textGroup.empty()
                                        self.screenSetUp = False
                                        self.gameSetup = False
                                    else:
                                        print("Selections to be made!")
                                    """
                                    if (self.missionSettings.currentBattlefield != None and 
                                        self.missionSettings.player1Army != None and
                                        self.missionSettings.player2Army != None and
                                        self.missionSettings.pointCap != None):
                                        if ((self.missionSettings.player1Army.totalPoints 
                                             <= self.missionSettings.pointCap) and
                                            (self.missionSettings.player2Army.totalPoints 
                                             <= self.missionSettings.pointCap)):
                                            print("READY TO PLAY")
                                            #Reset game setup variables
                                            values.state = 2
                                            self.screenSetUp = False
                                            self.state = 1
                                            self.gameSetup = False
                                            self.currentArmy = None
                                            self.tabGroup.empty()
                                            self.textGroup.empty()
                                            
                                            #Create battle
                                            values.battle = battle.Battle(values, 
                                                                           [self.missionSettings.player1Army,
                                                                           self.missionSettings.player2Army],
                                            self.missionSettings.currentBattlefield.storage)
                                            
                                            self.missionSettings.currentBattlefield = None
                                            self.missionSettings.player1Army = None
                                            self.missionSettings.player2Army = None   
                                        else:
                                            print("Armies above point cap")
                                    else:
                                        print("Selections to be made!")
                                        
                                #Back out of game setup
                                elif button.code == 15:
                                    self.state = 1
                                    self.screenSetUp = False
                                    self.gameSetup = False
                                    self.currentArmy = None
                                    self.missionSettings.currentBattlefield = None
                                    self.missionSettings.player1Army = None
                                    self.missionSettings.player2Army = None
                                    self.tabGroup.empty()
                                    self.textGroup.empty()
                                    
                                #Select battlefield
                                elif button.code == 17:
                                    #Change previous selected battlefield's colour to white
                                    if self.missionSettings.currentBattlefield != None:
                                        image = values.font20.render(self.missionSettings.currentBattlefield.storage.name,
                                                                     True, values.colours["White"])
                                        self.missionSettings.currentBattlefield.sprites[1].image = image
                                    self.missionSettings.currentBattlefield = button
                                    image = values.font20.render(self.missionSettings.currentBattlefield.storage.name,
                                                                     True, values.colours["Lime"])
                                    self.missionSettings.currentBattlefield.sprites[1].image = image
                                    
                                    #Show battlefield info
                                    self.get_battlefield_tab_display(values)
                                    
                                #Select an army
                                elif button.code == 18:
                                    #Set army as current army
                                    if self.currentArmy != None:
                                        image = values.font20.render(self.currentArmy.storage.name, True, 
                                                                     values.colours["White"])
                                        self.currentArmy.sprites[1].image = image
                                    self.currentArmy = button
                                    image = values.font20.render(self.currentArmy.storage.name, True, 
                                                                     values.colours["Lime"])
                                    self.currentArmy.sprites[1].image = image
                                    
                                    #Assign army if there is a selected player
                                    if self.selectedPlayer == 1:
                                        self.missionSettings.player1Army = self.currentArmy.storage
                                    elif self.selectedPlayer == 2:
                                        self.missionSettings.player2Army = self.currentArmy.storage
                                    self.selectedPlayer = None
                                    for b in values.buttons:
                                        if b.code == 19:
                                            image = values.font20.render("Player 1", True, 
                                                                         values.colours["White"])
                                            b.sprites[1].image = image
                                        elif b.code == 20:
                                                image = values.font20.render("Player 2", True, 
                                                                             values.colours["White"])
                                                b.sprites[1].image = image
                                    
                                    #Display army info
                                    self.get_armies_tab_display(values)
                                    
                                #Select player 1 button
                                elif button.code == 19:
                                    #If player is already selected
                                    if self.selectedPlayer == 1:
                                        #Deselect player
                                        self.selectedPlayer = None
                                        #Turn highlight to white
                                        image = values.font20.render("Player 1", True, values.colours["White"])
                                        button.sprites[1].image = image
                                    #Else
                                    else:
                                        #Set selected player to 1
                                        self.selectedPlayer = 1
                                        #Highlight player text green
                                        image = values.font20.render("Player 1", True, values.colours["Lime"])
                                        button.sprites[1].image = image
                                        #Turn player 2 button white
                                        for b in values.buttons:
                                            if b.code == 20:
                                                image = values.font20.render("Player 2", True, 
                                                                             values.colours["White"])
                                                b.sprites[1].image = image
                                        
                                #Select player 2 button
                                elif button.code == 20:
                                    #If player is already selected
                                    if self.selectedPlayer == 2:
                                        #Deselect player
                                        self.selectedPlayer = None
                                        #Turn highlight to white
                                        image = values.font20.render("Player 2", True, values.colours["White"])
                                        button.sprites[1].image = image
                                    #Else
                                    else:
                                        #Set selected player to 2
                                        self.selectedPlayer = 2
                                        #Highlight player text green
                                        image = values.font20.render("Player 2", True, values.colours["Lime"])
                                        button.sprites[1].image = image
                                        #Turn player 2 button white
                                        for b in values.buttons:
                                            if b.code == 19:
                                                image = values.font20.render("Player 1", True, 
                                                                             values.colours["White"])
                                                b.sprites[1].image = image
                                    
                                break          
        
        else:
        
            self.group.empty()
            values.buttons = []
            self.bgColour = None
            self.bgImage = None
            
            if self.state == 0:
                self.get_main_menu(values)
                
            elif self.state == 1:
                self.get_play_menu(values)
                
            elif self.state == 2:
                if not self.gameSetup:
                    self.get_game_setup_menu(values)
                    self.gameSetup = True
                self.set_up_battlefield_tab(values)
                
            self.screenSetUp = True
        
    def get_main_menu(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        image = values.font90.render("Wargame", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (400, 100))
        x = sprites.centre_x(400, values.settings.width, 0)
        
        button = sprites.Button(0, 0, image, (x, 200, 400, 100), "Same PC Mode", values.font60, values)
        button = sprites.Button(1, 0, image, (x, 325, 400, 100), "Server Mode", values.font60, values)
        button = sprites.Button(2, 0, image, (x, 450, 400, 100), "Direct Link Mode", values.font60, values)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (300, 50))
        x = sprites.centre_x(300, values.settings.width, 0)
        
        button = sprites.Button(5, 0, image, (x, 600, 300, 50), "Quit Game", values.font30, values)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def get_play_menu(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        image = values.font90.render("Wargame", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (400, 100))
        x = sprites.centre_x(400, values.settings.width, 0)
        
        button = sprites.Button(6, 0, image, (x, 200, 400, 100), "Create Game", values.font60, values)
        button = sprites.Button(7, 0, image, (x, 325, 400, 100), "Army Builder", values.font60, values)
        button = sprites.Button(8, 0, image, (x, 450, 400, 100), "Unused Button", values.font60, values)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (300, 50))
        x = sprites.centre_x(300, values.settings.width, 0)
        
        button = sprites.Button(9, 0, image, (x, 600, 300, 50), "Back", values.font30, values)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def get_game_setup_menu(self, values):
        
        #self.missionsList = missions.get_open_play_missions()
        self.battlefieldsList = battlefields.get_battlefields()
        
        self.bgColour = values.colours["Beige"]
        
        longPanelImage = resources.load_secondary_sprite("long_panel01.png")
        
        panel01Image = pygame.transform.scale(longPanelImage, (270, 595))
        panel02Image = pygame.transform.scale(longPanelImage, (860, 595))
        
        sprList = [
            sprites.GameSprite(panel01Image, (50, 75, 270, 595)),
            sprites.GameSprite(panel02Image, (370, 75, 860, 595)),
            ]
        
        self.group.add(sprList)
        
        buttonImage = resources.load_secondary_sprite("button01.png")
        buttonImage01 = pygame.transform.scale(buttonImage, (150, 50))
        
        button = sprites.Button(11, 0, buttonImage01, (225, 0, 150, 50), "Battlefields", values.font20, values)
        button = sprites.Button(12, 0, buttonImage01, (400, 0, 150, 50), "Armies", values.font20, values)
        button = sprites.Button(13, 0, buttonImage01, (575, 0, 150, 50), "Game Settings", values.font20, values)
        button = sprites.Button(14, 0, buttonImage01, (750, 0, 150, 50), "Start Game", values.font20, values)
        button = sprites.Button(15, 0, buttonImage01, (925, 0, 150, 50), "Back", values.font20, values)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def get_armies_tab_display(self, values):
        
        self.textGroup.empty()
        army1 = self.currentArmy.storage
        spr = []
        # Display info for selected army
        self.print_army_info(values, spr, army1, 450, 100)

        # If Player 1 has an army, display key info
        if self.missionSettings.player1Army != None:
            army1 = self.missionSettings.player1Army
            self.print_army_info(values, spr, army1, 900, 130)
        
        # Do same for player 2
        if self.missionSettings.player2Army != None:
            army1 = self.missionSettings.player2Army
            self.print_army_info(values, spr, army1, 900, 430)
            
        self.textGroup.add(spr)
            
    def get_battlefield_tab_display(self, values):
        
        self.textGroup.empty()
        b = self.missionSettings.currentBattlefield.storage
        spr = []
        
        text = b.name + " (" + str(b.size[0]) + "x" + str(b.size[1]) + ")"
        image = values.font30.render(text, True, values.colours["White"])
        x = sprites.centre_x(image.get_width(), 860, 370)
        y = 95
        spr.append(sprites.GameSprite(image, (x, y, image.get_width(), image.get_height())))
        y += 40
        
        width = int(10 * (72/b.size[0]))
        
        blocks = {"Aqua": pygame.Surface((width, 10)), "Dark Green": pygame.Surface((width, 10)), 
                  "Forest Green": pygame.Surface((width, 10)), "Dark Olive Green": pygame.Surface((width, 10)),
                  "Green": pygame.Surface((width, 10)), "Sea Green": pygame.Surface((width, 10)),
                  "Slate Grey": pygame.Surface((width, 10))}
        
        for block in blocks:
            blocks[block].fill(values.colours[block])
            
        x = sprites.centre_x(720, 860, 370)
        
        for line in b.map:
            for node in line[0]:
                if node == "*" and b.tileset == 0:
                    image = blocks["Green"]
                elif node == "*" and b.tileset == 1:
                    image = blocks["Forest Green"]
                elif node == "T":
                    image = blocks["Dark Green"]
                elif node == "t":
                    image = blocks["Dark Olive Green"]
                elif node == "m":
                    image = blocks["Sea Green"]
                elif node == "r":
                    image = blocks["Slate Grey"]
                elif node == "w":
                    image = blocks["Aqua"]
                spr.append(sprites.GameSprite(image, (x, y, width, 10)))
                x += width
            x = sprites.centre_x(720, 860, 370)
            y += 10
        
        self.textGroup.add(spr)
        
    def set_up_armies_tab(self, values):
        
        widePanelImage = resources.load_secondary_sprite("wide_panel01.png")
        buttonImage = pygame.transform.scale(widePanelImage, (255, 25))
        x = sprites.centre_x(255, 270, 50)
        y = 85
        
        #load armies from save data
        db = sqlite3.connect('Save Data/save data') #connect to database
        cursor = db.cursor()
        
        cursor.execute('''SELECT name, bossTrait, faction, totalSP, totalPoints, detachments FROM armies''')
        data = cursor.fetchall()
        self.armies = army.get_army_lists(data)
        
        #Set up buttons for list
        for a in self.armies:
            button = sprites.Button(18, 0, buttonImage, (x, y, 255, 25), a.name, values.font20, values, storage=a)
            y += 25
            self.tabGroup.add(button.sprites)
            
        #Set up player army buttons
        button = sprites.Button(19, 0, buttonImage, (850, 100, 255, 25), "Player 1", values.font20, values)
        self.tabGroup.add(button.sprites)
        button = sprites.Button(20, 0, buttonImage, (850, 400, 255, 25), "Player 2", values.font20, values)
        self.tabGroup.add(button.sprites)
        
        #display current army setup
        if self.missionSettings.player1Army != None or self.missionSettings.player2Army != None:
            self.get_armies_tab_display(values)

    def set_up_battlefield_tab(self, values):
        
        widePanelImage = resources.load_secondary_sprite("wide_panel01.png")
        buttonImage = pygame.transform.scale(widePanelImage, (255, 25))
        x = sprites.centre_x(255, 270, 50)
        y = 85
        
        for b in self.battlefieldsList:
            if self.missionSettings.currentBattlefield != None:
                if b == self.missionSettings.currentBattlefield.storage:
                    button = sprites.Button(17, 0, buttonImage, (x, y, 255, 25), b.name, values.font20, values, colour=values.colours["Lime"], storage=b)
                    self.missionSettings.currentBattlefield = button
                else:
                    button = sprites.Button(17, 0, buttonImage, (x, y, 255, 25), b.name, values.font20, values, storage=b)
            else:
                button = sprites.Button(17, 0, buttonImage, (x, y, 255, 25), b.name, values.font20, values, storage=b)
            y += 25
            self.tabGroup.add(button.sprites)
            
        if self.missionSettings.currentBattlefield != None:
            self.get_battlefield_tab_display(values)
            
    def print_army_info(self, values, spr, army1, x, y):
        
        factions = ["Paladins", "Orcs", "Sorcerers", "Earthlings", "Valkyries", "Titans", "Elves", "Undead",
                    "Hobgoblins", "The Kraaw", "Demonic Legion"]
        armyFaction = "Faction :  " + factions[army1.faction]
        bossName = "Boss : " + army1.codex.units[army1.boss.data].title
        
        # Name, Faction, Points, Boss, SP, No. of detachments
        info = [army1.name, " ", armyFaction, "Points : " + str(army1.totalPoints), bossName, 
                "Total SP : " + str(army1.totalSP), "No. of Detachments : " + str(len(army1.detachments))]
        
        for text in info:
            image = values.font30.render(text, True, values.colours["White"])
            spr.append(sprites.GameSprite(image, (x, y, image.get_width(), image.get_height())))
            y += 20
        
        