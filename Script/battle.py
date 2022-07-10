'''
Created on 28 Mar 2019
@author: Femi
'''

import pygame
from pygame.locals import *

import copy
import math
import operator
import random
import time

import misc # @UnresolvedImport
import resources # @UnresolvedImport
import sprites # @UnresolvedImport

class Attack:
    def __init__(self, toHit, strength, damage, ap, primaryTarget, otherTargets, effects=[]):
        self.toHit = toHit
        self.strength = strength
        self.damage = damage
        self.ap = ap
        self.primaryTarget = primaryTarget
        self.otherTargets = otherTargets
        self.effects = effects

class Battle:
    def __init__(self, values, playerArmies, battlefield, playerNames = ["Player 1", "Player 2"]):
        #Used to keep track of the first play who finished deploying
        self.announcedFirstToFinish = False
        self.attackingModels = [] #Shows who can shoot/attack
        self.awaitingEvent = False
        self.backgroundGroup = pygame.sprite.Group()
        self.blackLine1 = pygame.Surface((1280, 8))
        self.blackLine2 = pygame.Surface((10, 200))
        self.blackLine3 = pygame.Surface((10, 200))
        self.camera = None
        #used so that the game knows how far down a list to display in terms of Commands (e.g. deployment)
        self.commandListCounter = 0
        #420 x 200, at location 860, 520
        self.commandListGroup = pygame.sprite.Group()
        self.commandListImage = resources.load_primary_background("battle_ui_bottom_panel.png")
        self.commandListMaxed = False
        self.commandListSurface = pygame.Surface((420, 200))
        #determines the first string shown in the chat log. Is increased or decreased by scrolling
        self.chatLogCounter = 0
        #420 x 200, at location 0, 520)
        self.chatLogGroup = pygame.sprite.Group()
        self.chatLogImage = resources.load_primary_background("battle_ui_bottom_panel.png")
        self.chatLogSurface = pygame.Surface((420, 200))
        self.chatLogText = []
        self.checkingExplosions = False
        self.controlPointGroup = pygame.sprite.Group()
        self.controlPoints = [] #List of control point co-ordinates. Replace with tuple.
        #marks the status of an objective marker (0 = neutral, 1 = player1, 2 = player2, 3 = contested)
        self.controlPointStatus = [0, 0, 0, 0, 0, 0]
        self.currentModel = None
        self.currentNode = None #Used to track clicking
        self.currentSpell = None
        self.currentTransport = None
        self.currentTurn = None
        self.currentTurnSaved = None #Used to keep track of who's turn it actually is during melee
        self.currentUnit = None
        self.currentWeapon = None
        self.deploymentMap = battlefield.deploymentMap
        self.disembarkNodes = [] #Used when disembarking from a transport
        #determines the first string shown in the event log. Is increased or decreased by scrolling
        self.eventLogCounter = 0
        #420 x 200, at location 430, 520
        self.eventLogGroup = pygame.sprite.Group()
        self.eventLogImage = resources.load_primary_background("battle_ui_bottom_panel.png")
        self.eventLogSurface = pygame.Surface((420, 200))
        self.eventLogText = []
        self.firstBloodAwarded = False
        self.flagsGroup = pygame.sprite.Group()
        self.headerGroup = pygame.sprite.Group()
        self.headerImage = resources.load_primary_background("battle_ui_header.png")
        self.headerSurface = pygame.Surface((1280, 32))
        self.hideUI = False
        self.highlightGroup = pygame.sprite.Group()
        self.highlighting = False
        #Determines the type of information displayed on the side panels
        self.infoType = 0 #0 = units, 1 = terrain, 2 = models, 3 = transport passengers
        #150 x 450, at location 0, 60
        self.leftPanelGroup = pygame.sprite.Group()
        self.leftPanelImage = resources.load_primary_background("battle_ui_side_panel.png")
        self.leftPanelSurface = pygame.Surface((160, 480))
        self.logButtons = []
        self.mainMessage = None
        self.meleePriority = None #Used to track the current priority level
        self.modelCount = 0
        self.models = {}
        self.modelsGroup = pygame.sprite.Group()
        #co-ordinates as key, Node object as value
        self.nodes = {}
        self.otherTurn = None
        self.otherTurnSaved = None #Used to keep track of who's turn it actually is during melee
        self.otherUnit = None
        self.pileIn = True #Used to differentiate between a pile in an a consolidate
        #0 = deploy, 1 = move, 2 = magic, 3 shoot, 4 = charge, 5 = melee, 6 = morale
        self.phase = 0
        #150 x 450, at location 1130, 60
        self.randomNumbers = []
        self.rightPanelGroup = pygame.sprite.Group()
        self.rightPanelImage = resources.load_primary_background("battle_ui_side_panel.png")
        self.rightPanelSurface = pygame.Surface((160, 480))
        self.selectedModels = []
        self.showInfo = True
        self.squaresGroup = pygame.sprite.Group()
        self.state = 0
        #Node co-ordinates. Used to move models as a group
        self.targetNode = None
        self.targetedNodes = [] #Used to display targets of attacks
        self.turn = [0, 0] #first int is player 1 turn, 2nd is player 2
        self.terrainGroup = pygame.sprite.Group()
        self.surface = None
        self.unitCount = 0
        self.units = {}
        self.unitsForMelee = [[], [], [], [], [], []]
        #list of tuples. Contains Ids of units still in need of deployment
        self.unitsToDeploy = []
        self.xOffset = 0 #Minimum of 0
        self.xOffsetMax = 0
        self.yOffset = 0 #Minimum of 0
        self.yOffsetMax = 0 
        
        #Track pygame key pushes
        self.upPressed = False
        self.downPressed = False
        self.leftPressed = False
        self.rightPressed = False
        
        self.ctrlPressed = False
        self.altPressed = False
        self.cPressed = False
        
        #These variables are used for out of bounds testing
        self.lowestX = 9999
        self.highestX = 0
        self.lowestY = 9999
        self.highestY = 0
        
        #Movement type trackers
        self.moveFormation = False
        self.moveToPoint = False
        self.moveModels = False
        
        #Set up log buttons
        upArrow = resources.load_primary_sprite('log_up_arrow.png')
        self.logButtons.append(LogButton(0, upArrow, (400, 0, 20, 100)))
        downArrow = resources.load_primary_sprite('log_down_arrow.png')
        self.logButtons.append(LogButton(1, downArrow, (400, 100, 20, 100)))
        
        for button in self.logButtons:
            if button.use in range(0, 2):
                self.eventLogGroup.add(button.sprite)
        
        self.players = []
        i = 0
        colours = (values.colours["Red"], values.colours["Dark Blue"])
        #Set up player objects
        for a in playerArmies:
            self.players.append(Player(playerNames[i], a, colours[i]))
            i += 1
            
        #===Set up battlefield===
        
        #Set up surface and camera
        width = (battlefield.size[0] * 32) + 320
        height = (battlefield.size[1] * 32) + 240
        self.xOffsetMax = width - 1280
        self.yOffsetMax = height - 720
        self.surface = pygame.Surface((width, height))
        self.camera = self.surface.subsurface(self.xOffset, self.yOffset, 1280, 720)
        
        #Set up tiles
        images = {}
        x = 0 #150
        y = 0 #50
        
        for line in battlefield.map:
            
            for char in line[0]:
                
                node = Node()
                img = []
                
                if battlefield.tileset == 0:
                    
                    if char == "*":
                        
                        node.terrain = "Grass"
                        
                        if "dense_forest_standard_ground_tile.png" not in images:
                            images["dense_forest_standard_ground_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_standard_ground_tile.png")
                        img.append(images["dense_forest_standard_ground_tile.png"])
                        
                    elif char == "r":
                        
                        node.terrain = "Rock"
                        
                        if "dense_forest_standard_ground_tile.png" not in images:
                            images["dense_forest_standard_ground_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_standard_ground_tile.png")
                        img.append(images["dense_forest_standard_ground_tile.png"])
                        
                        if "dense_forest_rock_tile.png" not in images:
                            images["dense_forest_rock_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_rock_tile.png")
                        img.append(images["dense_forest_rock_tile.png"])
                        
                    elif char == "t":
                        
                        node.terrain = "Small tree"
                        node.cover = 1
                        
                        if "dense_forest_standard_ground_tile.png" not in images:
                            images["dense_forest_standard_ground_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_standard_ground_tile.png")
                        img.append(images["dense_forest_standard_ground_tile.png"])
                        
                        if "tree_tile.png" not in images:
                            images["tree_tile.png"] = resources.load_primary_sprite("tree_tile.png")
                        img.append(images["tree_tile.png"])
                        
                    elif char == "T":
                        
                        node.terrain = "Large tree"
                        node.cover = 2
                        
                        if "dense_forest_standard_ground_tile.png" not in images:
                            images["dense_forest_standard_ground_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_standard_ground_tile.png")
                        img.append(images["dense_forest_standard_ground_tile.png"])
                        
                        if "tree_tile2.png" not in images:
                            images["tree_tile2.png"] = resources.load_primary_sprite("tree_tile2.png")
                        img.append(images["tree_tile2.png"])
                        
                    elif char == "m":
                        
                        node.terrain = "Large mossy rock"
                        node.blocksLOS = True
                        node.walkable = False
                        
                        if "dense_forest_standard_ground_tile.png" not in images:
                            images["dense_forest_standard_ground_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_standard_ground_tile.png")
                        img.append(images["dense_forest_standard_ground_tile.png"])
                        
                        if "dense_forest_mossy_rock_tile.png" not in images:
                            images["dense_forest_mossy_rock_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_mossy_rock_tile.png")
                        img.append(images["dense_forest_mossy_rock_tile.png"])
                        
                    elif char == "w":
                        
                        node.terrain = "Water"
                        node.walkable = False
                        
                        if "dense_forest_water_tile.png" not in images:
                            images["dense_forest_water_tile.png"] = resources.load_primary_sprite(
                                "dense_forest_water_tile.png")
                        img.append(images["dense_forest_water_tile.png"])
                        
                node.coordinates = (x, y)
                node.backSprite = sprites.GameSprite(img[0], ((x * 32) + 160, (y * 32) + 32, 32, 32))
                self.backgroundGroup.add(node.backSprite)
                
                self.lowestX = min(self.lowestX, node.backSprite.rect.x)
                self.highestX = max(self.highestX, node.backSprite.rect.x + 32)
                self.lowestY = min(self.lowestY, node.backSprite.rect.y)
                self.highestY = max(self.highestY, node.backSprite.rect.y + 32)
                
                if len(img) > 1:
                    node.foreSprite = sprites.GameSprite(img[1], ((x * 32) + 160, (y * 32) + 32, 32, 32))
                    self.terrainGroup.add(node.foreSprite)
                node.x = x
                node.y = y
                
                self.nodes[(x, y)] = node
                
                #See if the node is a control point
                #If so, set up sprite and control point to ordered list
                n = 0 #Used to put the control points in order later
                if (x, y) == battlefield.objective1:
                    image = resources.load_primary_sprite("control_point_1_marker.png")
                    n = 1
                elif (x, y) == battlefield.objective2:
                    image = resources.load_primary_sprite("control_point_2_marker.png")
                    n = 2
                elif (x, y) == battlefield.objective3:
                    image = resources.load_primary_sprite("control_point_3_marker.png")
                    n = 3
                elif (x, y) == battlefield.objective4:
                    image = resources.load_primary_sprite("control_point_4_marker.png")
                    n = 4
                elif (x, y) == battlefield.objective5:
                    image = resources.load_primary_sprite("control_point_5_marker.png")
                    n = 5
                elif (x, y) == battlefield.objective6:
                    image = resources.load_primary_sprite("control_point_6_marker.png")
                    n = 6
                if n > 0:
                    self.controlPointGroup.add(sprites.GameSprite(image, ((x * 32) + 160, (y * 32) + 32, 32, 32)))
                    self.controlPoints.append((x, y, n))
                
                x += 1
                
            x = 0
            y += 1
            
        #order control point list
        a = []
        for i in range(1, 7):
            for j in self.controlPoints:
                if j[2] == i:
                    a.append((j[0], j[1]))
                    break
                
        self.controlPoints = tuple(a)
        
        #Set up unit and model IDs
        playerID = 1
        names = {} #unit tile string as key, count of that unit as value
        
        #If the two players are using the same army object, create a new copy for player 2
        if self.players[0].playerArmy == self.players[1].playerArmy:
            self.players[1].playerArmy = copy.deepcopy(self.players[0].playerArmy)

        for player in self.players:
            for detachment in player.playerArmy.detachments:
                for unit in detachment.units:
                        
                    
                    self.units[(playerID, self.unitCount)] = unit
                    unit.ID = (playerID, self.unitCount)
                    player.units.append((playerID, self.unitCount))
                    self.unitCount += 1
                    
                    #Name unit
                    title = player.playerArmy.codex.units[unit.data].title
                    if title not in names:
                        names[title] = 1
                    unit.name = title + " #" + str(names[title])
                    names[title] += 1
                    
                    #Set up list of deployment units
                    self.unitsToDeploy.append(unit.ID)
                    
                    for model in unit.models:
                        model.unitID = unit.ID
                        self.models[(playerID, self.modelCount)] = model
                        model.ID = (playerID, self.modelCount)
                        player.models.append((playerID, self.modelCount))
                        self.modelCount += 1
                        
            playerID += 1
            
        self.update_event_log(values, "Game start")
            
        #Set up header display
        self.set_up_header_display(values)
        
        #Set up deployment
        self.randomNumbers = self.get_random_numbers()
        
        #Assign deployment zones
        n = self.randomNumbers.pop(0)
        if n < 4:
            self.players[0].deploymentZone = 1
            self.players[1].deploymentZone = 2
            if self.deploymentMap == 0:
                text = self.players[0].name + " deploys in the west. " + self.players[1].name + " deploys in the east."
                self.update_event_log(values, text)
        else:
            self.players[0].deploymentZone = 2
            self.players[1].deploymentZone = 1
            if self.deploymentMap == 0:
                text = self.players[1].name + " deploys in the west. " + self.players[0].name + " deploys in the east."
                self.update_event_log(values, text)
            
        #Set up deployment zone nodes
        if self.deploymentMap == 0:
            #calculate centre point
            centrePoint = battlefield.size[0]/2
            xLeft = centrePoint - 12
            xRight = centrePoint + 11
            for node in self.nodes:
                if self.nodes[node].x < xLeft:
                    if self.players[0].deploymentZone == 1:
                        self.players[0].deploymentZoneNodes.append(node)
                    else:
                        self.players[1].deploymentZoneNodes.append(node)
                elif self.nodes[node].x > xRight:
                    if self.players[0].deploymentZone == 2:
                        self.players[0].deploymentZoneNodes.append(node)
                    else:
                        self.players[1].deploymentZoneNodes.append(node)
            
        #Assign who deploys first
        n = math.ceil(self.randomNumbers.pop(0)/3)
        self.currentTurn = self.players[n - 1]
        if self.players[0] == self.currentTurn:
            self.otherTurn = self.players[1]
        else:
            self.otherTurn = self.players[0]
        text = self.currentTurn.name + " deploys first."
        self.update_event_log(values, text)
        
    def update(self, values, event=None):
        
        if self.awaitingEvent and not self.checkingExplosions:
            if event != None:
                if event.type == KEYUP:
                    
                    if event.key == K_LCTRL:
                        if self.hideUI:
                            self.hideUI = False
                        else:
                            self.hideUI = True
                            
                    elif event.key == K_UP:
                        self.upPressed = False
                    elif event.key == K_DOWN:
                        self.downPressed = False
                    elif event.key == K_LEFT:
                        self.leftPressed = False
                    elif event.key == K_RIGHT:
                        self.rightPressed = False
                        
                    elif event.key == K_SPACE:
                        #check if current unit is none
                        if self.currentUnit != None:
                            #If not, move camera to the first node of the first model
                            if len(self.currentUnit.models[0].nodes) > 0:
                                point = self.currentUnit.models[0].nodes[0]
                                self.centre_camera_on_point(values, point)
                        
                    elif event.key == K_1 or event.key == K_KP1:
                        self.centre_camera_on_point(values, self.controlPoints[0])
                        
                    elif event.key == K_2 or event.key == K_KP2:
                        self.centre_camera_on_point(values, self.controlPoints[1])
                        
                    elif event.key == K_3 or event.key == K_KP3:
                        self.centre_camera_on_point(values, self.controlPoints[2])
                        
                    elif event.key == K_4 or event.key == K_KP4:
                        self.centre_camera_on_point(values, self.controlPoints[3])
                        
                    elif event.key == K_5 or event.key == K_KP5:
                        self.centre_camera_on_point(values, self.controlPoints[4])
                        
                    elif event.key == K_6 or event.key == K_KP6:
                        self.centre_camera_on_point(values, self.controlPoints[5])
                        
                    elif event.key == ord('u'):
                        if self.showInfo:
                            self.infoType = 0
                            self.get_panel_info(values)
                            
                    elif event.key == ord('t'):
                        if self.showInfo:
                            self.infoType = 1
                            self.get_panel_info(values)
                            
                    elif event.key == ord('m'):
                        if self.showInfo:
                            self.infoType = 2
                            self.get_panel_info(values)
                            
                    elif event.key == ord('n'):
                        if self.showInfo:
                            self.infoType = 3
                            self.get_panel_info(values)
                            
                    elif event.key == ord('p'):
                        if self.showInfo:
                            self.get_panel_info(values, controlPoints=True)
                            
                    elif event.key == ord('h'):
                        if self.highlighting:
                            self.highlighting = False
                            self.highlightGroup.empty()
                        else:
                            self.highlighting = True
                            self.toggle_highlighting()
                            
                    elif event.key in [ord('q'), ord('w'), ord('a'), ord('s'), ord('z'), ord('x'), ord('e'),
                                        ord('r'), ord('d'), ord('f'), ord('c'), ord('v')]:
                        for button in values.buttons:
                            if event.key == ord(button.code):
                                self.handle_button(values, button)
                                break
                            
                        if event.key == ord('c'):
                            self.cPressed = False
                            
                    elif event.key == K_LCTRL:
                        self.ctrlPressed = False
                        
                    elif event.key == K_LALT:
                        self.altPressed = False
                    
                elif event.type == KEYDOWN:
                    
                    if event.key == K_UP:
                        self.upPressed = True
                        self.downPressed = False
                        
                    elif event.key == K_DOWN:
                        self.downPressed = True
                        self.upPressed = False
                        
                    elif event.key == K_LEFT:
                        self.leftPressed = True
                        self.rightPressed = False
                        
                    elif event.key == K_RIGHT:
                        self.rightPressed = True
                        self.leftPressed = False
                        
                    elif event.key == ord('c'):
                        self.cPressed = True
                        
                    elif event.key == K_LCTRL:
                        self.ctrlPressed = True
                        
                    elif event.key == K_LALT:
                        self.altPressed = True
                        
                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        #Find out if click is on the UI
                        if not self.hideUI and (pos[1] < 32 or pos[0] < 160 or pos[0] > 1119 or pos[1] > 511):
                            #See if click was with a command or on the even log
                            isCommand = misc.is_point_inside_rect(pos[0], pos[1], pygame.Rect(860, 520, 420, 200))
                            isEvent = misc.is_point_inside_rect(pos[0], pos[1], pygame.Rect(430, 520, 420, 200))
                            if isCommand:
                            #Adjust pos to reflect where it is in the command surface
                                pos = (pos[0] - 860, pos[1] - 520)
                                for button in values.buttons[:]:
                                    clicked = misc.is_point_inside_rect(pos[0], pos[1], button.rect)
                                    if clicked:
                                        self.handle_button(values, button) 
                                        break
                            elif isEvent:
                                #Adjust pos to reflect where it is in the event surface
                                pos = (pos[0] - 430, pos[1] - 520)
                                for button in self.logButtons:
                                    clicked = misc.is_point_inside_rect(pos[0], pos[1], button.sprite.rect)
                                    if clicked:
                                        if button.use == 0:
                                            direction = -1
                                        elif button.use == 1:
                                            direction = 1
                                        else:
                                            direction = 0
                                        if direction != 0:
                                            self.update_event_log(values, scroll=True, direction=direction)
                                            break         
                            else:
                                print("Isn't a command or event")
                        else:
                            worldPos = (pos[0] + self.xOffset, pos[1] + self.yOffset)
                            #Is the click out of bounds
                            if (worldPos[0] < self.lowestX or worldPos[0] > self.highestX or
                                worldPos[1] < self.lowestY or worldPos[1] > self.highestY):
                                print("OUT OF BOUNDS")
                                
                            else:
                                #Find node that click is in and save it
                                x = max(int((worldPos[0] - 160)/32), 0)
                                y = max(int((worldPos[1] - 32)/32), 0)
                                self.currentNode = self.nodes[(x, y)]
                                #Take action based on game state/show info
                                
                                if self.showInfo:
                                    self.get_panel_info(values)
                                
                                self.handle_field_click(values)
                                
                    elif event.button in [4, 5]:
                        pos = pygame.mouse.get_pos()
                        #Find out if scroll is on the UI
                        if not self.hideUI and (pos[1] < 32 or pos[0] < 160 or pos[0] > 1119 or pos[1] > 511):
                            #See if in the even log
                            isEvent = misc.is_point_inside_rect(pos[0], pos[1], pygame.Rect(430, 520, 420, 200))
                            if isEvent:
                                if event.button == 4:
                                    direction = -1
                                else:
                                    direction = 1
                                self.update_event_log(values, scroll=True, direction=direction)
                                
            elif self.ctrlPressed and self.altPressed and self.cPressed and self.state not in [54, 55, 56]:
                self.state = 56
                self.awaitingEvent = False
                           
            else:
                self.scroll(values, 32) 
        
        elif self.checkingExplosions:
            print("Checking explosions!")
            self.checkingExplosions = False #Adding this to prevent the script from crashing
        
        else:
            
            #Check if a player has been wiped
            for player in self.players:
                alive = False
                for unit in player.units:
                    if not self.units[unit].destroyed:
                        alive = True
                        break
                
                if not alive:
                    player.armyWiped = True
                    self.state = 55
            
            #Deployment - select a unit to deploy
            if self.state in [0, 3, 5]:
                self.handle_deployment(values)
                
            elif self.state in [6, 7, 8, 9, 10, 11, 13, 14, 58, 59, 60, 61]:
                self.handle_movement(values)
                
            elif self.state in [15, 16, 17, 18, 19, 20, 21, 22, 23]:
                self.handle_magic(values)
                
            elif self.state in [24, 25, 26, 27, 28, 29, 30, 31, 32]:
                self.handle_shooting(values)
                
            elif self.state in [33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]:
                self.handle_charge(values)
                
            elif self.state in [44, 45, 46, 47, 48, 49, 50, 51]:
                self.handle_melee(values)
                
            elif self.state in [52, 53]:
                self.handle_morale(values)
                
            elif self.state in [54, 55, 56]:
                self.handle_endgame(values)

    def apply_damage(self, values, attacks, targetCodex, spell=None, melee=False):
        
        damage = 0
        hits = 0
        deaths = {}
        unitAlive = True
        unit = self.units[attacks[0].primaryTarget.unitID]
        
        print("======")
        
        #Loop through attacks
        for attack in attacks:
            #If main target is dead
            if attack.primaryTarget.dead:
                #set main target to none
                attack.primaryTarget = None
                #keep popping targets until a living one can be found
                try:
                    while attack.primaryTarget == None:
                        attack.primaryTarget = attack.otherTargets.pop(0)
                        if attack.primaryTarget.dead:
                            attack.primaryTarget = None
                except IndexError:
                    pass
            #If main target is not none, carry out attack
            if attack.primaryTarget != None:
                
                success = True
                
                #check to-hit
                if attack.toHit < 99:
                    roll = self.randomNumbers.pop(0)
                    if roll > attack.toHit:
                        print("Failed to-hit. Roll:", roll, "Range Skill:", attack.toHit)
                        success = False
                    else:
                        hits += 1
                  
                #check strength      
                if success and attack.strength < 99:
                    
                    print("Strength:", attack.strength)
                    
                    if attack.strength > attack.primaryTarget.fort:
                        
                        if attack.strength >= (attack.primaryTarget.fort * 2):
                            dc = 5
                            
                        else:
                            dc = 4
                            
                    elif attack.strength < attack.primaryTarget.fort:
                        
                        if attack.strength <= (attack.primaryTarget.fort/2):
                            dc = 1
                            
                        else:
                            dc = 2
                            
                    else:
                        dc = 3
                        
                    roll = self.randomNumbers.pop(0)
                    if roll > dc:
                        print("Failed crit check. roll:", roll, "dc:", dc)
                        success = False
                        
                #check saves
                if success and attack.ap < 99:
                    
                    armour = attack.primaryTarget.armour - attack.ap
                    if melee:
                        save = max(armour, attack.primaryTarget.invul)
                    else:
                        save = max(armour, attack.primaryTarget.cover, attack.primaryTarget.invul)
                    
                    roll = self.randomNumbers.pop(0)
                    if roll <= save:
                        print("Successful save!. roll:", roll, "save:", save)
                        success = False
                        
                if success:
                
                    #reduce target hp by damage
                    attack.primaryTarget.currentHP -= attack.damage
                    damage += attack.damage
                    #If target is dead, mark it as dead and save deathcount
                    if attack.primaryTarget.currentHP <= 0:
                        attack.primaryTarget.dead = True
                        unit.modelsLost += 1
                        #Kill sprite and wipe nodes
                        attack.primaryTarget.sprite.kill()
                        for n in attack.primaryTarget.nodes[:]:
                            self.nodes[n].takenBy = None
                            attack.primaryTarget.nodes.remove(n)
                            
                        attack.primaryTarget.topLeftNode = None
                        #Store death info
                        data = targetCodex.models[attack.primaryTarget.data].name
                        if data not in deaths:
                            deaths[data] = 1
                        else:
                            deaths[data] += 1
                            
                        self.checkingExplosions = True
                            
                        #Pass details to is unit still alive
                        unitAlive = self.is_unit_still_alive(values, unit, targetCodex=targetCodex)
                
        #Report deaths
        self.update_control_point_status(values)
        
        if spell != None:
            text1 = self.currentUnit.name + " casts " + spell.name + " on " + unit.name + "!"
            text2 = "The spell hits, dealing " + str(damage) + " damage"
            if len(deaths) > 0:
                i = 1
                text3 = " killing "
                for d in deaths:
                    #first string
                    if i == 1:
                        text3 = text3 + str(deaths[d]) + " " + d + "(s)"
                    #last string in dict
                    elif i == len(deaths):
                        text3 = text3 + " and " + str(deaths[d]) + " " + d + "(s)!"
                    else:
                        text3 = text3 + ", " + str(deaths[d]) + " " + d + "(s)"
                    i += 1
                    
                if i == 2:
                    text3 = text3 + "!"
            else:
                text3 = ""
            if unitAlive:
                text4 = ""
            else:
                text4 = unit.name + " has been destroyed!"
                for p in self.unitsForMelee:
                    if unit.ID in p:
                        p.remove(unit.ID)
            
            text = text1 + text2 + text3 + text4
            
        elif melee:
            shootingUnit = self.units[self.attackingModels[0].unitID]
            text1 = (shootingUnit.name + " makes " + str(len(attacks)) + " attacks with their " + 
                     self.currentWeapon.name + "(s) into " + unit.name + "! ")
            text2 = str(hits) + " attacks hit, dealing " + str(damage) + " damage"
            if len(deaths) > 0:
                i = 1
                text3 = " killing "
                for d in deaths:
                    #first string
                    if i == 1:
                        text3 = text3 + str(deaths[d]) + " " + d + "(s)"
                    #last string in dict
                    elif i == len(deaths):
                        text3 = text3 + " and " + str(deaths[d]) + " " + d + "(s)!"
                    else:
                        text3 = text3 + ", " + str(deaths[d]) + " " + d + "(s)"
                    i += 1
                    
                if i == 2:
                    text3 = text3 + "!"
            else:
                text3 = ""
            if unitAlive:
                text4 = ""
            else:
                text4 = unit.name + " has been destroyed!"
                for p in self.unitsForMelee:
                    if unit.ID in p:
                        p.remove(unit.ID)
            
            text = text1 + text2 + text3 + text4
            
        else:
            shootingUnit = self.units[self.attackingModels[0].unitID]
            text1 = (shootingUnit.name + " fire " + str(len(attacks)) + " shots from their " + 
                     self.currentWeapon.name + "(s) into " + unit.name + "! ")
            text2 = str(hits) + " shots hit, dealing " + str(damage) + " damage"
            if len(deaths) > 0:
                i = 1
                text3 = " killing "
                for d in deaths:
                    #first string
                    if i == 1:
                        text3 = text3 + str(deaths[d]) + " " + d + "(s)"
                    #last string in dict
                    elif i == len(deaths):
                        text3 = text3 + " and " + str(deaths[d]) + " " + d + "(s)!"
                    else:
                        text3 = text3 + ", " + str(deaths[d]) + " " + d + "(s)"
                    i += 1
                    
                if i == 2:
                    text3 = text3 + "!"
            else:
                text3 = ""
            if unitAlive:
                text4 = ""
            else:
                text4 = unit.name + " has been destroyed!"
                unit.destroyed = True
                for p in self.unitsForMelee:
                    if unit.ID in p:
                        p.remove(unit.ID)
            
            text = text1 + text2 + text3 + text4
        
        self.update_event_log(values, text)
        self.update_melee_status(values)
        
    def attack_charge_target(self, values):
        if len(self.selectedModels) > 0:
                
            #If current unit charged this turn and its target is still alive
            chooseTarget = False
            if self.currentUnit.chargedUnit != None:
                if not self.units[self.currentUnit.chargedUnit].destroyed:
                    targetFound = False
                    self.attackingModels = []
                    #Is current unit in range of its charge target?
                    for model in self.selectedModels:
                        result = self.get_melee_range(self.currentUnit, model, 
                                                      self.units[self.currentUnit.chargedUnit])
                        if len(result) > 0:
                            #If so, skip straight to rolling attack
                            model.attackTargets = result
                            self.attackingModels.append(model)
                            targetFound = True
                    if targetFound:
                        self.state = 51
                        self.awaitingEvent = False 
                    else: #Else, player must select different models
                        self.update_main_message(values, "No models are in range of target.")
                else:
                    chooseTarget = True
            else:
                chooseTarget = True
                
            if chooseTarget:
                self.state = 49
                self.awaitingEvent = False
            
    def centre_camera_on_point(self, values, point):
        
        self.xOffset = ((point[0] * 32) + 160) - 640
        self.xOffset = max(self.xOffset, 0)
        self.xOffset = min(self.xOffset, self.xOffsetMax)
        
        self.yOffset = ((point[1] * 32) + 32) - 360
        self.yOffset = max(self.yOffset, 0)
        self.yOffset = min(self.yOffset, self.yOffsetMax)
        
        self.camera = self.surface.subsurface(self.xOffset, self.yOffset, 1280, 720)
        
    def check_engame_points(self, values):
        
        #Check for Conquest
        player1 = 0
        player2 = 0
        #Loop through control points
        for status in self.controlPointStatus:
            #Sum points per player
            if status == 1:
                player1 += 1
            elif status == 2:
                player2 += 1
        #Assign points#
        if player1 > 0:
            self.players[0].vp += (player1 * 3)
            self.players[0].objectivesAcheived.append(Objective("Conquest", (0, 2)))
            text = self.players[0].name + " scores " + str(player1 * 3) + " points for achieving Conquest!"
            self.update_event_log(values, text)
        if player2 > 0:
            self.players[1].vp += (player2 * 3)
            self.players[1].objectivesAcheived.append(Objective("Conquest", (0, 2)))
            text = self.players[1].name + " scores " + str(player2 * 3) + " points for achieving Conquest!"
            self.update_event_log(values, text)
            
        #Check for Full Distance
        
        #loop through players
        for player in self.players:
            #loop through deployment nodes
            if player == self.players[0]:
                otherPlayer = self.players[1]
            else:
                otherPlayer = self.players[0]
            for node in player.deploymentZoneNodes:
                #if node is taken by enemy model, award Full Distance and break out of loop
                if self.nodes[node].takenBy in otherPlayer.models:
                    if "AIRBORNE" not in self.models[self.nodes[node].takenBy].keywords:
                        otherPlayer.vp += 1
                        otherPlayer.objectivesAcheived.append(Objective("Full Distance", (0, 3)))
                        text = otherPlayer.name + " scores 1 point for achieving Full Distance!"
                        self.update_event_log(values, text)
                        break
            
        self.set_up_header_display(values)
        
    def check_explosions(self, values):
        newExplosions = False
        for m in self.models:
            if self.models[m].dead and not self.models[m].exploded and 'Explodes' in self.models[m].keywords:
                newExplosions = True
                self.models[m].exploded = True
                #Calculate range around model
                for x in range(self.models[m]):
                    pass
                #Loop through nodes in range
                #
        
    def check_kill_points(self, values, unit):
        
        #If this is the first unit to die, award First Blood
        if not self.firstBloodAwarded:
            self.firstBloodAwarded = True
            if unit.ID in self.players[0].units:
                scoringPlayer = self.players[1]
            else:
                scoringPlayer = self.players[0]
            
            scoringPlayer.vp += 1
            scoringPlayer.objectivesAcheived.append(Objective("First Blood", (0, 0)))
            text = scoringPlayer.name + " scores 1 point for achieving First Blood!"
            self.update_event_log(values, text)
            self.set_up_header_display(values)
        
        #If this unit is the boss, award Kingslayer
        if unit.isBoss:
            if unit.ID in self.players[0].units:
                scoringPlayer = self.players[1]
            else:
                scoringPlayer = self.players[0]
                
            scoringPlayer.vp += 2
            scoringPlayer.objectivesAcheived.append(Objective("Kingslayer", (0, 1)))
            text = scoringPlayer.name + " scores 2 points for achieving Kingslayer!"
            self.update_event_log(values, text)
            self.set_up_header_display(values)
        
    def check_unit_coherency(self, unit):
        #If unit contains just one model, return true by default
        if len(unit.models) > 1:
            #set up coherent and not found lists
            coherent = []
            notFound = []
            dead = []
            for model in unit.models:
                if model.dead:
                    dead.append(model)
                else:
                    notFound.append(model)
            #Set first living model as starting model
            coherent.append(notFound.pop(0))
            new = True
            #while loop
            while new:
                new = False
                #loop through coherent list
                for model1 in coherent[:]:
                    #loop through not found list
                    for model2 in notFound[:]:
                        #Get distance between nodes
                        distance = 9999
                        for node1 in model1.nodes:
                            for node2 in model2.nodes:
                                d = self.get_distance_between_nodes(node1, node2)
                                distance = min(d, distance)
                        #If distance is 2 or less, add model to coherent list and flag new
                        if distance <= 2:
                            coherent.append(model2)
                            notFound.remove(model2)
                            new = True
                            
            
        else:
            return True
        
        #Return true of coherent list is as long as model list
        if (len(coherent) + len(dead)) == len(unit.models):
            return True
        #Else, return false
        else:
            return False
        
    def clear_buttons(self, values):
        values.buttons = []
        self.commandListGroup.empty()
        self.commandListMaxed = False
        
    def delete_unit_from_field(self, unit):
        for model in unit.models:
            if model.sprite != None:
                model.sprite.kill()
                
            #remove node associations
            for n in model.nodes[:]:
                self.nodes[n].takenBy = None
                model.nodes.remove(n)
                
            model.topLeftNode = None
            
    def deploy_unit(self, values, selectedNode, nodeList, unit, playerCodex, deployment):
        """
        selectedNode - Node Object where the deployment is to take place
        nodeList - tuple of all deployable Node coordinates
        unit - Unit Object being deployed
        playerCodex - Codex Object for the player's unit
        deployment - bool, True = deployment phase, False = unit disembarking from transport
        """
        
        #Check to see if selected Node is on a friendly transport. If so, change state to ask player if 
        #they would like to deploy within the transport
        #Make sure current unit is infantry before offering to deploy
        
        infantry = True
        for model in unit.models:
            if "INFANTRY" not in model.keywords:
                infantry = False
                break
        
        if deployment and infantry and selectedNode.takenBy != None:
            if ("TRANSPORT" in self.models[selectedNode.takenBy].keywords and
                selectedNode.takenBy in self.currentTurn.models):
                self.currentTransport = self.units[self.models[selectedNode.takenBy].unitID]
                text = "Would you like to deploy " + unit.name + " inside of " + self.currentTransport.name + "?"
                self.update_main_message(values, text)
                self.state = 57
                return None
        
        #Check if node is in players deployment zone
        if selectedNode.coordinates in nodeList:
            #If so, look at the viability of placing models as closely to the click as possible
            successes = 0 #Count of models successfully allocated
            
            nodes = []
            for node in nodeList:
                self.nodes[node].H = (abs(self.nodes[node].x - selectedNode.x) + 
                                      abs(self.nodes[node].y - selectedNode.y))
                nodes.append(self.nodes[node])
            nodes.sort(key=operator.attrgetter("H"))
            
            images = {}
            
            for model in unit.models:
                #Loop through size and check that nodes are available
                size = playerCodex.models[model.data].size
                running2 = True
                if "FLY" in model.keywords:
                    checkWalkable = False
                else:
                    checkWalkable = True
                while len(nodes) > 0 and running2:
                    node = nodes.pop(0)
                    running = True
                    while running:
                        running, taken = self.get_standable_nodes(node, size, checkWalkable, deploymentOnly=deployment)
                        
                        if running:
                            #If enough space can be found assign nodes to model
                            cover = 3
                            for n in taken:
                                self.nodes[n].takenBy = model.ID
                                cover = min(cover, self.nodes[n].cover)
                                model.nodes.append(n)
                                
                                #Set top left node
                                if model.topLeftNode == None:
                                    model.topLeftNode = n
                                else:
                                    if n[0] <= model.topLeftNode[0] and n[1] <= model.topLeftNode[1]:
                                        model.topLeftNode = n
                             
                            #set cover   
                            model.cover = cover
                            
                            #Set up sprites
                            imageName = playerCodex.models[model.data].spriteName
                            imagePrimary = playerCodex.models[model.data].spritePrimary
                            imageRect = playerCodex.models[model.data].spriteRect
                            imageRect = (node.backSprite.rect.x, node.backSprite.rect.y, imageRect[0], 
                                         imageRect[1])
                            
                            if imageName not in images:
                                if imagePrimary:
                                    images[imageName] = resources.load_primary_sprite(imageName)
                                else:
                                    images[imageName] = resources.load_secondary_sprite(imageName)
                            image = images[imageName]
                            model.sprite = sprites.GameSprite(image, imageRect)
                            self.modelsGroup.add(model.sprite)
                            running = False
                            running2 = False
                            successes += 1
            
            
            
            #Clean up failures
            if successes < len(unit.models):
                print("ULTIMATE FAILURE")
                #kill models sprites
                self.delete_unit_from_field(unit)
                
            #If successful and disembarking
            elif not deployment:
                if self.check_unit_coherency(unit):
                    text = "{0} has disembarked.".format(self.currentUnit.name)
                    self.update_event_log(values, text)
                    self.update_control_point_status(values)
                    #Flag unit as having disembarked
                    self.currentUnit.disembarked = True
                    
                    #Remove unit from onboard
                    self.currentTransport.onboard.remove(self.currentUnit.ID)
                    
                    #Set transport up as current unit again
                    self.currentUnit = self.currentTransport
                    self.currentTransport = None
                    
                    
                    self.squaresGroup.empty()
                    self.state = 9
                    self.awaitingEvent = False
                else:
                    text = "Unable to deploy - units cannot be deployed in coherency"
                    self.update_main_message(values, text)
                    self.delete_unit_from_field(unit)
            
            else:
                #Add purple squares to units
                self.get_purple_squares()
                #Update message
                text = self.currentTurn.name + " can move individual models or confirm the unit's position"
                self.update_main_message(values, text)
                self.state = 3
                
    def embark_on_transport(self, values):
        
        if self.phase == 1:
            self.update_control_point_status(values)
            self.update_melee_status(values)
            self.squaresGroup.empty()
            #Clear old nodes and mark unit as having finished the phase
            self.currentUnit.endPhase = True
            for model in self.currentUnit.models:
                model.oldNodes = []
                
            if self.highlighting:
                self.toggle_highlighting()
            if self.phase == 1:
                self.state = 8
                
            self.delete_unit_from_field(self.currentUnit)
        
        self.currentTransport.onboard.append(self.currentUnit.ID)
        if self.phase == 0:
            text = self.currentTurn.name + " deploys " + self.currentUnit.name + " inside of " + self.currentTransport.name
        else:
            text = self.currentUnit.name + " embarks upon " + self.currentTransport.name
        self.currentTransport = None
        
        return text
            
    def get_closest_visible_unit(self):
        #Get closest visible unit
        if self.currentTurn == self.players[0]:
            enemy = self.players[1]
        else:
            enemy = self.players[0]
        maxRange = 999
        finalNodes = {}
        for unit in enemy.units:
            for model in self.selectedModels:
                #Get list of in range nodes
                attackTargets = self.get_nodes_in_range(model, self.units[unit], maxRange)
                #Check LOS on in range nodes
                newNodes = []
                for target in attackTargets:
                    for node in model.nodes:
                        if node not in newNodes:
                            success = self.is_node_in_line_of_sight(node, target, enemy)
                            if success:
                                newNodes.append(target)
                                break
                        
                #Set closest node as the new max range    
                newDistances = {}
                for node1 in newNodes:
                    for node2 in model.nodes:
                        distance = self.get_distance_between_nodes(node1, node2)
                        maxRange = min(distance, maxRange)
                        newDistances[distance] = node1
                        
                #Remove any final nodes which are further than the maximum
                for distance in list(finalNodes.keys()):
                    if distance > maxRange:
                        del finalNodes[distance]
                        
                #Add new nodes which are at the distance
                for d in newDistances:
                    if d == maxRange:
                        finalNodes[d] = newDistances[d]
                        
        #Grab units for final nodes
        self.currentUnit.closestVisible = []
        for d in finalNodes:
            unit = self.models[self.nodes[finalNodes[d]].takenBy].unitID
            if unit not in self.currentUnit.closestVisible:
                self.currentUnit.closestVisible.append(unit)
        
    def get_command_list(self, values, itemList, actionList=None):
        
        """
        NOTE - THE COMMANDLISTCOUNTER SHOULD BE RESET TO 0 AFTER SELECTING AN OPTION, PROVIDING THE OPTION LIST IS LARGER THAN 11 ITEMS
                THIS MAY CAUSE AN ISSUE WITH LARGE MELEE FIGHTS
        """
        
        widePanelImage = resources.load_secondary_sprite("wide_panel01.png")
        buttonImage = pygame.transform.scale(widePanelImage, (210, 25))
        keys = ('q', 'w', 'a', 's', 'z', 'x', 'e', 'r', 'd', 'f', 'c', 'v')
        x = 0
        y = 20
        createButton = True
        moreNeeded = False
        
        for i in range(0, 12):
            
            #At button 12, consider a 'more' button
            if i == 11 and self.commandListCounter == 0:
                try:
                    #Check if another button in needed
                    item = itemList[i + self.commandListCounter + 1] 
                    #if so, create a 'more' button
                    moreNeeded = True
                    createButton = False
                except IndexError:
                    pass
            elif i == 11 and self.commandListCounter > 0:
                moreNeeded = True
                createButton = False
            if createButton:
            
                try:
                    #Set up button object for each item in the given list
                    item = itemList[i + self.commandListCounter]
                    if self.state == 0:
                        storage = self.units[item]
                        text = storage.name + " (" + keys[i] + ")"
                        action = 0
                    elif self.state == 17:
                        if item != "Cancel":
                            storage = item
                            text = item.name + " (" + keys[i] + ")"
                            action = 20
                        else:
                            storage = None
                            text = item + " (" + keys[i] + ")"
                            action = 21
                    elif self.state == 26:
                        if item != "Cancel":
                            storage = item
                            text = item.name + " (" + keys[i] + ")"
                            action = 32
                        else:
                            storage = None
                            text = item + " (" + keys[i] + ")"
                            action = 33
                    elif self.state == 45:
                        storage = self.units[item]
                        text = storage.name + " (" + keys[i] + ")"
                        action = 58
                    elif self.state == 46:
                        if item != "End attack":
                            storage = item
                            text = storage.name + " (" + keys[i] + ")"
                            action = 59
                        else:
                            storage = None
                            text = item + " (" + keys[i] + ")"
                            action = 70
                    elif self.state == 60:
                        if item != "Cancel":
                            storage = self.units[item]
                            text = storage.name + " (" + keys[i] + ")"
                            action = 79
                        else:
                            storage = None
                            text = item + " (" + keys[i] + ")"
                            action = 80 
                    elif self.state in [2, 5, 8, 9, 10, 11, 14, 16, 18, 19, 20, 21, 23, 25, 27, 28, 29, 30, 32,
                                        34, 35, 36, 37, 40, 42, 43, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58,
                                        59, 61]:
                        storage = None
                        text = item + " (" + keys[i] + ")"
                        action = actionList[i]
                        
                    button = sprites.Button(keys[i], action, buttonImage, (x, y, 210, 25), text, values.font20, 
                                            values, storage=storage)
                    
                    #Add button to group
                    self.commandListGroup.add(button.sprites)
        
                    #Adjust x and y
                    x += 210
                    if x > 210:
                        y += 25
                        x = 0
                        
                except IndexError:
                    createButton = False
                    self.commandListMaxed = True
                    if self.commandListCounter > 0:
                        moreNeeded = True
                    
            if moreNeeded:
                text = "More..." + " (" + keys[i] + ")"
                button = sprites.Button(keys[i], 1, buttonImage, (x, y, 210, 25), text,
                                        values.font20, values)
                
                self.commandListGroup.add(button.sprites)
                createButton = False
                break
    
    def get_disembark_nodes(self, transport, playerCodex, emergency):
        
        #Get enemy model IDs
        if transport.ID in self.players[0].units:
            enemy = self.players[1]
        else:
            enemy = self.players[0]
            
        #Get top left and bottom right vectors
        x_min = transport.models[0].topLeftNode[0]
        y_min = transport.models[0].topLeftNode[1]
        size = playerCodex.models[transport.models[0].data].size
        x_max = transport.models[0].topLeftNode[0] + size[0]
        y_max = transport.models[0].topLeftNode[1] + size[1]
        
        #Set up list for available nodes
        availableNodes = []
        
        #Loop through x and y nodes
        for x in range(x_min - 3, x_max + 3):
            for y in range(y_min - 3, y_max + 3):
                #Are x and y in the node list? If not, ignore
                if (x, y) in self.nodes:
                    #Are x and y in the transport's nodes? If so, ignore
                    ignore = False
                    if (x, y) in transport.models[0].nodes and not emergency:
                        ignore = True
                    #Check node's neighbours
                    if not ignore:
                        close = False
                        for x2 in range(x - 1, x + 2):
                            if not close:
                                for y2 in range(y - 1, y + 2):
                                    if (x, y) == (x2, y2):
                                        pass
                                    else:
                                        #If neighbour is in node list and is taken by enemy, then ignore the node
                                        if self.nodes[(x2, y2)].takenBy in enemy.models:
                                            close = True
                                            break
                        
                        #If all checks are passed, add node to available
                        if not close:
                            availableNodes.append((x, y))
                            
        return availableNodes
            
    def get_distance_between_nodes(self, node1, node2):
        #Get absolute differences
        xDiff = abs(node1[0] - node2[0])
        yDiff = abs(node1[1] - node2[1])
        
        #Set the smallest and largest difference
        smallDiff = min(xDiff, yDiff)
        largeDiff = max(xDiff, yDiff)
        
        #calculate distance as diagonal movement + extra horizontal/vertical movements
        distance = smallDiff + (largeDiff - smallDiff)
        
        return distance
    
    def get_melee_range(self, unit, model, target):
        
        attackingModels = [model]
        result = []
        i = 0
        while i < 2:
            #Loop through attacking models
            for m in attackingModels[:]:
                #Loop through model's nodes
                for node in m.nodes:
                    #Loop through adjacent nodes
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            adjNode = (x + node[0], y + node[1])
                            if adjNode in self.nodes:
                                #If node contains an enemy from the target unit, approve for list
                                if self.nodes[adjNode].takenBy != None:
                                    if (self.models[self.nodes[adjNode].takenBy] in target.models and
                                        adjNode not in result):
                                        success = True
                                        if ("AIRBORNE" in model.keywords and "FLY" not in 
                                            self.models[self.nodes[adjNode].takenBy].keywords):
                                            success = False
                                        if ("AIRBORNE" in self.models[self.nodes[adjNode].takenBy].keywords 
                                            and "FLY" not in model.keywords):
                                            success = False
                                        if success:
                                            result.append(adjNode)
                                    #If node contains the unit, add to allies list if this is the first iteration
                                    elif (i == 0 and self.models[self.nodes[adjNode].takenBy] in unit.models
                                          and self.models[self.nodes[adjNode].takenBy] != model):
                                        attackingModels.append(self.models[self.nodes[adjNode].takenBy])
                                        
                attackingModels.remove(m)
            
            i += 1
            
        return result
    
    def get_movement_range(self, startNode, minMove, maxMove, size, checkPassable=True, checkStandable=True,
                           checkWalkable=False, allowTaken=True, passClose=False, standClose=False, 
                           passCloseSpecific=None, standCloseSpecific=None, mustBeClose=False, modelID=None,
                           enemyModels=[]):
        #Set up openList, closedList, available and round
        openList = [] #nodes for checking
        closedList = [startNode] #nodes already looked at
        available = [] #standable nodes
        currentRound = 1
        
        #NOTE - allowTaken is used to check if its okay to move through taken nodes
        
        #Add nodes adjacent to the starting node to the open list
        for x in range(-1, 2):
            for y in range(-1, 2):
                newNode = (startNode[0] + x, startNode[1] + y)
                if newNode in self.nodes:
                    success = True
                    
                    if newNode in closedList:
                        success = False
                    
                    #Make passable node checks
                    if success and checkPassable:
                        success = self.get_passable_nodes(self.nodes[newNode], size, checkWalkable, allowTaken, 
                                                          passClose, modelID, enemyModels, 
                                                          passCloseSpecific=passCloseSpecific)
                        
                    if success:
                        openList.append(newNode)

        #while open list is not empty and max move has not been reached
        while len(openList) > 0 and currentRound <= maxMove:
            #loop through open list nodes
            for node in openList[:]:
                #remove from open list and add to closed list
                openList.remove(node)
                closedList.append(node)
                #Check if node is appropriate
                #If so, add to available and add neighbours to open list
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        newNode = (node[0] + x, node[1] + y)
                        if newNode in self.nodes:
                            success = True
    
                            if newNode in closedList or newNode in openList:
                                success = False
                                
                            if success and checkPassable:
                                success = self.get_passable_nodes(self.nodes[newNode], size, checkWalkable,
                                                                  allowTaken, passClose, modelID, enemyModels,
                                                                  passCloseSpecific=passCloseSpecific)
                                
                            if success:
                                openList.append(newNode)
                
                success2 = True
                if checkStandable and currentRound >= minMove:
                    success2 = self.get_standable_nodes(self.nodes[node], size, checkWalkable, 
                                                       returnTaken=False, deploymentOnly=False, 
                                                       allowClose=standClose, modelID=modelID,
                                                       enemyModels=enemyModels,
                                                       standCloseSpecific=standCloseSpecific,
                                                       mustBeClose=mustBeClose)
                
                if success2 and currentRound >= minMove:
                    available.append(node)
                
            #advance round
            currentRound += 1

        #when done, return available
        return available
    
    def get_next_melee_turn(self):
        #Set current player and other player flags to false
        currentPlayer = False
        otherPlayer = False
        priority = 0
        
        #Loop through priorities
        for p in self.unitsForMelee:
            #Loop through lists
            for l in p:
                #If current or other player units can be found, turn appropriate flags to true
                if l in self.currentTurnSaved.units:
                    currentPlayer = True
                elif l in self.otherTurnSaved.units:
                    otherPlayer = True
                    
            #Once at least one flag is true, break out of loops
            if currentPlayer or otherPlayer:
                self.meleePriority = priority
                break
            else:
                priority += 1
                
        
        #If only one flag is true, assign that player the current turn
        #Otherwise, if both are true and current turn is none, assign saved current turn as current turn
        if currentPlayer and otherPlayer and self.currentTurn == None:
            otherPlayer = False
        #Else, if both are true and current turn is not none, alternate current player
        elif currentPlayer and otherPlayer and self.currentTurn != None:
            if self.currentTurn == self.currentTurnSaved:
                currentPlayer = False
            else:
                otherPlayer = False
                
        if otherPlayer:
            self.currentTurn = self.otherTurnSaved
            self.otherTurn = self.currentTurnSaved
        elif currentPlayer:
            self.currentTurn = self.currentTurnSaved
            self.otherTurn = self.otherTurnSaved
                
        #If neither player has units, return false as melee will end
        if not currentPlayer and not otherPlayer:
            return False
        #Else, return true
        else:
            return True
    
    def get_nodes_in_range(self, model, target, attackRange):
        result = []
        
        #Loop through models in target
        for m in target.models:
            if not m.dead:
                #Loop through nodes in target model against attacking model
                for node1 in model.nodes:
                    for node2 in m.nodes:
                        distance = self.get_distance_between_nodes(node1, node2)
                        #If node is in range and not already in result list, add it
                        if distance <= attackRange and node2 not in result:
                            result.append(node2)
                        
        return result
        
    def get_panel_info(self, values, controlPoints=False):
        
        spr = []
        rightPanel = False
        
        if self.currentNode != None and not controlPoints:
        
            #Unit display
            if self.infoType == 0 and self.currentNode.takenBy != None:
                y = 190
                unit = self.units[self.models[self.currentNode.takenBy].unitID]
                #Display name
                image = values.font20.render(unit.name, True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 0, 
                                                      image.get_width(), image.get_height())))
                #Boss status
                if unit.isBoss:
                    image = values.font20.render("BOSS", True, values.colours["Red"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 20, 
                                                      image.get_width(), image.get_height())))
                
                #Portrait
                if unit.ID in self.players[0].units:
                    i = 0
                else:
                    i = 1
                    
                
                text = self.players[i].playerArmy.codex.models[unit.models[0].data].portraitSprite 
                image = resources.load_primary_sprite(text)
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 40, 
                                                      image.get_width(), image.get_height())))
                #Mage profile (if applicable)
                if unit.currentMana != None:
                    text = "Mana: " + str(unit.currentMana) + "/" + str(unit.maxMana)
                    image = values.font20.render(text, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 20
                    text = "Dispel Level: " + str(unit.dispelLevel)
                    image = values.font20.render(text, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 20
                    text = "   Dispel Rate: " + str(unit.dispelRate)
                    image = values.font20.render(text, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 20
                    
                
                #Models lost this turn
                text = "Models lost this turn: " + str(unit.modelsLost)
                image = values.font20.render(text, True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 40
                #flags
                text = ""
                moved = False
                if unit.moved:
                    text += "Moved this turn"
                    moved = True
                elif unit.advanced:
                    text += "Advanced this turn"
                    moved = True
                elif unit.fellBack:
                    text += "Fell back this turn"
                    moved = True
                if moved:
                    image = values.font20.render(text, True, values.colours["Red"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 20
                    
                #Set up charged unit info
                if unit.chargedUnit != None:
                    text = "Charged " + self.units[unit.chargedUnit].name + " this turn"
                    newText = misc.cut_down_string(text, 22)
                    for t in newText:
                        image = values.font20.render(t, True, values.colours["Red"])
                        spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                        y += 20
                    
                if unit.inMelee:
                    text = "In melee"
                    image = values.font20.render(text, True, values.colours["Red"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 20
                
                if unit.ID in self.players[1].units:
                    rightPanel = True
                    self.rightPanelGroup.empty()
                else:
                    self.leftPanelGroup.empty()
                
            elif self.infoType == 1:
                #If terrain info, clear left panel and display
                self.leftPanelGroup.empty()
                y = 80
                
                image = values.font30.render("Terrain", True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 40, 
                                                      image.get_width(), image.get_height())))
                image = values.font20.render(self.currentNode.terrain, True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 20
                text = "Cover Bonus: " + str(self.currentNode.cover)
                image = values.font20.render(text, True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 20
                if self.currentNode.walkable:
                    text = "Walkable"
                    colour = values.colours["Black"]
                else:
                    text = "Unwalkable"
                    colour = values.colours["Red"]
                image = values.font20.render(text, True, colour)
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 20
                if self.currentNode.blocksLOS:
                    text = "Blocks line of sight"
                    image = values.font20.render(text, True, values.colours["Red"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                    
            elif self.infoType == 2 and self.currentNode.takenBy != None:
                y = 190
                model = self.models[self.currentNode.takenBy]
                #Name
                if model.ID in self.players[0].models:
                    i = 0
                else:
                    i = 1
                text = self.players[i].playerArmy.codex.models[model.data].name
                image = values.font20.render(text, True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 0, 
                                                      image.get_width(), image.get_height())))
                
                #Portrait
                text = self.players[i].playerArmy.codex.models[model.data].portraitSprite
                image = resources.load_primary_sprite(text)
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 40, 
                                                      image.get_width(), image.get_height())))
                
                #Characteristics
                hp = "HP: " + str(model.currentHP) + "/"  + str(model.maxHP) 
                move = "   Move: " + str(model.minMove) + "-" + str(model.maxMove)
                mSkill = "MS: " + str(model.mSkill)
                rSkill = "    RS: " + str(model.rSkill)
                attackSpeed = "    AS: " + str(model.attackSpeed)
                strength = "Str: " + str(model.strength)
                fortitude = "    Fort: " + str(model.fort)
                will = "    Will: " + str(model.will)
                text = [hp + move, mSkill + rSkill + attackSpeed, strength + fortitude + will]
                for t in text:
                    image = values.font20.render(t, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 20
                image = values.font20.render("Saves", True, values.colours["Aqua"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 20
                armour = "Arm: " + str(model.armour)
                cover = "  Cov: " + str(model.cover)
                invul = "  Inv: " + str(model.invul)
                image = values.font20.render(armour + cover + invul, True, values.colours["Black"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                #keywords
                y += 20
                image = values.font20.render("Keywords", True, values.colours["Aqua"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 20
                text = misc.cut_down_string(str(model.keywords), 25)
                for t in text:
                    image = values.font20.render(t, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                    y += 20
                #wargear
                image = values.font20.render("Wargear", True, values.colours["Aqua"])
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                y += 20
                #Get list of wargear names and counts
                wargear = {}
                string = ""
                for w in model.wargear:
                    gear = self.players[i].playerArmy.codex.wargear[(self.players[i].playerArmy.faction, w)].name
                    if gear in wargear:
                        wargear[gear] += 1
                    else:
                        wargear[gear] = 1
                #Combine to one string
                for w in wargear:
                    string += w + " x" + str(wargear[w]) + ", " 
                string = string.rstrip(", ")
                #Cut string back down
                text = misc.cut_down_string(string, 25)
                for t in text:
                    image = values.font20.render(t, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                    y += 20
                if model.ID in self.players[1].models:
                    rightPanel = True
                    self.rightPanelGroup.empty()
                else:
                    self.leftPanelGroup.empty()
                   
            #Transport view 
            elif self.infoType == 3 and self.currentNode.takenBy != None:
                if "TRANSPORT" in self.models[self.currentNode.takenBy].keywords:
                    y = 190
                    unit = self.units[self.models[self.currentNode.takenBy].unitID]
                    #Display name
                    image = values.font20.render(unit.name, True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 0, 
                                                          image.get_width(), image.get_height())))
                    
                    #Portrait
                    if unit.ID in self.players[0].units:
                        i = 0
                    else:
                        i = 1
                    text = self.players[i].playerArmy.codex.models[unit.models[0].data].portraitSprite
                    image = resources.load_primary_sprite(text)
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 40, 
                                                          image.get_width(), image.get_height())))
                    
                    if unit.ID in self.players[1].units:
                        rightPanel = True
                        self.rightPanelGroup.empty()
                    else:
                        self.leftPanelGroup.empty()
                        
                    y += 20
                    
                    #Set up subtitle reading "On board:"
                    image = values.font20.render("On board:", True, values.colours["Black"])
                    spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                          image.get_width(), image.get_height())))
                    y += 10
                    #Loop through units in transport
                    for u in unit.onboard:
                        y += 10
                        #Unit names
                        text = self.units[u].name + "("
                        #Loop through models and count variations
                        modelDict = {}
                        for model in self.units[u].models:
                            if model.ID in self.players[0].models:
                                i = 0
                            else:
                                i = 1
                            modelName = self.players[i].playerArmy.codex.models[model.data].name
                            if modelName in modelDict:
                                modelDict[modelName] += 1
                            else:
                                modelDict[modelName] = 1
                            
                        #combine to form one string per unit
                        first = True
                        for model in modelDict:
                            if first:
                                text += model + "x" + str(modelDict[model])
                                first = False
                            else:
                                text += ", " + model + "x" + str(modelDict[model])
                        
                        text += ")"
                        textList = misc.cut_down_string(text, 30)
                        for t in textList:
                            image = values.font20.render(t, True, values.colours["Black"])
                            spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                                  image.get_width(), image.get_height())))
                            y += 10
                            
        elif controlPoints:
            
            self.leftPanelGroup.empty()
            image = values.font20.render("Control Point Status", True, values.colours["Black"])
            spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), 40, 
                                                      image.get_width(), image.get_height())))
            
            i = 1
            y = 80
            for point in self.controlPointStatus:
                if point == 0:
                    status = "Neutral"
                    colour = values.colours["Black"]
                elif point == 1:
                    status = self.players[0].name
                    colour = self.players[0].colour
                elif point == 2:
                    status = self.players[1].name
                    colour = self.players[1].colour
                else:
                    status = "Contested"
                    colour = values.colours["Green"]
                text = "Point #" + str(i) + " - " + status
                image = values.font20.render(text, True, colour)
                spr.append(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 160, 0), y, 
                                                      image.get_width(), image.get_height())))
                i += 1
                y += 20
                
        if rightPanel:
            self.rightPanelGroup.add(spr)
        else:
            self.leftPanelGroup.add(spr)
            
    def get_passable_nodes(self, node, size, checkWalkable, allowTaken, allowClose=False, modelID=None,
                           enemyModels=[], passCloseSpecific=None):
        success = True
        try:
            for x in range(0, size[0]):
                for y in range(0, size[1]):
                    currentNode = (node.coordinates[0] + x, node.coordinates[1] + y) 
                    if self.nodes[currentNode].takenBy != None and not allowTaken:
                        if self.nodes[currentNode].takenBy != modelID:
                            otherModel = self.models[self.nodes[currentNode].takenBy]
                            if 'AIRBORNE' not in otherModel.keywords:
                                success = False
                    if success and checkWalkable and not self.nodes[currentNode].walkable:
                        success = False
                    if success and not allowClose:
                        #Check neighbouring nodes to see if they're taken by the enemy
                        for x2 in range(-1, 2):
                            for y2 in range(-1, 2):
                                closeNode = (currentNode[0] + x2, currentNode[1] + y2)
                                if closeNode in self.nodes:
                                    if self.nodes[closeNode].takenBy != None:
                                        if passCloseSpecific == None:
                                            if self.nodes[closeNode].takenBy in enemyModels:
                                                success = False
                                        else:
                                            if (self.models[self.nodes[closeNode].takenBy].unitID !=
                                                passCloseSpecific and self.nodes[closeNode].takenBy not in 
                                                self.currentTurn.models):
                                                success = False
                    if not success:
                        #break out of loops
                        raise KeyError
                
        except KeyError:
            success = False
                
        return success
        
    def get_purple_squares(self, highlightUnit=True, highlightModel=False, highlightMoved=True,
                           otherUnit=False, highlightSelected=False, highlightAttacking=False,
                           highlightTarget=False):
        #Add purple squares to units
        self.squaresGroup.empty()
        image = resources.load_primary_sprite("highlight_purple.png")
        if highlightUnit:
            unit = self.currentUnit
        elif otherUnit:
            unit = self.otherUnit
        if highlightUnit or otherUnit:
            for model in unit.models:
                highlight = True
                if not highlightMoved and len(model.oldNodes) > 0:
                    highlight = False
                if model.dead:
                    highlight = False
                if highlight:
                    for node in model.nodes:
                        x = self.nodes[node].backSprite.rect.x
                        y = self.nodes[node].backSprite.rect.y
                        self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
        elif highlightModel:
            for node in self.currentModel.nodes:
                x = self.nodes[node].backSprite.rect.x
                y = self.nodes[node].backSprite.rect.y
                self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
                
        elif highlightSelected:
            for model in self.selectedModels:
                for node in model.nodes:
                    x = self.nodes[node].backSprite.rect.x
                    y = self.nodes[node].backSprite.rect.y
                    self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
                    
        elif highlightAttacking:
            for model in self.attackingModels:
                for node in model.nodes:
                    x = self.nodes[node].backSprite.rect.x
                    y = self.nodes[node].backSprite.rect.y
                    self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
                    
        elif highlightTarget:
            for model in self.currentUnit.targetUnit.models:
                for node in model.nodes:
                    x = self.nodes[node].backSprite.rect.x
                    y = self.nodes[node].backSprite.rect.y
                    self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
        
    def get_random_numbers(self):
        
        rolls = []
        while len(rolls) < 1000:
            rolls.append(random.randint(1, 6))
            
        return rolls
    
    def get_standable_nodes(self, node, size, checkWalkable, returnTaken=True, deploymentOnly=True, 
                            allowClose=True, modelID=None, enemyModels=[], standCloseSpecific=None,
                            mustBeClose=False):
        success = True
        close = False
        try:
            taken = []
            for x in range(0, size[0]):
                for y in range(0, size[1]):
                    currentNode = (node.coordinates[0] + x, node.coordinates[1] + y) 
                    if deploymentOnly:
                        if (self.nodes[currentNode].takenBy == None and 
                            currentNode in self.currentTurn.deploymentZoneNodes and not checkWalkable):
                            pass
                            #Node is good, look for next
                        elif (self.nodes[currentNode].takenBy == None and 
                            currentNode in self.currentTurn.deploymentZoneNodes and 
                            self.nodes[currentNode].walkable):
                            pass
                            #Node is good, look for next
                        else:
                            success = False
                    else:
                        if self.nodes[currentNode].takenBy != None:
                            if self.nodes[currentNode].takenBy != modelID:
                                success = False
                        if success and checkWalkable and not self.nodes[currentNode].walkable:
                            success = False
                        if success and (not allowClose or mustBeClose):
                            #Check neighbouring nodes to see if they're taken by the enemy
                            for x2 in range(-1, 2):
                                for y2 in range(-1, 2):
                                    closeNode = (currentNode[0] + x2, currentNode[1] + y2)
                                    if closeNode in self.nodes:
                                        if self.nodes[closeNode].takenBy != None:
                                            if standCloseSpecific == None:
                                                if (not allowClose and self.nodes[closeNode].takenBy in 
                                                    enemyModels):
                                                    success = False
                                                elif (mustBeClose and self.nodes[closeNode].takenBy in 
                                                      enemyModels):
                                                    close = True
                                            else:
                                                if (self.models[self.nodes[closeNode].takenBy].unitID !=
                                                    standCloseSpecific and self.nodes[closeNode].takenBy not in
                                                    self.currentTurn.models):
                                                    success = False
                    if success:
                        taken.append(currentNode)
                    else:
                        raise KeyError
                
        except KeyError:
            success = False
            
        if mustBeClose and not close:
            success = False
                
        if returnTaken:
            return success, taken
        else:
            return success
    
    def handle_button(self, values, button):
        
        #Selecting a unit to deploy
        if button.use == 0:
            self.awaitingEvent = False
            self.commandListCounter = 0
            self.currentUnit = button.storage
            #Change state to 2 and set up new buttons
            self.state = 2
            self.handle_deployment(values)
        
        #Selecting 'more'
        elif button.use == 1:
            #Increase command list counter by 12, or reset to 0 if maxed out
            if self.commandListMaxed:
                self.commandListCounter = 0
            else:
                self.commandListCounter += 11
            #Set state to 0 and awaiting event off
            if self.state == 1:
                self.state = 0
            self.awaitingEvent = False
            
        #Selecting 'confirm' while deploying
        elif button.use == 2:
            if self.state == 3:
                self.awaitingEvent = False
            elif self.state == 57:
                #Make sure the transport has capacity to store the current unit
                #Loop through living models in the current unit and sum the total
                newModels = 0
                for model in self.currentUnit.models:
                    if not model.dead:
                        newModels += 1
                #Loop through living models and units in the current transport
                onboardModels = 0
                for unit in self.currentTransport.onboard:
                    for model in self.units[unit].models:
                        if not model.dead:
                            onboardModels += 1
                            
                if ((self.currentTransport.models[0].maxHP - onboardModels) - newModels) >= 0:
                    #If so, set state to 3 to progress the phase
                    self.state = 3
                    self.awaitingEvent = False
                #Else, warn the player and set state back to 2
                else:
                    text = "Cannot confirm: transport does not have capacity to carry this many models"
                    self.update_main_message(values, text)
                    #Set current transport back to none
                    self.currentTransport = None
                    self.state = 2
            
        #Cancel from deploying a unit
        elif button.use == 3:
            self.squaresGroup.empty()
            if self.state == 4:
                #Add purple squares to units
                self.get_purple_squares()
                #Update message
                text = self.currentTurn.name + " can move individual models or confirm the unit's position"
                self.update_main_message(values, text)
                self.state = 3
            else:
                self.delete_unit_from_field(self.currentUnit)
                self.currentUnit = None
                #Update message
                text = self.currentTurn.name + " is deploying a unit"
                self.update_main_message(values, text)
                self.state = 0
                self.awaitingEvent = False
                
        #Player who completed deploying first, chooses to go first
        elif button.use == 4:
            #Advance phase and turn
            self.turn = [1, 0]
            self.phase = 1
            
            #Update header
            self.set_up_header_display(values)
            
            #Announce in event log
            text = self.currentTurn.name + " chooses to go first."
            self.update_event_log(values, text)
            
            text = self.currentTurn.name + " begins their movement phase."
            self.update_event_log(values, text)
            
            #Set state to 7
            self.state = 7
            self.awaitingEvent = False
            
        #Player who completed deploying first, chooses to go second
        elif button.use == 5:
            #Advance phase and turn
            self.turn = [1, 0]
            self.phase = 1
            
            #Update header
            self.set_up_header_display(values)
            
            #Announce in event log
            text = self.currentTurn.name + " chooses to go second."
            self.update_event_log(values, text)
            
            #Set other player to current turn
            if self.currentTurn == self.players[0]:
                self.currentTurn = self.players[1]
                self.otherTurn = self.players[0]
            else:
                self.currentTurn = self.players[0]
                self.otherTurn = self.players[1]
                
            text = self.currentTurn.name + " begins their movement phase."
            self.update_event_log(values, text)
            
            #Set state to 7
            self.state = 7
            self.awaitingEvent = False
            
        #Clicking move, advance or fall back during the movement phase
        elif button.use in range(6, 9):
            #Turn move, advance or fall back to true
            if button.use == 6:
                self.currentUnit.moved = True
                self.currentUnit.advanced = False
                self.currentUnit.fellBack = False
            elif button.use == 7:
                self.currentUnit.advanced = True
                self.currentUnit.moved = False
                self.currentUnit.fellBack = False
            elif button.use == 8:
                self.currentUnit.fellBack = True
                self.currentUnit.moved = False
                self.currentUnit.advanced = False
            #Set state to 10 and awaiting event to false
            self.state = 10
            self.awaitingEvent = False
            
        #Cancel from selecting a unit in the movement phase
        elif button.use == 9:
            #Clear purple squares
            self.squaresGroup.empty()
            
            #Set current unit to none
            self.currentUnit = None
            
            #Set state to 8 and awaiting event to false
            self.state = 8
            self.awaitingEvent = False
            
        #Move in formation
        elif button.use == 10:
            self.moveFormation = True
            self.moveToPoint = False
            self.moveModels = False
            #Set state to 11 and awaiting event to false
            self.state = 11
            self.awaitingEvent = False
            
        #Move to point
        elif button.use == 11:
            self.moveFormation = False
            self.moveToPoint = True
            self.moveModels = False
            #Set state to 11 and awaiting event to false
            self.state = 11
            self.awaitingEvent = False
            
        #Move by model
        elif button.use == 12:
            self.moveFormation = False
            self.moveToPoint = False
            self.moveModels = True
            #Set state to 11 and awaiting event to false
            self.state = 11
            self.awaitingEvent = False
            
        #Back button on movement options
        elif button.use == 13:
            if self.phase == 1:
                self.currentUnit.moved = False
                self.currentUnit.advanced = False
                self.currentUnit.fellBack = False
                
                self.state = 9
            elif self.phase == 4:
                text = (self.currentUnit.name + " has cancelled their charge against " + 
                        self.units[self.currentUnit.chargedUnit].name + "!")
                self.update_event_log(values, text)
                
                self.currentUnit.chargedUnit = None
                self.currentUnit.endPhase = True
                self.currentUnit = None
                self.squaresGroup.empty()
                
                self.state = 34
            elif self.phase == 5:
                self.currentUnit = None
                self.squaresGroup.empty()
                self.state = 42
            self.awaitingEvent = False
            
        #Confirm unit movement during movement phase
        elif button.use == 14:
            self.state = 13
            self.awaitingEvent = False
            
        #Reset when moving units
        elif button.use == 15:
            if self.currentUnit.ID in self.currentTurn.units:
                self.reset_unit_movement(self.currentUnit, self.currentTurn)
            else:
                self.reset_unit_movement(self.currentUnit, self.otherTurn)
            #Reset squares
            self.get_purple_squares()
            self.update_main_message(values, "Click on models to move them. Confirm when ready.")
            #Set state to 11
            self.currentModel = None
            self.state = 11
            
        #Cancel when moving units
        elif button.use == 16:
            if self.currentUnit.ID in self.currentTurn.units:
                self.reset_unit_movement(self.currentUnit, self.currentTurn)
            else:
                self.reset_unit_movement(self.currentUnit, self.otherTurn)
            #Reset squares
            self.squaresGroup.empty()
            
            #Set state
            if self.phase == 1:
                #Reset movement flags
                self.currentUnit.moved = False
                self.currentUnit.advanced = False
                self.currentUnit.fellBack = False
                self.currentModel = None
                self.currentUnit = None
                self.state = 8
            elif self.phase == 4:
                self.get_purple_squares()
                self.state = 10
            elif self.phase == 5:
                self.currentModel = None
                self.currentUnit = None
                self.state = 42
            elif self.phase == 6:
                if self.pileIn:
                    self.currentModel = None
                    self.currentUnit = None
                    self.state = 45
                else:
                    self.currentModel = None
                    self.state = 11
            self.awaitingEvent = False
            
        #End phase button during movement phase
        elif button.use == 17:
            self.state = 14
            self.awaitingEvent = False
            
        #Choosing to end the movement phase
        elif button.use == 18:
            
            #Loop through current player's units
            for unit in self.currentTurn.units:
                #If not moved
                if (not self.units[unit].moved and not self.units[unit].advanced and 
                    not self.units[unit].fellBack):
                    #If unit has a minimum movement characteristic
                    if self.units[unit].models[0].minMove > 0:
                        #destroy unit
                        self.units[unit].destroyed = True
                        for model in self.units[unit].models:
                            model.dead = True
                        self.delete_unit_from_field(self.units[unit])
                        #Report destroyed units
                        text = self.units[unit].name + " crashed and burned!"
                        self.update_event_log(values, text)
                        self.check_kill_points(values, self.units[unit])  
                        self.checkingExplosions = True            
                
            self.phase = 2
            
            self.set_up_header_display(values)
            text = self.currentTurn.name + " begins their magic phase."
            self.update_event_log(values, text)
            
            self.state = 15
            self.awaitingEvent = False
            
        #Choosing not to end the movement phase
        elif button.use == 19:
            self.state = 8
            self.awaitingEvent = False
            
        #Selecting a spell in the magic phase
        elif button.use == 20:
            if button.storage.use1 == 0:
                #User must select a target
                self.selectedModels = []
                for model in self.currentUnit.models:
                    self.selectedModels.append(model)
                self.get_closest_visible_unit()
                self.currentSpell = button.storage
                self.state = 18
                self.awaitingEvent = False
            
        #Cancelling after selecting a mage in the magic phase
        elif button.use == 21:
            self.currentUnit = None
            self.squaresGroup.empty()
            self.state = 16
            self.awaitingEvent = False
            
        #Cancelling a spell selection
        elif button.use == 22:
            self.currentSpell = None
            self.state = 17
            self.awaitingEvent = False
            
        #Confirm spell target
        elif button.use == 23:
            text = self.currentUnit.name + " attempts to cast " + self.currentSpell.name + "..."
            self.update_event_log(values, text)
            self.state = 20
            self.awaitingEvent = False
            
        #Cancelling a target selection during magic phase
        elif button.use == 24:
            self.currentUnit.targetUnit = None
            self.currentUnit.spellTargets = []
            self.state = 18
            self.awaitingEvent = False
            
        #Choosing to dispel 
        elif button.use == 25:
            self.state = 21
            self.awaitingEvent = False
            
        elif button.use == 26:
            self.state = 22
            self.awaitingEvent = False
            
        #Confirm mage for dispelling
        elif button.use == 27:
            if self.otherUnit != None:
                #Subract mana from dispeller
                self.otherUnit.currentMana = self.otherUnit.currentMana - math.floor(self.otherUnit.dispelRate * 
                                                                                     self.currentSpell.mana)
                #Mark dispeller as having completed the phase
                self.otherUnit.endPhase = True
                
                #Store spell ID as casted
                self.currentTurn.spellsUsed.append(self.currentSpell.ID)
                
                #Update event log
                text = (self.otherUnit.name + " dispels " + self.currentUnit.name + "'s " + 
                        self.currentSpell.name + " spell!")
                self.update_event_log(values, text)
                
                #other unit and current spell to none
                self.otherUnit = None
                self.currentSpell = None
                self.currentUnit.spellTargets = []
                
                #Clear squares
                self.squaresGroup.empty()
                #State to 17 and await event to false
                self.state = 17
                self.awaitingEvent = False
            
        #Cancel button when dispelling
        elif button.use == 28:
            if self.otherUnit == None:
                self.state = 22
                self.awaitingEvent = False
            else:
                self.otherUnit = None
                self.squaresGroup.empty()
                self.update_main_message(values, "Select a mage to dispel with. Press 'confirm' when ready", 
                                     otherPlayer=True)
                
        #End phase button during the magic phase
        elif button.use == 29:
            self.state = 23
            self.awaitingEvent = False
            
        #Choosing to end the magic phase
        elif button.use == 30:
            self.phase = 3
            
            self.set_up_header_display(values)
            text = self.currentTurn.name + " begins their shooting phase."
            self.update_event_log(values, text)
            
            self.state = 24
            self.awaitingEvent = False
            
        #Choosing not to end the magic phase
        elif button.use == 31:
            self.state = 16
            self.awaitingEvent = False
            
        #Selecting a weapon to fire in the shooting phase
        elif button.use == 32:
            self.currentWeapon = button.storage
            owned = 0
            ownedBy = None
            
            if self.phase == 3:
                currentUnit = self.currentUnit
            elif self.phase == 4:
                currentUnit = self.currentUnit.targetUnit
            
            for model in currentUnit.models:
                for w in model.wargear:
                    if w == button.storage.ID[1]:
                        owned += 1
                        ownedBy = model
                        break
            #If weapon is owned by more than one model
            if owned > 1:
                if button.storage.gearType == 4:
                    self.state = 28
                else:
                    self.state = 27
                self.awaitingEvent = False
            else:
                self.selectedModels = [ownedBy]
                #Update purple squares
                self.get_purple_squares(highlightUnit=False, highlightSelected=True)
                if self.phase == 3:
                    self.get_closest_visible_unit()
                    self.state = 29
                elif self.phase == 4:
                    self.state = 38
                self.awaitingEvent = False
            
            
        #Cancelling selecting a unit to shoot with in the shooting phase
        elif button.use == 33:
            if self.phase == 3:
                self.squaresGroup.empty()
                self.currentUnit = None
                self.state = 25
            elif self.phase == 4:
                if not self.currentUnit.destroyed:
                    self.get_purple_squares()
                    self.state = 39
                else:
                    text = self.currentUnit.name + " is destroyed and cannot charge!."
                    self.update_event_log(values, text)
                    self.currentUnit = None
                    self.state = 34
            self.awaitingEvent = False
            
        #Choosing to fire will all available models in the shooting phase
        elif button.use == 34:
            self.selectedModels = []
            if self.phase == 3:
                currentUnit = self.currentUnit
            elif self.phase == 4:
                currentUnit = self.currentUnit.targetUnit
            for model in currentUnit.models:
                #Does model have the current weapon?
                success = False
                for w in model.wargear:
                    if w == self.currentWeapon.ID[1]:
                        success = True
                        break
                #Has this weapon been fired already?
                if self.currentWeapon.ID in model.weaponsFired:
                    success = False
                #Is this model allowed to use this type of weapon?
                if self.currentWeapon.gearType in range(1, 4) and (model.pistolsUsed or model.grenadesUsed):
                    success = False
                elif self.currentWeapon.gearType == 5 and (model.otherWeaponsUsed or model.grenadesUsed):
                    success = False
                if success:
                    self.selectedModels.append(model)
            #Update purple squares
            self.get_purple_squares(highlightUnit=False, highlightSelected=True)
            if self.phase == 3:
                self.get_closest_visible_unit()
                self.state = 29
            else:
                self.state = 38
            self.awaitingEvent = False
            
        #Choosing to select models to fire with in the shooting phase
        elif button.use == 36:
            self.state = 28
            self.awaitingEvent = False
            
        #Cancelling selecting a weapon in the shooting phase
        elif button.use == 37:
            self.currentWeapon = None
            self.state = 26
            self.awaitingEvent = False
            
        #Confirming which models will fire
        elif button.use == 38:
            if len(self.selectedModels) > 0:
                
                if self.phase == 3:
                    self.get_closest_visible_unit()
                
                    self.state = 29
                elif self.phase == 4:
                    self.state = 38
                self.awaitingEvent = False

        #Reset model selection during shooting phase
        elif button.use == 39:
            self.selectedModels = []
            self.get_purple_squares(highlightUnit=False, highlightSelected=True)
           
        #Backing out of model selection during shooting phase or selecting a target
        elif button.use in range(40, 42):
            self.selectedModels = []
            if self.phase == 3:
                self.get_purple_squares()
            elif self.phase == 4:
                self.get_purple_squares(highlightUnit=False, highlightTarget=True)
            self.state = 26
            self.awaitingEvent = False
            
        #Confirming to shoot target in the shooting phase
        elif button.use == 42:
            self.state = 31
            self.awaitingEvent = False
            
        #Cancel targeting a unit in the shooting phase
        elif button.use == 43:
            self.flagsGroup.empty()
            self.get_purple_squares(highlightUnit=False, highlightSelected=True)
            self.state = 29
            self.awaitingEvent = False
            
        #End phase button in the shooting phase
        elif button.use == 44:
            self.state = 32
            self.awaitingEvent = False
            
        #Choosing to end the shooting phase
        elif button.use == 45:
            self.phase = 4
            
            self.set_up_header_display(values)
            text = self.currentTurn.name + " begins their charge phase."
            self.update_event_log(values, text)
            
            self.state = 33
            self.awaitingEvent = False
            
        #Choosing not to end the shooting phase
        elif button.use == 46:
            self.state = 25
            self.awaitingEvent = False
            
        #Backing out of selecting a unit to charge with
        elif button.use == 47:
            self.currentUnit = None
            self.squaresGroup.empty()
            self.state = 34
            self.awaitingEvent = False
            
        #Confirming charge target
        elif button.use == 48:
            text = self.currentUnit.name + " declares a charge against " + self.currentUnit.targetUnit.name + "!"
            self.update_event_log(values, text)
            #If unit can overwatch, ask for confirmation
            if not self.currentUnit.targetUnit.endPhase:
                self.state = 37
            else:
                self.state = 39
            self.awaitingEvent = False
            
        #Cancelling after selecting a target to charge
        elif button.use == 49:
            self.currentUnit.targetUnit = None
            self.state = 35
            self.awaitingEvent = False
            
        #Choosing to fire overwatch
        elif button.use == 50:
            
            #Reset shooting flags
            self.currentUnit.targetUnit.thrownGrenade = False
            for model in self.currentUnit.targetUnit.models:
                model.weaponsFired = []
                model.grenadesUsed = False
                model.otherWeaponsUsed = False
                model.pistolsUsed = False
            
            self.state = 26
            self.awaitingEvent = False
            
        #Choosing not to fire overwatch
        elif button.use == 51:
            self.state = 39
            self.awaitingEvent = False
            
        #End phase button in the charge phase
        elif button.use == 52:
            self.state = 40
            self.awaitingEvent = False
            
        #Choosing to end the charge phase
        elif button.use == 53:
            self.phase = 5
            
            text = self.otherTurn.name + " has the option to intervene in melee with their CHARACTER units."
            self.update_event_log(values, text)
            
            self.state = 41
            self.awaitingEvent = False
            
        #Choosing not to end the charge phase
        elif button.use == 54:
            self.state = 34
            self.awaitingEvent = False
            
        #End phase button during intervention
        elif button.use == 55:
            self.state = 43
            self.awaitingEvent = False
            
        #Choosing to end the intervention phase
        elif button.use == 56:
            self.phase = 6
            
            self.set_up_header_display(values)
            text = self.currentTurn.name + " begins their melee phase."
            self.update_event_log(values, text)
            
            self.state = 44
            self.awaitingEvent = False
            
        #Choosing not to end the charge phase
        elif button.use == 57:
            self.state = 42
            self.awaitingEvent = False
            
        #Selecting a unit to attack with during the melee phase
        elif button.use == 58:
            #Set selected as current unit
            self.currentUnit = button.storage
            self.get_purple_squares()
            
            self.moveFormation = False
            self.moveToPoint = False
            self.moveModels = True
            #Set state to 11
            self.state = 11
            self.awaitingEvent = False
            
        #Selecting a weapon to attack with in the melee phase
        elif button.use == 59:
            self.currentWeapon = button.storage
            owned = 0
            ownedBy = None
            
            for model in self.currentUnit.models:
                for w in model.wargear:
                    if w == button.storage.ID[1]:
                        owned += 1
                        ownedBy = model
                        break
            #If weapon is owned by more than one model
            if owned > 1:
                self.state = 47
                self.awaitingEvent = False
            else:
                self.selectedModels = [ownedBy]
                #Update purple squares
                self.get_purple_squares(highlightUnit=False, highlightSelected=True)
                self.attack_charge_target(values)
                
        #Choosing to attack with all available models in the melee phase
        elif button.use == 60:
            self.selectedModels = []
            for model in self.currentUnit.models:
                #Does model have the current weapon?
                success = False
                for w in model.wargear:
                    if w == self.currentWeapon.ID[1]:
                        success = True
                        break
                #Has this model attacked already?
                if model.meleeUsed:
                    success = False
                if success:
                    self.selectedModels.append(model)
            #Update purple squares
            self.get_purple_squares(highlightUnit=False, highlightSelected=True)
            self.attack_charge_target(values)
                
        #Choosing to attack with individual models in the melee phase
        elif button.use == 62:
            self.state = 48
            self.awaitingEvent = False
                
        #Back out of weapon selection in the melee phase
        elif button.use == 63:
            self.currentWeapon = None
            self.state = 46
            self.awaitingEvent = False
            
        #Confirming which models will attack in melee
        elif button.use == 64:
            self.attack_charge_target(values)
            
        #Reset model selection during melee phase
        elif button.use == 65:
            self.selectedModels = []
            self.get_purple_squares(highlightUnit=False, highlightSelected=True)
            
        #Backing out of attacking with models individually in the melee phase
        elif button.use in range(66, 68):
            self.selectedModels = []
            self.get_purple_squares()
            self.state = 46
            self.awaitingEvent = False
            
        #Confirming to attack target in the melee phase
        elif button.use == 68:
            self.state = 51
            self.awaitingEvent = False
            
        #Cancel targeting a unit in the melee phase
        elif button.use == 69:
            self.flagsGroup.empty()
            self.get_purple_squares(highlightUnit=False, highlightSelected=True)
            self.state = 49
            self.awaitingEvent = False
            
        #Ending the attack section of the melee phase
        elif button.use == 70:
            self.pileIn = False
            
            self.get_purple_squares()
            
            self.moveFormation = False
            self.moveToPoint = False
            self.moveModels = True
            #Set state to 11
            self.state = 11
            self.awaitingEvent = False
            
        #Starting the morale checks
        elif button.use == 71:
            self.state = 53
            self.awaitingEvent = False
            
        #End morale phase
        elif button.use == 72:
            #Advance turn order
            #If not final turn, swap players
            if self.turn == [5, 5]:
                self.state = 54
                self.awaitingEvent = False
            else:
                if self.turn[0] == self.turn[1]:
                    turn = self.turn[0]
                    self.turn[0] += 1
                    newTurn = self.turn[0]
                else:
                    turn = self.turn[1]
                    self.turn[1] += 1
                    newTurn = self.turn[1]
                #Announce in event log
                text = self.currentTurn.name + "'s turn " + str(turn) + " ends."
                self.update_event_log(values, text)
                
                otherTurn = self.currentTurn
                self.currentTurn = self.otherTurn
                self.otherTurn = otherTurn
                
                text = self.currentTurn.name + "'s turn " + str(newTurn) + " begins."
                self.update_event_log(values, text)
                text = self.currentTurn.name + " begins their movement phase."
                self.update_event_log(values, text)
                
                #Head back to the movement phase
                self.phase = 1
        
                #Update header
                self.set_up_header_display(values)
                
                #Set state to 7
                self.state = 7
                self.awaitingEvent = False
                
        #End game, proceed to score screen
        elif button.use == 73:
            values.state = 0
            
        #Embark button
        elif button.use == 74:
            #Advance the current state
            self.state = 58
            self.awaitingEvent = False
            
        #Back button when choose a transport to embark onto
        elif button.use == 75:
            #Loop through models and see if any have already moved.
            alreadyMoved = False
            for model in self.currentUnit.models:
                if len(model.oldNodes) != 0:
                    alreadyMoved = True
                    break
            #If they have, back into state 11
            if alreadyMoved:
                self.state = 11
            #Else, back into state 9
            else:
                self.state = 9
            self.awaitingEvent = False
            
        #Confirm button when embarking on a transport in the movement phase
        elif button.use == 76:
            text = self.embark_on_transport(values)
            self.update_event_log(values, text)
            self.state = 8
            self.awaitingEvent = False
            
        #Back button when confirming whether or not to embark on a transport
        elif button.use == 77:
            self.currentTransport = None
            self.state = 58
            self.awaitingEvent = False
            
        #Disembark button
        elif button.use == 78:
            self.state = 60
            self.awaitingEvent = False
            
        #Select unit for disembarking
        elif button.use == 79:
            self.commandListCounter = 0
            self.currentTransport = self.currentUnit
            self.currentUnit = button.storage
            self.state = 61
            self.awaitingEvent = False
            
        #Backing out of disembarking
        elif button.use == 80:
            self.commandListCounter = 0
            
            alreadyMoved = False
            for model in self.currentUnit.models:
                if len(model.oldNodes) != 0:
                    alreadyMoved = True
                    break
            #If they have, back into state 11
            if alreadyMoved:
                self.state = 11
            #Else, back into state 9
            else:
                self.state = 9
                
            self.awaitingEvent = False
            
    def handle_charge(self, values):
        
        #Set up
        if self.state == 33:
            #Loop through units
            for unit in self.units:
                if unit in self.currentTurn.units:
                    #Mark current player units as having completed the phase if they have advanced,
                    #fallen back, in melee, or have the airborne keyword
                    if (self.units[unit].advanced or self.units[unit].fellBack or self.units[unit].inMelee or 
                        'AIRBORNE' in self.units[unit].models[0].keywords):
                        self.units[unit].endPhase = True
                    else:
                        self.units[unit].endPhase = False
                else:
                    #Mark enemy units as having completed the phase if they are in melee or
                    #do not have range weapons
                    endPhase = False
                    if self.units[unit].inMelee:
                        endPhase = True
                    if not endPhase:
                        ranged = False
                        if self.currentTurn == self.players[0]:
                            otherPlayer = self.players[1]
                        else:
                            otherPlayer = self.players[0]
                        for model in self.units[unit].models:
                            if not model.dead:
                                for w in model.wargear:
                                    wargear = otherPlayer.playerArmy.codex.wargear[(
                                        otherPlayer.playerArmy.faction, w)]
                                    if wargear.gearType in range(1, 6):
                                        ranged = True
                                        break
                                if ranged:
                                    break
                        if not ranged:
                            endPhase = True
                            
                    self.units[unit].endPhase = endPhase
                    
            self.state = 34
            
        #Initial state
        if self.state == 34:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["End Phase"], actionList=[52])
            
            self.update_main_message(values, "Please select a unit to charge with")
            
            self.awaitingEvent = True
            
        #Charging unit selected
        elif self.state == 35:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Cancel"], actionList=[47])
            
            self.update_main_message(values, "Select a target to charge")
            
            self.awaitingEvent = True
            
        #Charging target selected
        elif self.state == 36:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Cancel"], actionList=[48, 49])
            
            text = "Are you sure you want to charge " + self.currentUnit.targetUnit.name + "?"
            self.update_main_message(values, text)
            
            self.awaitingEvent = True
            
        #Other player chooses whether or not to overwatch
        elif self.state == 37:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Yes", "No"], actionList=[50, 51])
            
            self.update_main_message(values, "Would you like to fire overwatch?", otherPlayer=True)
            
            self.awaitingEvent = True
            
        #Set up current unit as target for overwatch
        elif self.state == 38:
            self.attackingModels = []
            for model in self.selectedModels:
                model.attackTargets = []
                if not model.dead:
                    #Get list of target nodes
                    for m in self.currentUnit.models:
                        for node in m.nodes:
                            model.attackTargets.append(node)
                    self.attackingModels.append(model)
                
            #Set up target sprites
            self.currentUnit.targetUnit.targetUnit = self.currentUnit
            self.state = 31
            self.awaitingEvent = False
            
        #Making the charge move
        elif self.state == 39:
            self.currentUnit.chargedUnit = self.currentUnit.targetUnit.ID
            self.currentUnit.chargeRange = 7 + math.ceil(self.randomNumbers.pop(0)/2)
            self.state = 10
            
        #Pressing the end phase button
        elif self.state == 40:
            #Clear buttons
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Set up confirmation buttons
            commands = ["Yes", "No"]
            self.get_command_list(values, commands, actionList=[53, 54])
            
            self.update_main_message(values, "Are you sure you want to end the phase?")
            self.awaitingEvent = True
            
        #Set up for character intervention
        elif self.state == 41:
            #Loop through units
            for unit in self.units:
                #If unit is owned by the other player, is a character, and is not in melee, then it can move
                if unit in self.otherTurn.units:
                    if "CHARACTER" in self.units[unit].models[0].keywords:
                        if not self.units[unit].inMelee:
                            self.units[unit].endPhase = False
                            #Else, end turn
                        else:
                            self.units[unit].endPhase = True
                    else:
                        self.units[unit].endPhase = True
                else:
                    self.units[unit].endPhase = True
            
            self.state = 42
            
        if self.state == 42:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["End Intervention"], actionList=[55])
            
            self.update_main_message(values, "Please select a CHARACTER to move", otherPlayer=True)
            
            self.awaitingEvent = True
            
        #Pressing the end invention button
        elif self.state == 43:
            #Clear buttons
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Set up confirmation buttons
            commands = ["Yes", "No"]
            self.get_command_list(values, commands, actionList=[56, 57])
            
            self.update_main_message(values, "Are you sure you want to end the intervention?", otherPlayer=True)
            self.awaitingEvent = True
    
    def handle_deployment(self, values):
        
        spr = []
        
        if self.state == 0:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            #Inform players who's turn it is
            text = self.currentTurn.name + " is deploying a unit"
            self.update_main_message(values, text)
            #Move camera to player's deployment zone
            if self.deploymentMap == 0:
                if self.currentTurn.deploymentZone == 1:
                    self.xOffset = 0
                else:
                    self.xOffset = self.xOffsetMax
                self.yOffset = int(self.yOffsetMax/2)
            self.camera = self.surface.subsurface(self.xOffset, self.yOffset, 1280, 720)
            
            #Create a list of the units the player has yet to deploy
            units = []
            for unit in self.unitsToDeploy:
                if unit in self.currentTurn.units:
                    units.append(unit)
            
            #Set up command buttons 
            self.get_command_list(values, units)
            
            #Update state and turn input on
            self.state = 1
            self.awaitingEvent = True
            
        #Player has selected a unit to deploy
        elif self.state == 2:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            #Inform player
            text = "Select where to deploy " + self.currentUnit.name + "."
            self.update_main_message(values, text)
            #set up buttons for confirm, reset and cancel
            
            commands = ["Confirm", "Cancel"]
            self.get_command_list(values, commands, actionList=[2, 3])
            self.awaitingEvent = True
            
        if self.state == 3:
            #Check that the current unit for coherency
            #If player is deploying a unit in a transport, ignore the coherency check
            if self.currentTransport == None:
                coherent = self.check_unit_coherency(self.currentUnit)
            else:
                coherent = True
            #If it passes, remove unit ID from deploy list
            if coherent:
                #If deployment is in a transport, announce this approprately
                #Set current transport back to none
                if self.currentTransport == None:
                    text = self.currentTurn.name + " deploys " + self.currentUnit.name
                else:
                    """
                    self.currentTransport.onboard.append(self.currentUnit.ID)
                    text = self.currentTurn.name + " deploys " + self.currentUnit.name + " inside of " + self.currentTransport.name
                    self.currentTransport = None
                    """
                    text = self.embark_on_transport(values)
                self.update_event_log(values, text)
                self.unitsToDeploy.remove(self.currentUnit.ID)
                self.squaresGroup.empty()
                #Check if deployment list is empty
                if len(self.unitsToDeploy) == 0:
                    #If so, end deployment
                    self.update_control_point_status(values)
                    print("DEPLOYMENT PHASE OVER")
                    self.awaitingEvent = False
                    self.state = 5
                else:
                    #If not, check that both players can still deploy
                    player1 = False
                    player2 = False
                    for unit in self.unitsToDeploy:
                        if unit in self.players[0].units:
                            player1 = True
                        elif unit in self.players[1].units:
                            player2 = True
                        if player1 and player2:
                            break
                    #If so, give current turn to the other player
                    if player1 and player2:
                        if self.currentTurn == self.players[0]:
                            self.currentTurn = self.players[1]
                            self.otherTurn = self.players[0]
                        else:
                            self.currentTurn = self.players[0]
                            self.otherTurn = self.players[1]
                    #Else, mark one player as having finished deployment and set current turn to the other
                    else:
                        if not self.announcedFirstToFinish:
                            self.announcedFirstToFinish = True
                            text = self.currentTurn.name + " finishes deploying first."
                            self.update_event_log(values, text)
                        if player1:
                            self.players[1].finishedDeployment = True
                            self.currentTurn = self.players[0]
                            self.otherTurn = self.players[1]
                        else:
                            self.players[0].finishedDeployment = True
                            self.currentTurn = self.players[1]
                            self.otherTurn = self.players[0]
                    if self.highlighting:
                        self.toggle_highlighting()
                    self.currentUnit = None                 
                    self.awaitingEvent = False
                    self.state = 0
                    
            else:
                text = "Cannot confirm: Models within unit must be closer together"
                self.update_main_message(values, text)
                self.awaitingEvent = True
         
        #Player who finished deployment first can opt to go first or second   
        elif self.state == 5:
            #Set player who deployed first as current turn
            if self.players[0].finishedDeployment:
                self.currentTurn = self.players[0]
                self.otherTurn = self.players[1]
            else:
                self.currentTurn = self.players[1]
                self.otherTurn = self.players[0]
            #Create buttons for first turn or second turn
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            commands = ["First turn", "Second turn"]
            self.get_command_list(values, commands, actionList=[4, 5])
            #Update event log and main message
            text = "Select whether to take the 1st or 2nd turn."
            self.update_main_message(values, text)
            text = self.currentTurn.name + " is choosing whether to go first or second."
            self.update_event_log(values, text)
            #Set state to 6
            self.awaitingEvent = True
            self.state = 6
            
        self.commandListGroup.add(spr)
        
    def handle_endgame(self, values):
        
        #End game due to final round complete
        if self.state == 54:
            
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Inform player
            self.update_main_message(values, "Game over!")
            self.get_command_list(values, ["Score screen"], actionList=[73])
            
            self.check_engame_points(values)
            
            #Compare scores
            draw = False
            if self.players[0].vp > self.players[1].vp:
                winner = self.players[0]
                loser = self.players[1]
            elif self.players[0].vp < self.players[1].vp:
                winner = self.players[1]
                loser = self.players[0]
            else:
                self.update_event_log(values, "Game over! The game ends in a draw!")
                draw = True
                
            #Assign minor or major victory
            if not draw:
                if winner.vp >= (loser.vp * 2):
                    victory = " major "
                else:
                    victory = " minor "
                    
                text = "Game over! " + winner.name + " wins a" + victory + "victory over " + loser.name + "!"
                self.update_event_log(values, text)
                
            self.awaitingEvent = True
            
        #End game due to an army wipe out
        elif self.state == 55:
            
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Inform player
            self.update_main_message(values, "Game over!")
            self.get_command_list(values, ["Score screen"], actionList=[73])
            
            if self.players[0].armyWiped and self.players[1].armyWiped:
                text = "Game over! The game ends in a draw as both armies have been wiped out!"
                self.update_event_log(values, text)
            else:
                if self.players[0].armyWiped:
                    winner = self.players[1]
                    loser = self.players[0]
                else:
                    winner = self.players[0]
                    loser = self.players[1]
                    
                text = loser.name + "'s entire army has been wiped out!"
                self.update_event_log(values, text)
                text = "Game over! " + winner.name + " wins a major victory over " + loser.name + "!" 
                self.update_event_log(values, text)
                
            self.awaitingEvent = True
            
        #End game due to a concession
        elif self.state == 56:
            
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Inform player
            self.update_main_message(values, "Game over!")
            self.get_command_list(values, ["Score screen"], actionList=[73])
            
            text = self.currentTurn.name + " has conceded defeat!"
            self.update_event_log(values, text)
            text = ("Game over! " + self.otherTurn.name + " wins a major victory over " + self.currentTurn.name 
                    + "!")
            self.update_event_log(values, text)
        
            self.awaitingEvent = True
        
    def handle_magic(self, values):
        
        #Set up
        if self.state == 15:
            
            #Clear spells used
            self.currentTurn.spellsUsed = []
            
            #Loop through all units
            for unit in self.units:
                #Flag non-mages as having completed the phase
                if self.units[unit].currentMana == None:
                    self.units[unit].endPhase = True
                else:
                    self.units[unit].endPhase = False
                    
            #Move camera to player's deployment zone
            """
            if self.deploymentMap == 0:
                if self.currentTurn.deploymentZone == 1:
                    self.xOffset = 0
                else:
                    self.xOffset = self.xOffsetMax
                self.yOffset = int(self.yOffsetMax/2)
            self.camera = self.surface.subsurface(self.xOffset, self.yOffset, 1280, 720)
            """
                    
            #Set state to 16
            self.state = 16
            
        #Player to select a mage
        if self.state == 16:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["End Phase"], actionList=[29])
            
            self.update_main_message(values, "Please select a mage unit")
            
            self.awaitingEvent = True
            
        #Display spells for selected mage
        elif self.state == 17:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Create a list of spells which haven't been used yet, and there is enough mana for
            spells = []
            for spell in self.currentUnit.spells:
                if spell not in self.currentTurn.spellsUsed:
                    s = self.currentTurn.playerArmy.codex.spells[spell]
                    if self.currentUnit.currentMana >= s.mana:
                        spells.append(s)
                    
            #Add "Cancel" to the list
            spells.append("Cancel")
            
            #Get command list
            self.get_command_list(values, spells)
            
            #Update message
            self.update_main_message(values, "Please select a spell")
            #Turn awaiting event on
            self.awaitingEvent = True
            
        #Player has selected a spell
        elif self.state == 18:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Back"], actionList=[22])
            
            #Update message
            text = "Please select a target for " + self.currentSpell.name
            self.update_main_message(values, text)
            #Turn awaiting event on
            self.awaitingEvent = True
            
        #Player to confirm target of spell
        elif self.state == 19:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Cancel"], actionList=[23, 24])
            
            #Update message
            text = "Are you sure you want to target " + self.currentUnit.targetUnit.name + "?"
            self.update_main_message(values, text)
            #Turn awaiting event on
            self.awaitingEvent = True
            
        #Target confirmed, see if dispel is possible
        elif self.state == 20:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Subract mana from caster
            self.currentUnit.currentMana -= self.currentSpell.mana
            
            #Loop through enemy units and see if any have yet to end their phase
            if self.currentTurn == self.players[0]:
                otherTurn = self.players[1]
            else:
                otherTurn = self.players[0]
                
            canDispel = False
            for u in otherTurn.units:
                if not self.units[u].endPhase:
                    #See if unit is in range
                    keepLooking = False
                    for model in self.units[u].models:
                        if not model.dead:
                            targets = self.get_nodes_in_range(model, self.currentUnit, 24)
                            if len(targets) > 0:
                                keepLooking = True
                                break
                    
                    #Check spell level
                    if keepLooking:
                        if self.currentSpell.level > self.units[u].dispelLevel:
                            keepLooking = False
                        
                    #Check mana   
                    if keepLooking:
                        if self.units[u].currentMana >= math.floor(
                            self.currentSpell.mana * self.units[u].dispelRate):
                            canDispel = True
                            break
            
            if canDispel:
            
                #If so, ask other player if they would like to dispel
                self.get_command_list(values, ["Yes", "No"], actionList=[25, 26])
                
                #Update message
                text = "Would you like to dispel " + self.currentTurn.name + "'s spell?"
                self.update_main_message(values, text, otherPlayer=True)
                #Turn awaiting event on
                self.awaitingEvent = True
                
            else:
                self.state = 22
                
        #Other player opts to dispel 
        elif self.state == 21:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Cancel"], actionList=[27, 28])
            
            self.update_main_message(values, "Select a mage to dispel with. Press 'confirm' when ready", 
                                     otherPlayer=True)
            
            self.squaresGroup.empty()
            
            #Turn awaiting event on
            self.awaitingEvent = True
            
        #cast spell
        elif self.state == 22:
            #If spell is a damaging spell
            if self.currentSpell.use1 == 0:
                targets = []
                #Loop through nodes in targets
                for node in self.currentUnit.spellTargets:
                    #Get distance between node and mage unit
                    distance = 9999
                    for model in self.currentUnit.models:
                        if not model.dead:
                            for node2 in model.nodes:
                                d = self.get_distance_between_nodes(node, node2)
                                if d < distance:
                                    distance = d
                    #Add model standing on node if it hasn't been added already
                    if self.models[self.nodes[node].takenBy] not in targets:
                        self.models[self.nodes[node].takenBy].H = distance
                        targets.append(self.models[self.nodes[node].takenBy])
                    #If it has, see if this node is closer and update H value
                    else:
                        if distance < self.models[self.nodes[node].takenBy].H:
                            self.models[self.nodes[node].takenBy].H = distance
                #Sort list by H
                targets.sort(key=operator.attrgetter("H"))
                #Pop front of list and save it as target
                target = targets.pop(0)
                attacks = []
                #create an attack object for each point of damage
                for i in range(0, self.currentSpell.damage):
                    attacks.append(Attack(99, 99, 1, 99, target, targets))
                if self.currentTurn == self.players[0]:
                    otherTurn = self.players[1]
                else:
                    otherTurn = self.players[0]
                targetCodex = otherTurn.playerArmy.codex
                #Apply damage
                self.apply_damage(values, attacks, targetCodex, self.currentSpell)
                #Add spell to used list
                self.currentTurn.spellsUsed.append(self.currentSpell.ID)
                
                self.state = 17
                self.currentSpell = None
                self.currentUnit.spellTargets = []
                
        #Pressing the end phase button
        elif self.state == 23:
            #Clear buttons
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Set up confirmation buttons
            commands = ["Yes", "No"]
            self.get_command_list(values, commands, actionList=[30, 31])
            
            self.update_main_message(values, "Are you sure you want to end the phase?")
            self.awaitingEvent = True
            
    def handle_melee(self, values):
        
        if self.state == 44:
            #Loop through units
            for unit in self.units:
                self.units[unit].endPhase = False
                #If unit is in melee, add it to melee lists
                if self.units[unit].inMelee:
                    
                    #Assign to list based on priority and charge target
                    if self.units[unit].chargedUnit == None:
                        self.unitsForMelee[3].append(unit)
                    else:
                        self.unitsForMelee[2].append(unit)
                
                #Loop through models and set melee used flag to false
                for model in self.units[unit].models:
                    model.meleeUsed = False
                
            #Set current turn saved to current player
            self.currentTurnSaved = self.currentTurn
            self.otherTurnSaved = self.otherTurn
            #Set current player to None
            self.currentTurn = None
            self.otherTurn = None
            
            #Assign who will go next in melee
            continueMelee = self.get_next_melee_turn()
            
            if continueMelee:
                self.state = 45
            else:
                self.currentTurn = self.currentTurnSaved
                self.otherTurn = self.otherTurnSaved
                
                self.phase = 7
                self.set_up_header_display(values)
                self.update_event_log(values, "Melee phase complete.")
                text = self.currentTurn.name + " begins their morale phase."
                self.update_event_log(values, text)
                self.state = 52
        
        if self.state == 45:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.pileIn = True
            
            #Inform players who's turn it is
            text = self.currentTurn.name + ", select a unit to attack with"

            self.update_main_message(values, text)
            #Create a list of the units the player can use
            units = []
            for unit in self.unitsForMelee[self.meleePriority]:
                if unit in self.currentTurn.units:
                    units.append(unit)
            
            #Set up command buttons 
            self.get_command_list(values, units)
            
            self.awaitingEvent = True
            
        #Set up melee weapon choices
        elif self.state == 46:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            wargearList = []
            #Loop through models
            
            for model in self.currentUnit.models:
                hasMeleeWeapon = False
                if not model.dead and model.mSkill > 0 and not model.meleeUsed:
                    for w in model.wargear:
                        wargear = self.currentTurn.playerArmy.codex.wargear[(
                            self.currentTurn.playerArmy.faction, w)]
                        ignore = False
                        #If wargear is already in list, ignore it
                        if wargear in wargearList:
                            ignore = True
                            hasMeleeWeapon = True
                        if not ignore:
                            #If wargear is not melee
                            if wargear.gearType != 0:
                                ignore = True
                                
                        #If cleared, add wargear to list
                        if not ignore:
                            wargearList.append(wargear)
                            hasMeleeWeapon = True
                        
                    #Give close combat weapon if the unit does not have a melee weapon    
                    if not hasMeleeWeapon:
                        wargear = self.currentTurn.playerArmy.codex.wargear[(
                            self.currentTurn.playerArmy.faction, -1)]
                        
                        model.wargear.append((-1))
                        if wargear not in wargearList:
                            wargearList.append(wargear)
                        
            #Set list up as buttons
            wargearList.append("End attack")
            self.get_command_list(values, wargearList)
            
            #Update message
            self.update_main_message(values, "Please select a weapon to use")
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Melee weapon owned by more than one model
        elif self.state == 47:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["All models", "All without custom gear", "Select models individually",
                                           "Back"], actionList=[60, 61, 62, 63])
            
            #Update message
            
            text = "Who will attack with the " + self.currentWeapon.name + "?"
            self.update_main_message(values, text)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Attacking with models individually
        elif self.state == 48:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Reset", "Back"], actionList=[64, 65, 66])
            
            self.selectedModels = []
            
            #Update message
            text = "Select models to attack with. Press confirm when done."
            self.update_main_message(values, text)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Select target
        elif self.state == 49:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Back"], actionList=[67])
            
            self.update_main_message(values, "Select a target")
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Confirm target
        elif self.state == 50:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Back"], actionList=[68, 69])
            
            unit = self.units[self.models[self.nodes[self.targetedNodes[0]].takenBy].unitID]
            
            text = "Are you sure you want to target " + unit.name +"?"
            
            self.update_main_message(values, text)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Target confirmed, rolling damage
        elif self.state == 51:
            attacks = []
            #Loop through shooting models
            for model in self.attackingModels:
                targets = []
                #Loop through nodes in targets
                for node in model.attackTargets:
                    #Get distance between node and model
                    distance = 9999
                    for node2 in model.nodes:
                        d = self.get_distance_between_nodes(node, node2)
                        distance = min(d, distance)
                    #Add model standing on node if it hasn't been added already
                    if self.models[self.nodes[node].takenBy] not in targets:
                        self.models[self.nodes[node].takenBy].H = distance
                        targets.append(self.models[self.nodes[node].takenBy])
                    #If it has, see if this node is closer and update H value
                    else:
                        if distance < self.models[self.nodes[node].takenBy].H:
                            self.models[self.nodes[node].takenBy].H = distance
                #Sort list by H
                targets.sort(key=operator.attrgetter("H"))
                #Pop front of list and save it as target
                target = targets.pop(0)
                #Set strength using weapon stats
                if self.currentWeapon.userStrength:
                    strength = model.strength
                else:
                    strength = self.currentWeapon.strength
                if self.currentWeapon.strengthMultiplier > 1:
                    strength = strength * self.currentWeapon.strengthMultiplier
                if self.currentWeapon.strengthPlus > 0:
                    strength = strength + self.currentWeapon.strengthPlus
                #Check to see if model has a second melee weapon
                attackSpeed = model.attackSpeed
                #Loop through their wargear
                wargearList = copy.copy(model.wargear)
                wargearList.remove(self.currentWeapon.ID[1])
                for w in wargearList:
                    #If wargear is a melee weapon and isn't the current weapon, add +1 to attack speed
                    wargear = self.currentTurn.playerArmy.codex.wargear[self.currentTurn.playerArmy.faction, w]
                    if wargear.gearType == 0:
                        attackSpeed += 1
                        break
                    
                #create an attack object for each point of attack speed
                for i in range(0, attackSpeed):
                    attacks.append(Attack(model.mSkill, strength, self.currentWeapon.damage, 
                                          self.currentWeapon.ap, target, targets))
                    
                #Update melee flag
                model.meleeUsed = True
                    
            targetCodex = self.otherTurn.playerArmy.codex
            #Apply damage
            self.apply_damage(values, attacks, targetCodex, melee=True)
            
            self.flagsGroup.empty()
            self.squaresGroup.empty()
            
            self.currentWeapon = None
            self.state = 46
            
    def handle_morale(self, values):
        
        #Set up
        if self.state == 52:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Begin Phase"], actionList=[71])
            
            #Ask player to click on a unit to move
            self.update_main_message(values, "Press the 'Begin Phase' button to start checking morale")
            
            self.awaitingEvent = True
            
        elif self.state == 53:
            #Loop through all units
            for unit in self.units:
                #If unit is alive and has lost models this turn
                if not self.units[unit].destroyed and self.units[unit].modelsLost > 0:
                    currentUnit = self.units[unit]
                    unitAlive = True
                    fled = {}
                    #Get highest will
                    will = 0
                    for model in currentUnit.models:
                        if not model.dead:
                            will = max(model.will, will)
                    #Roll for deserters
                    print("Roll:", self.randomNumbers[0], "Will:", will, "Unit lost:", currentUnit.modelsLost)
                    deserters = (self.randomNumbers.pop(0) + currentUnit.modelsLost) - will
                    #If deserters is above 0, split models in lists based on will
                    if deserters > 0:
                        modelDict = {}
                        for model in currentUnit.models:
                            if not model.dead:
                                if model.will not in modelDict:
                                    modelDict[model.will] = [model]
                                else:
                                    modelDict[model.will].append(model)
                        #Sort lists by total points
                        for l in modelDict:
                            modelDict[l].sort(key=operator.attrgetter("totalPoints"))
                        #While there are still deserters
                        removed = 0
                        while removed < deserters:
                            breakLoop = True
                            #Grab lowest will list
                            for i in range(0, 20):
                                if i in modelDict:
                                    l = modelDict[i]
                                    currentModels = []
                                    points = 9999
                                    #Grab models with lowest point values and add them to new list
                                    for model in l[:]:
                                        if model.totalPoints <= points:
                                            currentModels.append(model)
                                            l.remove(model)
                                            points = model.totalPoints
                                            model.hpPercentage = model.currentHP/model.maxHP
                                    #Sort new list by HP percentage
                                    currentModels.sort(key=operator.attrgetter("hpPercentage"))
                                    #Remove as necessary, track removals
                                    while (removed < deserters) and (len(currentModels) > 0):
                                        breakLoop = False
                                        currentModels[0].dead = True
                                        currentModels[0].fled = True
                                        #Kill sprite and wipe nodes
                                        currentModels[0].sprite.kill()
                                        for n in currentModels[0].nodes[:]:
                                            self.nodes[n].takenBy = None
                                            currentModels[0].nodes.remove(n)
                                            
                                        currentModels[0].topLeftNode = None
                                        #Store fled info
                                        if currentModels[0].ID in self.currentTurn.models:
                                            playerCodex = self.currentTurn.playerArmy.codex
                                        else:
                                            playerCodex = self.otherTurn.playerArmy.codex
                                        data = playerCodex.models[currentModels[0].data].name
                                        if data not in fled:
                                            fled[data] = 1
                                        else:
                                            fled[data] += 1
                                            
                                        currentModels.pop(0)
                            
                                        #Pass details to is unit still alive
                                        unitAlive = self.is_unit_still_alive(values, self.units[unit])
                                        
                                        #Reduce deserters
                                        removed += 1
                                        
                            if breakLoop:
                                break
            
                        #Report results
                        
                        for modelType in fled:
                            text = (str(fled[modelType]) + " " + modelType + "(s) flee from " + currentUnit.name + 
                                    "!")
                            self.update_event_log(values, text)
                        if not unitAlive:
                            text = currentUnit.name + " has been destroyed!"
                            self.update_event_log(values, text)
                            
                self.units[unit].modelsLost = 0
                        
            #Update statuses
            self.update_control_point_status(values)
            self.update_melee_status(values)      
                      
            #Set up end phase button
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["End Phase"], actionList=[72])
            
            #Ask player to click on a unit to move
            self.update_main_message(values, "Press the 'End Phase' button to end")
            
            self.awaitingEvent = True
            
    def handle_movement(self, values):
        
        if self.state == 7:
            
            #Refresh random numbers
            self.randomNumbers = self.get_random_numbers()
            
            #Loop through current player's units
            for unit in self.units:
                #Reset movement flags
                self.units[unit].moved = False
                self.units[unit].advanced = False
                self.units[unit].fellBack = False
                self.units[unit].disembarked = False
                self.units[unit].chargedUnit = None
                
                if unit in self.currentTurn.units:
                    #Flag those who cannot move as having completed the phase
                    model = self.currentTurn.playerArmy.codex.models[self.units[unit].models[0].data]
                    if 'Immobile' in model.abilities and not model.dead:
                        self.units[unit].endPhase = True
                    else:
                        self.units[unit].endPhase = False
                else:
                    self.units[unit].endPhase = True
                    
            #Move camera to player's deployment zone
            if self.deploymentMap == 0:
                if self.currentTurn.deploymentZone == 1:
                    self.xOffset = 0
                else:
                    self.xOffset = self.xOffsetMax
                self.yOffset = int(self.yOffsetMax/2)
            self.camera = self.surface.subsurface(self.xOffset, self.yOffset, 1280, 720)
                    
            #Set state to 8
            self.state = 8
            
        if self.state == 8:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["End Phase"], actionList=[17])
            
            #Ask player to click on a unit to move
            self.update_main_message(values, "Please select a unit to move")
            
            self.awaitingEvent = True
            
        #Set up move, advance and fall back
        elif self.state == 9:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            commands = []
            actionList = []
            #Set up buttons for move, advance, fall back and cancel
            if self.currentUnit.inMelee:
                commands.append("Fall Back")
                actionList.append(8)
                
            else:
                commands.append("Move")
                commands.append("Advance")
                actionList.append(6)
                actionList.append(7)
            
            #Embark on transport option for infantry
            infantry = False
            if self.phase == 1:
                infantry = self.is_unit_infantry(self.currentUnit)
            if infantry:
                commands.append("Embark")
                actionList.append(74)
                
            #Add disembarking 
            elif len(self.currentUnit.onboard) > 0 and self.phase == 1:
                commands.append("Disembark")
                actionList.append(78)
                
            commands.append("Cancel")
            actionList.append(9)
            self.get_command_list(values, commands, actionList=actionList)
            self.update_main_message(values, "Select a movement type")
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Set up movement options
        elif self.state == 10:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Set up buttons for movement options
            commands = [" - in formation", " - towards point", " - by model"]
            for c in commands[:]:
                if self.phase == 1:
                    #If it's the charge phase, set up charge buttons
                    if self.currentUnit.moved:
                        text = "Move" + c
                    elif self.currentUnit.advanced:
                        text = "Advance" + c
                    elif self.currentUnit.fellBack:
                        text = "Fall Back" + c
                elif self.phase == 4:
                    text = "Charge" + c
                elif self.phase == 5:
                    text = "Move" + c
                commands.append(text)
                commands.remove(c)
            #Only add back button during movement phase
            if self.phase == 1 or self.phase == 5:
                commands.append("Back")
            elif self.phase == 4:
                commands.append("Cancel Charge")
            self.get_command_list(values, commands, actionList=[10, 11, 12, 13])
            
            #Update main message
            if self.phase != 6:
                if self.currentUnit.ID in self.otherTurn.units:
                    otherPlayer = True
                else:
                    otherPlayer = False
                self.update_main_message(values, "Select a movement option", otherPlayer)
            else:
                self.update_main_message(values, "Select a movement option")
            
            #Set awaiting event to true
            self.awaitingEvent = True
            
        #Move models or initial model
        elif self.state == 11:
            #Clear buttons
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Set up confirm and reset
            infantry = False
            if self.phase == 1:
                infantry = self.is_unit_infantry(self.currentUnit)
            if infantry:
                commands = ["Confirm", "Reset", "Embark", "Cancel"]
                self.get_command_list(values, commands, actionList=[14, 15, 74, 16])
            elif len(self.currentUnit.onboard) > 0 and self.phase == 1:
                commands = ["Confirm", "Reset", "Disembark", "Cancel"]
                self.get_command_list(values, commands, actionList=[14, 15, 78, 16])
            else:
                commands = ["Confirm", "Reset", "Cancel"]
                self.get_command_list(values, commands, actionList=[14, 15, 16])
            
            if self.phase == 6:
                otherPlayer = False
            else:
                if self.currentUnit.ID in self.otherTurn.units:
                    otherPlayer = True
                else:
                    otherPlayer = False
            
            #Update message
            if self.phase == 6:
                if self.pileIn:
                    text = ("Move models into melee range. Confirm when ready.")
                else:
                    text = ("Move models to follow up. Confirm when ready.")
                self.update_main_message(values, text, otherPlayer)
            else:
                if self.moveModels:
                    self.update_main_message(values, "Click on models to move them. Confirm when ready.",
                                             otherPlayer)
                else:
                    self.update_main_message(values, "Click on an initial model to move. The rest will follow.",
                                             otherPlayer)
            #Set awaiting event to true
            self.awaitingEvent = True
            
        #Confirm coherency after moving a unit
        elif self.state == 13:
            #Check the current unit for coherency
            coherent = self.check_unit_coherency(self.currentUnit)
            if (self.phase == 1 and not self.currentUnit.fellBack) or self.phase == 6:
                inRange = True
            elif self.phase == 4:
                inRange = False
                for model1 in self.currentUnit.models:
                    if not inRange:
                        for model2 in self.units[self.currentUnit.chargedUnit].models:
                            if not inRange:
                                for node1 in model1.nodes:
                                    if not inRange:
                                        for node2 in model2.nodes:
                                            distance = self.get_distance_between_nodes(node1, node2)
                                            if distance <= 1:
                                                inRange = True
                                                break
                                    else:
                                        break
                            else:
                                break
                    else:
                        break
            elif self.phase == 5:
                self.update_melee_status(values)
                if self.currentUnit.inMelee:
                    inRange = True
                else:
                    inRange = False
            if not coherent:
                hasMoved = False
                #loop through models
                for model in self.currentUnit.models:
                    #check if old nodes list is not empty
                    if len(model.oldNodes) > 0:
                        #turn has moved to true and break
                        hasMoved = True
                        break
                #if has moved is false, set coherent to true
                if not hasMoved:
                    coherent = True
            if self.phase == 1 and self.currentUnit.fellBack:
                self.update_melee_status(values)
                if self.currentUnit.inMelee:
                    inRange = False
                else:
                    inRange = True
            if coherent and inRange:
                self.update_control_point_status(values)
                self.update_melee_status(values)
                self.squaresGroup.empty()
                #Clear old nodes and mark unit as having finished the phase
                self.currentUnit.endPhase = True
                for model in self.currentUnit.models:
                    model.oldNodes = []
                    
                #Update event log
                if self.phase == 1:
                    if self.currentUnit.moved:
                        text = self.currentUnit.name + " has moved."
                    elif self.currentUnit.advanced:
                        text = self.currentUnit.name + " has advanced."
                    elif self.currentUnit.fellBack:
                        text = self.currentUnit.name + " has fallen back from the melee."
                elif self.phase == 4:
                    text = (self.currentUnit.name + " successfully charges " + 
                            self.units[self.currentUnit.chargedUnit].name + "!")
                    #After a successful charge, flag units as in melee and prevent charged unit from using
                    #overwatch
                    self.currentUnit.inMelee = True
                    self.units[self.currentUnit.chargedUnit].inMelee = True
                    self.units[self.currentUnit.chargedUnit].endPhase = True
                elif self.phase == 5:
                    text = self.currentUnit.name + " has moved."
                elif self.phase == 6:
                    text = self.currentUnit.name + " piles into the melee."
                self.update_event_log(values, text)
                #set current unit and model to none
                if self.phase != 6:
                    self.currentUnit = None
                self.currentModel = None
                if self.highlighting:
                    self.toggle_highlighting()
                if self.phase == 1:
                    self.state = 8
                elif self.phase == 4:
                    self.state = 34
                elif self.phase == 5:
                    self.state = 42
                elif self.phase == 6:
                    if self.pileIn:
                        self.state = 46
                    else:
                        self.currentUnit.endPhase = True
                        for p in self.unitsForMelee:
                            if self.currentUnit.ID in p:
                                p.remove(self.currentUnit.ID)
                        #Assign who will go next in melee
                        continueMelee = self.get_next_melee_turn()
                        if continueMelee:
                            self.state = 45
                        else:
                            self.currentTurn = self.currentTurnSaved
                            self.otherTurn = self.otherTurnSaved
                            
                            self.phase = 7
                            self.set_up_header_display(values)
                            self.update_event_log(values, "Melee phase complete.")
                            text = self.currentTurn.name + " begins their morale phase."
                            self.update_event_log(values, text)
                            self.state = 52
                self.awaitingEvent = False
                
            elif coherent and not inRange:
                self.get_purple_squares(highlightMoved=False)
                if self.phase == 1:
                    text = "Cannot confirm: unit must end out of melee range"
                elif self.phase == 4:
                    text = "Cannot confirm: unit must end in melee range of charge target"
                elif self.phase == 5:
                    text = "Cannot confirm: unit must end in melee range of an enemy"
                self.update_main_message(values, text)
                self.state = 11
                self.awaitingEvent = True
                
            else:
                self.get_purple_squares(highlightMoved=False)
                text = "Cannot confirm: Models within unit must be closer together"
                self.update_main_message(values, text)
                self.state = 11
                self.awaitingEvent = True
                
        #After pressing the endphase button
        elif self.state == 14:
            #Clear buttons
            self.clear_buttons(values)
            
            #Set up confirmation buttons
            commands = ["Yes", "No"]
            self.get_command_list(values, commands, actionList=[18, 19])
            
            self.update_main_message(values, "Are you sure you want to end the phase?")
            self.awaitingEvent = True
            
        #After pressing the embark button
        elif self.state == 58:
            #Clear buttons
            self.clear_buttons(values)
            #Ask player to select a transport
            self.update_main_message(values, "Select a friendly transport to embark onto")
            #Set up back button
            commands = ["Back"]
            self.get_command_list(values, commands, actionList=[75])
            self.awaitingEvent = True
            
        #Selecting a viable transport to embark onto
        elif self.state == 59:
            self.clear_buttons(values)
            
            #Set up confirmation buttons
            commands = ["Yes", "No"]
            self.get_command_list(values, commands, actionList=[76, 77])
            
            text = "Are you sure you want to embark onto " + self.currentUnit.name + "?"
            self.update_main_message(values, text)
            self.awaitingEvent = True
            
        #Selecting to disembark
        elif self.state == 60:
            self.clear_buttons(values)
            units = copy.copy(self.currentUnit.onboard)
            units.append("Cancel")
            self.get_command_list(values, units)
            self.update_main_message(values, "Select a unit for disembarking")
            self.awaitingEvent = True
            
        #Selecting where to disembark
        elif self.state == 61:
            self.clear_buttons(values)
            self.get_command_list(values, ["Cancel"], actionList=[81])
            
            #Create list of nodes for disembarking
            self.disembarkNodes = self.get_disembark_nodes(self.currentTransport, self.currentTurn.playerArmy.codex, False)
            
            #Highlight list like a movement range
            image = resources.load_primary_sprite("highlight_lime_green.png")
            image = sprites.get_translucent_sprite(image)
            for node in self.disembarkNodes:
                x = self.nodes[node].backSprite.rect.x
                y = self.nodes[node].backSprite.rect.y
                self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
            
            text = "Choose where to deploy " + self.currentUnit.name + " from " + self.currentTransport.name
            self.update_main_message(values, text)
            
            self.awaitingEvent = True
            
    def handle_shooting(self, values):
        
        #Set up
        if self.state == 24:
            #Loop through units
            for unit in self.currentTurn.units:
                endPhase = False
                self.units[unit].thrownGrenade = False
                #If unit advanced and has no assault weapons, mark as completed the phase
                if self.units[unit].advanced:
                    assault = False
                    for model in self.units[unit].models:
                        if not model.dead:
                            for w in model.wargear:
                                wargear = self.currentTurn.playerArmy.codex.wargear[(
                                    self.currentTurn.playerArmy.faction, w)]
                                if wargear.gearType == 1:
                                    assault = True
                                    break
                            if assault:
                                break
                    if not assault:
                        endPhase = True
                    
                #Elif unit fell back and does not have the fly keyword, mark as completed the phase
                elif self.units[unit].fellBack:
                    if self.units[unit].sharedKeywords:
                        if 'FLY' not in self.units[unit].keywords:
                            endPhase = True
                    else:
                        if 'FLY' not in self.units[unit].models[0].keywords:
                            endPhase = True
                #if unit has no ranged weapons, mark as completed the phase
                if not endPhase:
                    rangedWeapon = False
                    for model in self.units[unit].models:
                        if not model.dead:
                            for w in model.wargear:
                                wargear = self.currentTurn.playerArmy.codex.wargear[(
                                    self.currentTurn.playerArmy.faction, w)]
                                if wargear.gearType in range(1, 6):
                                    rangedWeapon = True
                                    break
                            if rangedWeapon:
                                break
                    if not rangedWeapon:
                        endPhase = True
                        
                #If unit is in melee and does not have a pistol
                if not endPhase and (self.units[unit].inMelee):
                    pistol = False
                    for model in self.units[unit].models:
                        if not model.dead:
                            for w in model.wargear:
                                wargear = self.currentTurn.playerArmy.codex.wargear[(
                                    self.currentTurn.playerArmy.faction, w)]
                                if wargear.gearType == 5:
                                    pistol = True
                                    break
                            if pistol:
                                break
                    if not pistol:
                        endPhase = True
                
                if endPhase:
                    self.units[unit].endPhase = True
                else:
                    self.units[unit].endPhase = False
                    
                #Clear out weapons
                for model in self.units[unit].models:
                    model.weaponsFired = []
                    model.grenadesUsed = False
                    model.otherWeaponsUsed = False
                    model.pistolsUsed = False
                    
            #Mark other units as ended the phase
            if self.players[0] == self.currentTurn:
                otherTurn = self.players[1]
            else:
                otherTurn = self.players[0]
                
            for unit in otherTurn.units:
                self.units[unit].endPhase = True
                 
            #Set state to 25
            self.state = 25
            
        if self.state == 25:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["End Phase"], actionList=[44])
            
            self.update_main_message(values, "Please select a unit to shoot with")
            
            self.awaitingEvent = True
            
        #Unit to shoot with selected
        elif self.state == 26:
            
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            wargearList = []
            #Loop through models
            
            if self.phase == 3:
                currentUnit = self.currentUnit
                turn = self.currentTurn
                otherPlayer = False
            elif self.phase == 4:
                currentUnit = self.currentUnit.targetUnit
                turn = self.otherTurn
                otherPlayer = True
            
            for model in currentUnit.models:
                if not model.dead:
                    #Loop through wargear
                    for w in model.wargear:
                        wargear = turn.playerArmy.codex.wargear[(turn.playerArmy.faction, w)]
                        ignore = False
                        #If wargear is already in list, ignore it
                        if wargear in wargearList:
                            ignore = True
                        if not ignore:
                            #If wargear is melee, other or a shield
                            if wargear.gearType == 0 or wargear.gearType == 6 or wargear.gearType == 7:
                                ignore = True
                            #If wargear is at odds with pistol, grenade or other flag
                            elif wargear.gearType in range(1, 4):
                                if model.grenadesUsed or model.pistolsUsed:
                                    ignore = True
                            elif wargear.gearType == 4:
                                if model.grenadesUsed or model.pistolsUsed or model.otherWeaponsUsed:
                                    ignore = True
                            elif wargear.gearType == 5:
                                if model.grenadesUsed or model.otherWeaponsUsed:
                                    ignore = True
                                    
                        #If wargear is not a pistol and unit is in melee
                        if not ignore and wargear.gearType != 5 and currentUnit.inMelee:
                            ignore = True
                                    
                        #If wargear is a grenade, and a grenade has already been used
                        if not ignore and wargear.gearType == 4 and currentUnit.thrownGrenade:
                            ignore = True
                            
                        #If unit advanced this turn
                        if not ignore and (currentUnit.advanced and wargear.gearType != 1):
                            ignore = True
                            
                        #If this wargear was already used
                        if not ignore and wargear.ID in model.weaponsFired:
                            firedCount = 0
                            ownedCount = 0
                            for w2 in model.weaponsFired:
                                if w2 == wargear.ID:
                                    firedCount += 1
                            for w3 in model.wargear:
                                if w3 == wargear.ID:
                                    ownedCount += 1
                            if firedCount >= ownedCount:
                                ignore = True
                            
                        #If cleared, add wargear to list
                        if not ignore:
                            wargearList.append(wargear)
                        
            #Set list up as buttons
            wargearList.append("Cancel")
            self.get_command_list(values, wargearList)
            
            #Update message
            self.update_main_message(values, "Please select a weapon to use", otherPlayer)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Wargear selected is owned by multiple units and is not grenade
        elif self.state == 27:
            
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["All models", "All without custom gear", "Select models individually",
                                           "Back"], actionList=[34, 35, 36, 37])
            
            #Update message
            if self.phase == 3:
                otherPlayer = False
            elif self.phase == 4:
                otherPlayer = True
            
            text = "Who will fire the " + self.currentWeapon.name + "?"
            self.update_main_message(values, text, otherPlayer)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Selecting models to fire with
        elif self.state == 28:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Reset", "Back"], actionList=[38, 39, 40])
            
            self.selectedModels = []
            
            #Update message
            if self.phase == 3:
                otherPlayer = False
            elif self.phase == 4:
                otherPlayer = True
            text = "Select models to shoot with. Press confirm when done."
            self.update_main_message(values, text, otherPlayer)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Select target
        elif self.state == 29:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Back"], actionList=[41])
            
            self.update_main_message(values, "Select a target")
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Confirm target
        elif self.state == 30:
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            self.get_command_list(values, ["Confirm", "Back"], actionList=[42, 43])
            
            unit = self.units[self.models[self.nodes[self.targetedNodes[0]].takenBy].unitID]
            
            text = "Are you sure you want to target " + unit.name +"?"
            
            self.update_main_message(values, text)
            
            #Awaiting event to true
            self.awaitingEvent = True
            
        #Target confirmed, shooting
        elif self.state == 31:
            attacks = []
            #Loop through shooting models
            for model in self.attackingModels:
                targets = []
                #Loop through nodes in targets
                for node in model.attackTargets:
                    #Get distance between node and model
                    distance = 9999
                    for node2 in model.nodes:
                        d = self.get_distance_between_nodes(node, node2)
                        distance = min(d, distance)
                    #Add model standing on node if it hasn't been added already
                    if self.models[self.nodes[node].takenBy] not in targets:
                        self.models[self.nodes[node].takenBy].H = distance
                        targets.append(self.models[self.nodes[node].takenBy])
                    #If it has, see if this node is closer and update H value
                    else:
                        if distance < self.models[self.nodes[node].takenBy].H:
                            self.models[self.nodes[node].takenBy].H = distance
                #Sort list by H
                targets.sort(key=operator.attrgetter("H"))
                #Pop front of list and save it as target
                target = targets.pop(0)
                #create an attack object for each shot
                #If rapid fire weapon used and primary target is at half range, double shots
                if self.currentWeapon.gearType == 3 and distance <= (self.currentWeapon.attackRange/2):
                    shots = self.currentWeapon.shots * 2
                else:
                    shots = self.currentWeapon.shots
                if self.phase == 3:
                    #Heavy weapon penalties
                    if self.currentWeapon.gearType == 2 and (self.units[model.unitID].moved or self.units[model.unitID].disembarked):
                        rSkill = max(model.rSkill - 1, 1)
                    #Assault weapon penalties
                    elif self.currentWeapon.gearType == 1 and self.units[model.unitID].advanced:
                        rSkill = max(model.rSkill - 1, 1)
                    else:
                        rSkill = model.rSkill
                elif self.phase == 4:
                    rSkill = 1
                for i in range(0, shots):
                    attacks.append(Attack(rSkill, self.currentWeapon.strength, self.currentWeapon.damage, 
                                          self.currentWeapon.ap, target, targets))
                    
                #Add weapon to weapons fired
                model.weaponsFired.append(self.currentWeapon.ID)
                #Update weapon flags
                if self.currentWeapon.gearType in range(1, 4):
                    model.otherWeaponsUsed = True
                elif self.currentWeapon.gearType == 4:
                    model.grenadesUsed = True
                    self.units[model.unitID].thrownGrenade = True
                elif self.currentWeapon.gearType == 5:
                    model.pistolsUsed = True
                    
            if self.phase == 3:
                targetCodex = self.otherTurn.playerArmy.codex
            elif self.phase == 4:
                targetCodex = self.currentTurn.playerArmy.codex
            #Apply damage
            self.apply_damage(values, attacks, targetCodex)
            
            self.flagsGroup.empty()
            self.squaresGroup.empty()
            if self.phase == 3:
                self.state = 25
            elif self.phase == 4:
                self.state = 26
            self.currentWeapon = None
            
        #Pressing the end phase button
        elif self.state == 32:
            #Clear buttons
            values.buttons = []
            self.commandListGroup.empty()
            self.commandListMaxed = False
            
            #Set up confirmation buttons
            commands = ["Yes", "No"]
            self.get_command_list(values, commands, actionList=[45, 46])
            
            self.update_main_message(values, "Are you sure you want to end the phase?")
            self.awaitingEvent = True
        
    def handle_field_click(self, values):
        #If selecting a node to deploy to
        if self.state == 2:
            self.deploy_unit(values, self.currentNode, self.currentTurn.deploymentZoneNodes, self.currentUnit, 
                             self.currentTurn.playerArmy.codex, True)
            """
            #Check if node is in players deployment zone
            if self.currentNode.coordinates in self.currentTurn.deploymentZoneNodes:
                #If so, look at the viability of placing models as closely to the click as possible
                successes = 0 #Count of models successfully allocated
                
                nodes = []
                for node in self.currentTurn.deploymentZoneNodes:
                    self.nodes[node].H = (abs(self.nodes[node].x - self.currentNode.x) + 
                                          abs(self.nodes[node].y - self.currentNode.y))
                    nodes.append(self.nodes[node])
                nodes.sort(key=operator.attrgetter("H"))
                
                images = {}
                
                for model in self.currentUnit.models:
                    #Loop through size and check that nodes are available
                    size = self.currentTurn.playerArmy.codex.models[model.data].size
                    running2 = True
                    if "FLY" in model.keywords:
                        checkWalkable = False
                    else:
                        checkWalkable = True
                    while len(nodes) > 0 and running2:
                        node = nodes.pop(0)
                        running = True
                        while running:
                            running, taken = self.get_standable_nodes(node, size, checkWalkable)
                            
                            if running:
                                #If enough space can be found assign nodes to model
                                cover = 3
                                for n in taken:
                                    self.nodes[n].takenBy = model.ID
                                    cover = min(cover, self.nodes[n].cover)
                                    model.nodes.append(n)
                                    
                                    #Set top left node
                                    if model.topLeftNode == None:
                                        model.topLeftNode = n
                                    else:
                                        if n[0] <= model.topLeftNode[0] and n[1] <= model.topLeftNode[1]:
                                            model.topLeftNode = n
                                 
                                #set cover   
                                model.cover = cover
                                
                                #Set up sprites
                                imageName = self.currentTurn.playerArmy.codex.models[model.data].spriteName
                                imagePrimary = self.currentTurn.playerArmy.codex.models[model.data].spritePrimary
                                imageRect = self.currentTurn.playerArmy.codex.models[model.data].spriteRect
                                imageRect = (node.backSprite.rect.x, node.backSprite.rect.y, imageRect[0], 
                                             imageRect[1])
                                
                                if imageName not in images:
                                    if imagePrimary:
                                        images[imageName] = resources.load_primary_sprite(imageName)
                                    else:
                                        images[imageName] = resources.load_secondary_sprite(imageName)
                                image = images[imageName]
                                model.sprite = sprites.GameSprite(image, imageRect)
                                self.modelsGroup.add(model.sprite)
                                running = False
                                running2 = False
                                successes += 1
                
                
                
                #Clean up failures
                if successes < len(self.currentUnit.models):
                    print("ULTIMATE FAILURE")
                    #kill models sprites
                    self.delete_unit_from_field(self.currentUnit)
                
                else:
                    #Add purple squares to units
                    self.get_purple_squares()
                    #Update message
                    text = self.currentTurn.name + " can move individual models or confirm the unit's position"
                    self.update_main_message(values, text)
                    self.state = 3
            """
        
        #Click on model to move during deployment     
        elif self.state == 3:
            #Does the clicked node contain a model?
            if self.currentNode.takenBy != None:
                #Is that model a part of the current unit
                if self.models[self.currentNode.takenBy] in self.currentUnit.models:
                    model = self.models[self.currentNode.takenBy]
                    model.availableNodes = []
                    size = self.currentTurn.playerArmy.codex.models[model.data].size
                    #Grab the nodes it can be moved to
                    if "FLY" in model.keywords:
                        checkWalkable = False
                    else:
                        checkWalkable = True
                    for node in self.currentTurn.deploymentZoneNodes:
                        running = True
                        while running:
                            running = self.get_standable_nodes(self.nodes[node], size, checkWalkable, 
                                                     returnTaken=False, deploymentOnly=False,
                                                     modelID=model.ID)  
                                
                            if running:
                                model.availableNodes.append(node)
                                break
                                
                                    
                    if len(model.availableNodes) > 0:
                        self.currentModel = model
                        #If nodes can be found, highlight them green for player to place unit
                        self.get_purple_squares(False, True)
                        
                        image = resources.load_primary_sprite("highlight_lime_green.png")
                        image = sprites.get_translucent_sprite(image)
                        for node in model.availableNodes:
                            x = self.nodes[node].backSprite.rect.x
                            y = self.nodes[node].backSprite.rect.y
                            self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
                            
                        #Update message
                        text = "Select where to move the model to"
                        self.update_main_message(values, text)
                            
                        #Change state to 4
                        self.state = 4
           
                        
        elif self.state == 4:
            #Make sure selected node is within the current model's available nodes
            if self.currentNode.coordinates in self.currentModel.availableNodes:
                #If so, move model to selected point
                dex = self.players[self.currentModel.ID[0] - 1].playerArmy.codex
                size = dex.models[self.currentModel.data].size
                self.move_model_to_point(self.currentModel, size, self.currentNode)
                #Clear squares group and current model
                self.get_purple_squares()
                self.currentModel = None
                #Update message
                text = self.currentTurn.name + " can move individual models or confirm the unit's position"
                self.update_main_message(values, text)
                #Set state back to three
                self.state = 3
                
        #Selecting a unit during movement phase
        elif self.state == 8:
            #Does the selected node contain a model?
            if self.currentNode.takenBy != None:
                #If so, has the unit the model belongs to completed the phase?
                unit = self.units[self.models[self.currentNode.takenBy].unitID]
                #If not, set unit as current unit and purple highlight it
                if not unit.endPhase and unit.ID in self.currentTurn.units:
                    self.currentUnit = unit
                    self.get_purple_squares()
                    #Set state to 9, turn awaiting event off
                    self.state = 9
                    self.awaitingEvent = False
                    
        #Selecting a model to move in the movement phase
        elif self.state == 11:
            #Does the clicked node contain a model?
            if self.currentNode.takenBy != None:
                #Is that model a part of the current unit
                if self.models[self.currentNode.takenBy] in self.currentUnit.models:
                    #Has the model moved already?
                    model = self.models[self.currentNode.takenBy]
                    if len(model.oldNodes) == 0:
                        #If not, generate movement range
                        if self.currentUnit.ID in self.currentTurn.units:
                            size = self.currentTurn.playerArmy.codex.models[model.data].size
                        else:
                            size = self.otherTurn.playerArmy.codex.models[model.data].size
                        
                        #Movement phase movement rules
                        if self.phase == 1:
                            passCloseSpecific = None
                            standCloseSpecific = None
                            standClose = False
                            mustBeClose = False
                            if "FLY" in model.keywords:
                                checkWalkable = False
                                allowTaken = True
                                passClose = True
                            else:
                                checkWalkable = True
                                allowTaken = False
                                passClose = False
                            if self.currentUnit.fellBack:
                                passClose = True
                            #Boost movement by 3 if advancing
                            if self.currentUnit.advanced:
                                maxMove = model.maxMove + 3
                            else:
                                maxMove = model.maxMove
                                
                        #Charge phase movement rules
                        elif self.phase == 4:
                            passCloseSpecific = self.currentUnit.chargedUnit
                            standCloseSpecific = self.currentUnit.chargedUnit
                            standClose = False
                            mustBeClose = False
                            if "FLY" in model.keywords:
                                checkWalkable = False
                                allowTaken = True
                                passClose = True
                            else:
                                checkWalkable = True
                                allowTaken = False
                                passClose = False
                            maxMove = self.currentUnit.chargeRange
                            
                        #Intervention movement rules
                        elif self.phase == 5:
                            passCloseSpecific = None
                            standCloseSpecific = None
                            standClose = True
                            mustBeClose = False
                            if "FLY" in model.keywords:
                                checkWalkable = False
                                allowTaken = True
                            else:
                                checkWalkable = True
                                allowTaken = False
                            passClose = True
                            maxMove = 3
                            
                        #Melee phase movement rules
                        elif self.phase == 6:
                            passCloseSpecific = None
                            standCloseSpecific = None
                            standClose = True
                            mustBeClose = False
                            for node  in model.nodes:
                                for x in range(-1, 2):
                                    for y in range(-1, 2):
                                        closeNode = (node[0] + x, node[1] + y)
                                        if closeNode in self.nodes:
                                            if self.nodes[closeNode].takenBy != None:
                                                if self.nodes[closeNode].takenBy in self.otherTurn.models:
                                                    mustBeClose = True
                                                    break
                                                
                                    if mustBeClose:
                                        break
                                    
                                if mustBeClose:
                                    break
                            if "FLY" in model.keywords:
                                checkWalkable = False
                                allowTaken = True
                            else:
                                checkWalkable = True
                                allowTaken = False
                            passClose = True
                            maxMove = 3
                        t1 = time.process_time()
                        moveRange = self.get_movement_range(model.topLeftNode, model.minMove, maxMove, size, 
                                                            checkWalkable=checkWalkable, allowTaken=allowTaken, 
                                                            passClose=passClose, standClose=standClose,
                                                            passCloseSpecific=passCloseSpecific, 
                                                            standCloseSpecific=standCloseSpecific,
                                                            mustBeClose=mustBeClose,
                                                            modelID=model.ID, enemyModels=self.otherTurn.models)
                        t2 = time.process_time()
                        timediff = t2 - t1
                        print(f"It took {timediff} seconds to calculate that movement range")
                        #If movement range is empty, do nothing
                        if len(moveRange) == 0:
                            print("No moverange!")
                        else:
                            #Else, Display movement range as green squares
                            model.availableNodes = moveRange
                            self.currentModel = model
                            self.get_purple_squares(highlightUnit=False, highlightModel=True)
                            
                            image = resources.load_primary_sprite("highlight_lime_green.png")
                            image = sprites.get_translucent_sprite(image)
                            for node in model.availableNodes:
                                if node not in model.nodes:
                                    x = self.nodes[node].backSprite.rect.x
                                    y = self.nodes[node].backSprite.rect.y
                                    self.squaresGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))           
                            
                            #Update main message and set state to 12
                            self.update_main_message(values, "Select where to move the model to")
                            self.state = 12
                        
            else:
                pass
                            
         
        #Selecting where to move a model to in the movement phase                   
        elif self.state == 12:
            #If node is in model's available nodes
            if self.currentNode.coordinates in self.currentModel.availableNodes:
                
                if self.moveModels:
                    #Set old nodes as current nodes
                    self.currentModel.oldNodes = self.currentModel.nodes
                    #Move node to point
                    if self.currentUnit.ID in self.currentTurn.units:
                        size = self.currentTurn.playerArmy.codex.models[self.currentModel.data].size
                    else:
                        size = self.otherTurn.playerArmy.codex.models[self.currentModel.data].size
                    self.move_model_to_point(self.currentModel, size, self.currentNode)
                    #If moving individually, set state to 11 and update message
                    self.update_main_message(values, "Click on models to move them. Confirm when ready.")
                elif self.moveFormation or self.moveToPoint:
                    #Set current model's top left node as initial model
                    initialModel = self.currentModel.topLeftNode
                    
                    
                    #Loop through models
                    models = []
                    for model in self.currentUnit.models:
                        #Ignore if model is the initial model or is dead
                        if model != self.currentModel and not model.dead:
                            #Otherwise, calculate distance between models and save it
                            model.H = self.get_distance_between_nodes(initialModel, model.topLeftNode)
                            if self.moveFormation:
                                #Also set relative position as target node
                                model.targetNode = (model.topLeftNode[0] - initialModel[0],
                                                    model.topLeftNode[1] - initialModel[1])
                            #Add model to list
                            models.append(model)
                    
                    #Move initial model
                    self.currentModel.oldNodes = self.currentModel.nodes
                    if self.currentUnit.ID in self.currentTurn.units:
                        size = self.currentTurn.playerArmy.codex.models[self.currentModel.data].size
                    else:
                        size = self.otherTurn.playerArmy.codex.models[self.currentModel.data].size
                    self.move_model_to_point(self.currentModel, size, self.currentNode)
                    
                    #Sort list of models by distance from initial model
                    models.sort(key=operator.attrgetter("H"))
                    
                    #loop through models
                    for model in models:
                        #Get available nodes if model hasn't moved and is alive
                        if len(model.oldNodes) == 0 and not model.dead:
                            if self.currentUnit.ID in self.currentTurn.units:
                                size = self.currentTurn.playerArmy.codex.models[model.data].size
                            else:
                                size = self.otherTurn.playerArmy.codex.models[model.data].size
                            
                            if self.phase == 1:
                                passCloseSpecific = None
                                standCloseSpecific = None
                                standClose = False
                                if "FLY" in model.keywords:
                                    checkWalkable = False
                                    allowTaken = True
                                    passClose = True
                                else:
                                    checkWalkable = True
                                    allowTaken = False
                                    passClose = False
                                if self.currentUnit.fellBack:
                                    passClose = True
                                #Boost movement by 3 if advancing
                                if self.currentUnit.advanced:
                                    maxMove = model.maxMove + 3
                                else:
                                    maxMove = model.maxMove
                                    
                            elif self.phase == 4:
                                passCloseSpecific = self.currentUnit.chargedUnit
                                standCloseSpecific = self.currentUnit.chargedUnit
                                standClose = False
                                if "FLY" in model.keywords:
                                    checkWalkable = False
                                    allowTaken = True
                                    passClose = True
                                else:
                                    checkWalkable = True
                                    allowTaken = False
                                    passClose = False
                                maxMove = self.currentUnit.chargeRange
                            
                            elif self.phase == 5:
                                passCloseSpecific = None
                                standCloseSpecific = None
                                standClose = True
                                if "FLY" in model.keywords:
                                    checkWalkable = False
                                    allowTaken = True
                                else:
                                    checkWalkable = True
                                    allowTaken = False
                                passClose = True
                                maxMove = 3
                                
                            moveRange = self.get_movement_range(model.topLeftNode, model.minMove, maxMove, size, 
                                                            checkWalkable=checkWalkable, allowTaken=allowTaken, 
                                                            passClose=passClose, standClose=standClose,
                                                            passCloseSpecific=passCloseSpecific, 
                                                            standCloseSpecific=standCloseSpecific,
                                                            modelID=model.ID, enemyModels=self.otherTurn.models)
                        #If model can move, move to node closest to the target node
                            if len(moveRange) > 0:
                                if self.moveFormation:
                                    model.targetNode = (model.targetNode[0] + self.currentModel.topLeftNode[0],
                                                        model.targetNode[1] + self.currentModel.topLeftNode[1])
                                elif self.moveToPoint:
                                    model.targetNode = self.currentNode.coordinates
                                bestNode = None
                                bestDistance = 9999
                                for node in moveRange:
                                    if bestNode == None:
                                        bestNode = node
                                        bestDistance = self.get_distance_between_nodes(node, model.targetNode)
                                    else:
                                        distance = self.get_distance_between_nodes(node, model.targetNode)
                                        if distance < bestDistance:
                                            bestNode = node
                                            bestDistance = distance
                                            
                                model.oldNodes = model.nodes
                                if self.currentUnit.ID in self.currentTurn.units:
                                    size = self.currentTurn.playerArmy.codex.models[model.data].size
                                else:
                                    size = self.otherTurn.playerArmy.codex.models[model.data].size
                                self.move_model_to_point(model, size, self.nodes[bestNode])
                #Update squares
                self.get_purple_squares(highlightMoved=False)
                self.state = 11
                #Set current model to none
                self.currentModel = None
                
        #Selecting a friendly mage unit for spellcasting
        elif self.state == 16:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #Can the unit act and is it friendly?
                unit = self.units[self.models[self.currentNode.takenBy].unitID]
                if not unit.endPhase and unit.ID in self.currentTurn.units: 
                    #Set as current unit
                    self.currentUnit = unit
                    #Add purple squares
                    self.get_purple_squares()
                    #Set state to 17 and awaiting event off
                    self.state = 17
                    self.awaitingEvent = False
                    
        #Selecting a target for a spell
        elif self.state == 18:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #If spell is a damaging spell....
                if self.currentSpell.use1 == 0:
                    #Make sure target is an enemy
                    if self.players[0] == self.currentTurn:
                        enemy = self.players[1]
                    else:
                        enemy = self.players[0]
                    #If target is CHARACTER and has <10 HP, ignore unless they are closest visible enemy
                    ignore = False
                    if 'CHARACTER' in self.models[self.currentNode.takenBy].keywords and self.models[self.currentNode.takenBy].maxHP < 10:
                        if not self.models[self.currentNode.takenBy].unitID in self.currentUnit.closestVisible:
                            ignore = True
                    if self.currentNode.takenBy in enemy.models and not ignore:
                        for model in self.currentUnit.models:
                            if not model.dead:
                                #Get list of in range nodes
                                model.attackTargets = self.get_nodes_in_range(model, 
                                                                              self.units[self.models[self.currentNode.takenBy].unitID], 
                                                                  self.currentSpell.targetRange)
                                #Check LOS on in range nodes
                                newNodes = []
                                if self.players[0] == self.currentTurn:
                                    enemy = self.players[1]
                                else:
                                    enemy = self.players[0]
                                for target in model.attackTargets:
                                    for node in model.nodes:
                                        if node not in newNodes:
                                            success = self.is_node_in_line_of_sight(node, target, enemy)
                                            if success:
                                                newNodes.append(target)
                                                break
                                model.attackTargets = newNodes
                                
                                #Add nodes to unit's spell targets list
                                for node in model.attackTargets:
                                    if node not in self.currentUnit.spellTargets:
                                        self.currentUnit.spellTargets.append(node)
                                        
                                model.attackTargets = []
                            
                        #If target has in range, visible nodes, then set state to 19
                        if len(self.currentUnit.spellTargets) > 0:
                            self.currentUnit.targetUnit = self.units[self.models[self.currentNode.takenBy].unitID]
                            self.state = 19
                            self.awaitingEvent = False
                        else:
                            print("No targets...")
                
        #Other player selecting a mage to dispel with                    
        elif self.state == 21:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #Make sure selected unit is an enemy
                if self.players[0] == self.currentTurn:
                    enemy = self.players[1]
                else:
                    enemy = self.players[0]
                if self.currentNode.takenBy in enemy.models:
                    unit = self.units[self.models[self.currentNode.takenBy].unitID]
                    if not unit.endPhase:
                        canDispel = False
                        #See if unit is in range
                        keepLooking = False
                        for model in unit.models:
                            if not model.dead:
                                targets = self.get_nodes_in_range(model, self.currentUnit, 24)
                                if len(targets) > 0:
                                    keepLooking = True
                                    break
                        
                        #Check spell level
                        if keepLooking:
                            if self.currentSpell.level > unit.dispelLevel:
                                keepLooking = False
                            
                        #Check mana   
                        if keepLooking:
                            if unit.currentMana >= math.floor(
                                self.currentSpell.mana * unit.dispelRate):
                                canDispel = True
                
                        if canDispel:
                            self.otherUnit = unit
                            self.get_purple_squares(highlightUnit=False, otherUnit=True)
                            text = "Dispel with " + unit.name + "?"
                            self.update_main_message(values, text, otherPlayer=True)
                
        #Selecting a unit to shoot with in the shooting phase            
        elif self.state == 25:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #Can the unit act
                unit = self.units[self.models[self.currentNode.takenBy].unitID]
                if not unit.endPhase: 
                    #Set as current unit
                    self.currentUnit = unit
                    #Add purple squares
                    self.get_purple_squares()
                    #Set state to 26 and awaiting event off
                    self.state = 26
                    self.awaitingEvent = False
                    
        #Select models to shoot with in the shooting phase
        elif self.state == 28:
            #Does clicked node contain a model?
            if self.currentNode.takenBy != None:
                #Is model in the current unit?
                model = self.models[self.currentNode.takenBy]
                if self.phase == 3:
                    currentUnit = self.currentUnit
                elif self.phase == 4:
                    currentUnit = self.currentUnit.targetUnit
                if model in currentUnit.models:
                    #Does model have the current weapon?
                    success = False
                    for w in model.wargear:
                        if w == self.currentWeapon.ID[1]:
                            success = True
                            break
                    #Has this weapon been fired already?
                    if self.currentWeapon.ID in model.weaponsFired:
                        success = False
                    #Is this model allowed to use this type of weapon?
                    if self.currentWeapon.gearType in range(1, 4) and (model.pistolsUsed or model.grenadesUsed):
                        success = False
                    elif self.currentWeapon.gearType == 5 and (model.otherWeaponsUsed or model.grenadesUsed):
                        success = False
                    elif self.currentWeapon.gearType == 4 and (model.pistolsUsed or model.otherWeaponsUsed):
                        success = False
                    if success:
                        if self.currentWeapon.gearType == 4:
                            self.selectedModels = [model]
                        else:
                            #If model is in the selected list, remove them
                            if model in self.selectedModels:
                                self.selectedModels.remove(model)
                            #Else, add them
                            else:
                                self.selectedModels.append(model)
                        #Update purple squares
                        self.get_purple_squares(highlightUnit=False, highlightSelected=True)
                
        #Select a target to shoot        
        elif self.state == 29:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                self.targetedNodes = []
                self.attackingModels = []
                #Make sure selected unit is an enemy
                if self.players[0] == self.currentTurn:
                    enemy = self.players[1]
                else:
                    enemy = self.players[0]
                if self.currentNode.takenBy in enemy.models:
                    targetUnit = self.units[self.models[self.currentNode.takenBy].unitID]
                    #If target is CHARACTER and has <10 HP, ignore unless they are closest visible enemy
                    ignore = False
                    if 'CHARACTER' in targetUnit.models[0].keywords and targetUnit.models[0].maxHP < 10:
                        if not targetUnit.ID in self.currentUnit.closestVisible:
                            ignore = True
                            
                    #If unit is in melee, ignore target unless they are the closest visible enemy
                    if not ignore and self.currentUnit.inMelee:
                        if not targetUnit.ID in self.currentUnit.closestVisible:
                            ignore = True
                            
                    #If unit is not in melee, do not allow shooting against a in-melee target
                    if not ignore and not self.currentUnit.inMelee and targetUnit.inMelee:
                        ignore = True
                            
                    if not ignore:
                        targetFound = False
                        for model in self.selectedModels:
                            model.attackTargets = []
                            if not model.dead:
                                #Get list of in range nodes
                                model.attackTargets = self.get_nodes_in_range(model, targetUnit, 
                                                                  self.currentWeapon.attackRange)
                                #Check LOS on in range nodes
                                newNodes = []
                                for target in model.attackTargets:
                                    for node in model.nodes:
                                        if node not in newNodes:
                                            success = self.is_node_in_line_of_sight(node, target, enemy)
                                            if success:
                                                newNodes.append(target)
                                                targetFound = True
                                                if target not in self.targetedNodes:
                                                    self.targetedNodes.append(target)
                                                break
                                model.attackTargets = newNodes
                                
                            if len(model.attackTargets) > 0:
                                self.attackingModels.append(model)
                            
                                
                        #If target has in range, visible nodes, then set state to 30
                        if targetFound:
                            self.get_purple_squares(highlightUnit=False, highlightAttacking=True)
                            image = resources.load_primary_sprite("target.png")
                            for node in self.targetedNodes:
                                x = self.nodes[node].backSprite.rect.x
                                y = self.nodes[node].backSprite.rect.y
                                self.flagsGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
                            
                            #Set up target sprites
                            self.currentUnit.targetUnit = targetUnit
                            self.state = 30
                            self.awaitingEvent = False
                
        #Selecting a unit to charge with in the charging phase    
        elif self.state == 34:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #Is model owned by the current player?
                if self.currentNode.takenBy in self.currentTurn.models:
                    #Can the unit act
                    unit = self.units[self.models[self.currentNode.takenBy].unitID]
                    if not unit.endPhase: 
                        #Set as current unit
                        self.currentUnit = unit
                        #Add purple squares
                        self.get_purple_squares()
                        #Set state to 35 and awaiting event off
                        self.state = 35
                        self.awaitingEvent = False
                
        #Selecting a target to charge        
        elif self.state == 35:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #Is unit an enemy?
                if self.currentNode.takenBy in self.otherTurn.models:
                    success = True
                    #Is target airborne? If so, current unit will need FLY
                    if 'AIRBORNE' in self.models[self.currentNode.takenBy].keywords:
                        if 'FLY' not in self.currentUnit.models[0].keywords:
                            success = False
                    if success:
                        #Is unit within 10 squares
                        found = False
                        enemyUnit = self.units[self.models[self.currentNode.takenBy].unitID]
                        for model in self.currentUnit.models:
                            if not model.dead:
                                inRange = self.get_nodes_in_range(model, enemyUnit, 10)
                                if len(inRange) > 0:
                                    found = True
                                    break
                        
                        if found:
                            #Set current unit's target unit to selected unit
                            self.currentUnit.targetUnit = enemyUnit
                            #Set state to 36 and awaiting event
                            self.state = 36
                            self.awaitingEvent = False
                
        #Selecting a CHARACTER to move during intervention            
        elif self.state == 42:
            #Does the clicked node contain a unit?
            if self.currentNode.takenBy != None:
                #Can the model act?
                unit = self.units[self.models[self.currentNode.takenBy].unitID]
                if not unit.endPhase:
                    self.currentUnit = unit
                    self.get_purple_squares()
                    self.state = 10
                    self.awaitingEvent = False
                    
        #Select models to attack with in the melee phase
        elif self.state == 48:
            #Does clicked node contain a model?
            if self.currentNode.takenBy != None:
                #Is model in the current unit?
                model = self.models[self.currentNode.takenBy]
                if model in self.currentUnit.models:
                    #Does model have the current weapon?
                    success = False
                    for w in model.wargear:
                        if w == self.currentWeapon.ID[1]:
                            success = True
                            break
                    #Has this model attacked already?
                    if model.meleeUsed:
                        success = False
                    if success:
                        #If model is in the selected list, remove them
                        if model in self.selectedModels:
                            self.selectedModels.remove(model)
                        #Else, add them
                        else:
                            self.selectedModels.append(model)
                        #Update purple squares
                        self.get_purple_squares(highlightUnit=False, highlightSelected=True)
                
        #Select target in melee phase        
        elif self.state == 49:
            #Does clicked node contain a model?
            if self.currentNode.takenBy != None:
                #Is model is in an enemy unit?
                if self.currentNode.takenBy in self.otherTurn.models:
                    #Get target unit
                    targetUnit = self.units[self.models[self.currentNode.takenBy].unitID]
                    self.targetedNodes = []
                    self.attackingModels = []
                    targetFound = False
                    #Loop through selected models
                    for model in self.selectedModels:
                        #If not dead, get targets
                        if not model.dead:
                            result = self.get_melee_range(self.currentUnit, model, 
                                                          targetUnit)
                            if len(result) > 0:
                                #If so, skip straight to rolling attack
                                model.attackTargets = result
                                self.attackingModels.append(model)
                                targetFound = True
                                for node in result:
                                    if node not in self.targetedNodes:
                                        self.targetedNodes.append(node)
                                
                    #If target has in range nodes then set state to 50
                    if targetFound:
                        self.get_purple_squares(highlightUnit=False, highlightAttacking=True)
                        image = resources.load_primary_sprite("target.png")
                        for node in self.targetedNodes:
                            x = self.nodes[node].backSprite.rect.x
                            y = self.nodes[node].backSprite.rect.y
                            self.flagsGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))
                        
                        #Set up target sprites
                        self.currentUnit.targetUnit = targetUnit
                        self.state = 50
                        self.awaitingEvent = False
                
        #Selecting a transport to embark onto        
        elif self.state == 58:
            #Does the clicked node contain a model?
            if self.currentNode.takenBy != None:
                transport = self.models[self.currentNode.takenBy]
                #Is the model in the current players models?
                if transport.ID in self.currentTurn.models:
                    friendly = True
                else:
                    friendly = False
                #Does it have the transport keyword?
                if friendly and 'TRANSPORT' in transport.keywords:
                    isTransport = True
                else:
                    isTransport = False
                    
                #Does it have capacity to carry the current unit?
                if friendly and isTransport:
                    newModels = 0
                    for model in self.currentUnit.models:
                        if not model.dead:
                            newModels += 1
                    #Loop through living models and units in the current transport
                    onboardModels = 0
                    for unit in self.units[transport.unitID].onboard:
                        for model in self.units[unit].models:
                            if not model.dead:
                                onboardModels += 1
                    if ((transport.maxHP - onboardModels) - newModels) >= 0:
                        hasCapacity = True
                    else:
                        hasCapacity = False
                        
                    if hasCapacity:
                        unitInRange = True
                        #Is every model in the current unit within 3 squares of the transport?
                        #Loop through models
                        for model in self.currentUnit.models:
                            #Loop through model's nodes
                            modelInRange = False
                            for node1 in model.nodes:
                                #Loop through transport's nodes
                                for node2 in transport.nodes:
                                    #Compare distance
                                    distance = self.get_distance_between_nodes(node1, node2)
                                    
                                    #If any distance is less than 4 squares, break out of the node loops and check the next model
                                    if distance < 4:
                                        modelInRange = True
                                        break
                                    
                                if modelInRange:
                                    break
                            #If all distances are further than 3 nodes, break out of all loops and flag that the transport is too far
                            if not modelInRange:
                                unitInRange = False
                                break
                            
                        if unitInRange:
                            self.currentTransport = self.units[transport.unitID]
                            self.state = 59
                            self.awaitingEvent = False
                        else:
                            text = "Cannot confirm: some models are too far away from the selected transport"
                            self.update_main_message(values, text)
                    
                    else:
                        text = "Cannot confirm: transport does not have capacity to carry this many models"
                        self.update_main_message(values, text)
            
            #If all checks are passed, advance state
            
        #Selecting where to disembark a unit
        elif self.state == 61:
            #attempt to deploy
            self.deploy_unit(values, self.currentNode, self.disembarkNodes, self.currentUnit, self.currentTurn.playerArmy.codex, False)
                        
    def is_node_in_line_of_sight(self, startNode, targetNode, enemy):
        #Create a current node and set success to true
        success = True
        if startNode[0] < targetNode[0]:
            x = 1
        elif startNode[0] > targetNode[0]:
            x = -1
        else:
            x = 0
        if startNode[1] < targetNode[1]:
            y = 1
        elif startNode[1] > targetNode[1]:
            y = -1
        else:
            y = 0
        currentNode = (startNode[0] + x, startNode[1] + y)
        #While current node is not target node
        while currentNode != targetNode:
            #Check current node is not blocking LOS
            if self.nodes[currentNode].blocksLOS:
                #If so, break and return false
                success = False
                break
            elif self.nodes[currentNode].takenBy != None:
                model = self.models[self.nodes[currentNode].takenBy]
                if model.ID in enemy.models and 'AIRBORNE' not in model.keywords:
                    success = False
                    break
                
            #Otherwise, advance current node and continue
            if success:
                if currentNode[0] < targetNode[0]:
                    x = 1
                elif currentNode[0] > targetNode[0]:
                    x = -1
                else:
                    x = 0
                if currentNode[1] < targetNode[1]:
                    y = 1
                elif currentNode[1] > targetNode[1]:
                    y = -1
                else:
                    y = 0
                currentNode = (currentNode[0] + x, currentNode[1] + y)
            
        return success
    
    def is_unit_infantry(self, unit):
        infantry = True
        for model in unit.models:
            if "INFANTRY" not in model.keywords:
                infantry = False
                break
            
        return infantry
    
    def is_unit_still_alive(self, values, unit, targetCodex=None):
        alive = False
        artillery = False
        #Check if a model can be found alive and has the artillery ability
        for model in unit.models:
            if not model.dead:
                alive = True
            if targetCodex != None:
                data = targetCodex.models[model.data]
                if 'Artillery' in data.abilities:
                    artillery = True
            
        #If a model has the artillery ability and the unit is alive
        if alive and artillery:
            #Loop through to see if any living models have the ARTILLERY GUNNER keyword
            gunner = False
            for model in unit.models:
                if "ARTILLERY GUNNER" in model.keywords and not model.dead:
                    gunner = True
                    break
            #If not, kill all living models
            if not gunner:
                alive = False
                for model in unit.models:
                    if not model.dead:
                        model.dead = True
                        #Kill sprite and wipe nodes
                        model.sprite.kill()
                        for n in model.nodes[:]:
                            self.nodes[n].takenBy = None
                            model.nodes.remove(n)
                            
                        model.topLeftNode = None
                        
                text = "With no artillery gunners left, " + unit.name + " is completely destroyed!"
                self.update_event_log(values, text)
       
        if not alive:
            unit.destroyed = True
            self.check_kill_points(values, unit)
            
        #If unit has been wiped, return true
        #otherwise, return false
        return alive
                
    def move_model_to_point(self, model, size, node):
        #move sprite's rect to node
        model.sprite.rect.x = node.backSprite.rect.x
        model.sprite.rect.y = node.backSprite.rect.y
        
        #Clear old nodes
        for n in model.nodes:
            if self.nodes[n].takenBy == model.ID:
                self.nodes[n].takenBy = None
        model.nodes = []
        
        #Set cover
        cover = 3
        
        #Take enough nodes to cover the size
        for x in range(0, size[0]):
            for y in range(0, size[1]):
                currentNode = (node.coordinates[0] + x, node.coordinates[1] + y)
                self.nodes[currentNode].takenBy = model.ID
                cover = min(cover, self.nodes[currentNode].cover)
                if currentNode not in model.nodes:
                    model.nodes.append(currentNode)
                    
        #Set topLeftNode
        model.topLeftNode = node.coordinates
        
        if "AIRBORNE" in model.keywords:
            model.cover = 0
        else:
            model.cover = cover
            
    def reset_unit_movement(self, unit, player):
        #Loop through current unit
        for model in unit.models:
            #If the model has old nodes, move model to the top-left most node in their old nodes
            if not model.dead:
                if len(model.oldNodes) > 0:
                    x = 9999
                    y = 9999
                    for node in model.oldNodes:
                        if node[0] <= x and node[1] <= y:
                            oldNode = node
                            x = node[0]
                            y = node[1]
                    size = player.playerArmy.codex.models[model.data].size
                    self.move_model_to_point(model, size, self.nodes[oldNode])
                #Reset old nodes to an empty list
                model.oldNodes = []
            
    def set_up_header_display(self, values):
        self.headerGroup.empty()
        
        #Display players scores and SP
        text = self.players[0].name + " - Points: " + str(self.players[0].vp) + " - SP: " + str(self.players[0].sp)
        image = values.font30.render(text, True, self.players[0].colour)
        self.headerGroup.add(sprites.GameSprite(image, (0, 0, image.get_width(), image.get_height())))
        
        text = self.players[1].name + " - Points: " + str(self.players[1].vp) + " - SP: " + str(self.players[1].sp)
        image = values.font30.render(text, True, self.players[1].colour)
        self.headerGroup.add(sprites.GameSprite(image, (1000, 0, image.get_width(), image.get_height())))
        
        #Display current turn and phase
        if self.phase == 0:
            phase = "Deployment"
        elif self.phase == 1:
            phase = "Movement Phase"
        elif self.phase == 2:
            phase = "Magic Phase"
        elif self.phase == 3:
            phase = "Shooting Phase"
        elif self.phase == 4:
            phase = "Charge Phase"
        elif self.phase == 6:
            phase = "Melee Phase"
        elif self.phase == 7:
            phase = "Morale Phase"
        text = "Turn " + str(self.turn[0]) + "/" + str(self.turn[1]) + " - " + phase
        x = sprites.centre_x(image.get_width(), 1280, 0)
        image = values.font30.render(text, True, values.colours["Lime"])
        self.headerGroup.add(sprites.GameSprite(image, (x, 0, image.get_width(), image.get_height())))
        
    def scroll(self, values, speed):
        
        if self.upPressed:
            self.yOffset = max(self.yOffset - speed, 0)
        if self.downPressed:
            self.yOffset = min(self.yOffset + speed, self.yOffsetMax)
        if self.leftPressed:
            self.xOffset = max(self.xOffset - speed, 0)
        if self.rightPressed:
            self.xOffset = min(self.xOffset + speed, self.xOffsetMax)
        if self.upPressed or self.downPressed or self.leftPressed or self.rightPressed:
            self.camera = self.surface.subsurface(self.xOffset, self.yOffset, 1280, 720)
            
    def toggle_highlighting(self):
        #Empty highlight group and set up dict for images
        self.highlightGroup.empty()
        images = {}
        
        #Loop through nodes
        for node in self.nodes:
            #If node is taken
            if self.nodes[node].takenBy != None:
                #If unit is in current player's army
                model = self.models[self.nodes[node].takenBy]
                unit = self.units[model.unitID]
                if unit.ID in self.currentTurn.units:
                    #If unit has ended the phase
                    if unit.endPhase:
                        #Grey highlight
                        imageName = "highlight_grey.png"
                    #Else, aqua highlight
                    else:
                        imageName = "highlight_aqua.png"
                #Else, if unit has ended the phase
                else:
                    #Orange highlight
                    if unit.endPhase:
                        imageName = "highlight_orange.png"
                    #Else, red highlight
                    else:
                        imageName = "highlight_red.png"
                
                #Add sprites to highlight group
                if imageName not in images:
                    images[imageName] = resources.load_primary_sprite(imageName)
                image = images[imageName]
                x = self.nodes[node].backSprite.rect.x
                y = self.nodes[node].backSprite.rect.y
                self.highlightGroup.add(sprites.GameSprite(image, (x, y, 32, 32)))    
                
    def update_control_point_status(self, values):
            
        #Loop through control points
        for i in range(0, 6):
            #Grab nodes within 3 squares
            nodes = self.get_movement_range(self.controlPoints[i], 0, 3, (1, 1), checkPassable=False,
                                            checkStandable=False)
            nodes.append(self.controlPoints[i])
            #Tally up models within range
            player1 = []
            player2 = []
            for node in nodes:
                if self.nodes[node].takenBy != None:
                    model = self.models[self.nodes[node].takenBy]
                    if model.ID in self.players[0].models and 'AIRBORNE' not in model.keywords:
                        if model.ID not in player1:
                            player1.append(model.ID)
                    elif model.ID in self.players[1].models and 'AIRBORNE' not in model.keywords:
                        if model.ID not in player2:
                            player2.append(model.ID)
                            
            #Get new assignment
            if len(player1) == 0 and len(player2) == 0:
                new = 0
                text = "Control point " + str(i + 1), " has been neutralised!"
            elif len(player1) > len(player2):
                new = 1
                text = self.players[0].name + " has captured control point " + str(i + 1) + "!"
            elif len(player1) < len(player2):
                new = 2
                text = self.players[1].name + " has captured control point " + str(i + 1) + "!"
            else:
                new = 3
                text = "Control point " + str(i + 1) + " is now contested!"
                
            #Replace assignment and update if necessary
            if new != self.controlPointStatus[i]:
                if new == 0 and self.controlPointStatus[i] in (1, 2):
                    pass
                else:
                    self.controlPointStatus[i] = new
                    self.update_event_log(values, text)
            
                
    def update_event_log(self, values, text=None, scroll=False, direction=0):
        
        redraw = True
        maxStrings = 14
        
        if scroll:
            newCounter = self.eventLogCounter + direction
            newCounter = max(newCounter, 0)
        
        else:
            #Cut text down
            newText = misc.cut_down_string(text, 80) #64 originally
            #Load text into list of strings
            for t in newText:
                self.eventLogText.append(t)
                #Advance counter by total of new strings
                self.eventLogCounter += 1
            
        #Apply maximum
        if scroll:
            #If length of string list is less or equal to max strings which can be shown, max is 0
            if len(self.eventLogText) < maxStrings:
                newCounter = 0
            #Else, max is len string list minus max which can be shown
            else:
                maximum = len(self.eventLogText) - maxStrings
                newCounter = min(newCounter, maximum)
                
            #Don't bother redrawing if scrolling is pointless
            if newCounter == self.eventLogCounter:
                redraw = False
            else:
                self.eventLogCounter = newCounter
        else:
            #If length of string list is less or equal to max strings which can be shown, max is 0
            if len(self.eventLogText) < maxStrings:
                self.eventLogCounter = 0
            #Else, max is len string list minus max which can be shown
            else:
                self.eventLogCounter = len(self.eventLogText) - maxStrings
            
        if redraw:

            self.eventLogGroup.empty()
            y = 0
            #Update sprites
            for i in range(self.eventLogCounter, len(self.eventLogText)):
                image = values.font20.render(self.eventLogText[i], True, values.colours["Black"])
                self.eventLogGroup.add(sprites.GameSprite(image, (0, y, image.get_width(), image.get_height())))
                y += image.get_height()
                
            #Add buttons back in
            for button in self.logButtons:
                if button.use in range(0, 2):
                    self.eventLogGroup.add(button.sprite)
            
    def update_main_message(self, values, text, otherPlayer=False):
        if self.mainMessage != None:
            self.mainMessage.kill()
        if not otherPlayer:
            colour = self.currentTurn.colour
        else:
            if self.players[0] == self.currentTurn:
                colour = self.players[1].colour
            else:
                colour = self.players[0].colour
        image = values.font20.render(text, True, colour)
        self.mainMessage = sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 420, 0), 0, 
                                                  image.get_width(), image.get_height()))
        self.commandListGroup.add(self.mainMessage)
        
    def update_melee_status(self, values):
        
        for unit in self.units:
            
            inMelee = False
            
            if unit in self.currentTurn.units:
                enemyPlayer = self.otherTurn
            else:
                enemyPlayer = self.currentTurn
                
            for model in self.units[unit].models:
                
                for node in model.nodes:
                    
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            node2 = (node[0] + x, node[1] + y)
                            if node2 in self.nodes:
                                if self.nodes[node2].takenBy != None:
                                    if self.nodes[node2].takenBy in enemyPlayer.models:
                                        inMelee = True
                                        break
                                
                        if inMelee:
                            break
                        
                    if inMelee:
                        break
                    
                if inMelee:
                    break
                
            if inMelee and not self.units[unit].inMelee:
                text = self.units[unit].name + " is now in melee."
                self.update_event_log(values, text)
                
                #In the melee phase, add newly engaged units to the melee list
                if self.phase == 6 and not self.units[unit].endPhase:
                    self.unitsForMelee[3].append(unit)
                
            elif not inMelee and self.units[unit].inMelee:
                text = self.units[unit].name + " is no longer in melee."
                self.update_event_log(values, text)
                
                #If in melee, remove non-engaged units from the melee list
                if self.phase == 6:
                    for p in self.unitsForMelee:
                        if unit in p:
                            p.remove(unit)
                
            self.units[unit].inMelee = inMelee
        
class LogButton:
    def __init__(self, use, image, rect):
        self.use = use
        self.sprite = sprites.GameSprite(image, rect)
        
            
class Node:
    def __init__(self):
        self.backSprite = None
        self.blocksLOS = False
        self.coordinates = None
        self.cover = 0
        self.foreSprite = None
        self.H = None
        self.takenBy = None #use model ID
        self.terrain = None
        self.walkable = True
        self.x = None
        self.y = None
        
class Objective:
    def __init__(self, name, ID):
        self.name = name
        self.ID = ID
        
class Player:
    def __init__(self, name, playerArmy, colour):
        self.armyWiped = False
        self.colour = colour
        self.currentObjectives = []
        self.deploymentZone = None
        self.deploymentZoneNodes = []
        self.discardedObjectives = []
        self.finishedDeployment = False
        self.models = [] 
        self.name = name
        self.objectivesAcheived = []
        self.objectivesDeck = [] #stack
        self.playerArmy = playerArmy
        self.sp = playerArmy.totalSP
        self.spellsUsed = []
        self.units = [] 
        self.vp = 0