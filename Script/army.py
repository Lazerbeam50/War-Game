'''
Created on 3 Sep 2018
@author: Femi
'''

import pygame
from pygame.locals import *

import copy
import eztext # @UnresolvedImport
import sqlite3

import codex # @UnresolvedImport
import misc # @UnresolvedImport
import resources # @UnresolvedImport
import sprites # @UnresolvedImport

class Army:
    def __init__(self):
        self.boss = None
        self.bossTrait = None
        self.codex = None
        self.detachments = []
        self.faction = None #(0 = Paladins, 1 = Orcs)
        self.name = "Enter Name"
        self.totalSP = 3
        self.totalPoints = 0
        
class ArmyManager:
    def __init__(self):
        self.armies = [] #Used to store armies during the load screen
        self.availableUnits = []
        self.bgColour = None
        self.bgImage = None
        self.currentDetachment = None
        self.currentModel = None
        self.currentOption = None
        self.currentUnit = None
        self.currentWargear = None
        self.downPressed = False
        self.group = pygame.sprite.LayeredUpdates()
        self.playerArmy = None
        self.screenSetUp = False
        self.state = 0
        self.surface = pygame.Surface((1280, 1490))
        self.textGroup = pygame.sprite.Group()
        self.textInput = None
        self.typing = False
        self.typingButton = None
        self.upPressed = False
        self.yOffset = 0
        
        self.camera = self.surface.subsurface(0, self.yOffset, 1280, 720)
        
    def update(self, values, event=None, typeText=None):
        
        if self.screenSetUp:
            if event != None:            
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        pos = (pos[0], pos[1] + self.yOffset)
                        clicked = False
                        for button in values.buttons[:]:
                            clicked = misc.is_point_inside_rect(pos[0], pos[1], button.rect)
                            if clicked:
                                if button.code == 0:
                                    
                                    self.playerArmy = Army()
                                    
                                    self.state = 1
                                    self.screenSetUp = False
                                    
                                #Load army button
                                elif button.code == 1:
                                    self.state = 7
                                    self.screenSetUp = False
                                    
                                #Quit army main screen
                                elif button.code == 2:
                                    values.state = 0
                                    self.state = 0
                                    self.screenSetUp = False
                                    self.group.empty()
                                    
                                #Select a faction from the faction selection screen
                                elif button.code == 3:
                                    #Change previous selected factions's colour to white
                                    if self.playerArmy.faction != None:
                                        image = values.font30.render(self.playerArmy.faction.storage.name,
                                                                     True, values.colours["White"])
                                        self.playerArmy.faction.sprites[1].image = image
                                        
                                    self.playerArmy.faction = button
                                    #Highlight current faction text lime green
                                    image = values.font30.render(self.playerArmy.faction.storage.name,
                                                                     True, values.colours["Lime"])
                                    self.playerArmy.faction.sprites[1].image = image
                                    
                                elif button.code == 4:
                                    #Confirm faction
                                    if self.playerArmy.faction != None:
                                        
                                        self.playerArmy.codex = get_codex(self.playerArmy.faction.storage.ID)
                                        
                                        if values.mageProfiles == None:
                                            db = sqlite3.connect('Game Data/game database') #connect to database
                                            cursor = db.cursor()
                                            
                                            cursor.execute('''SELECT id, itemNeeded, tier, mana, dispelLevel, 
                                            dispelCost FROM mage_profiles''')
                                            data = cursor.fetchall()
                                            values.mageProfiles = []
                                            for entry in data:
                                                obj = codex.MageProfile()
                                                obj.ID = misc.string_to_list(entry[0], True, True)
                                                obj.itemNeeded = misc.string_to_list(entry[1], True, True)
                                                obj.tier = entry[2]
                                                obj.mana = entry[3]
                                                obj.dispelLevel = entry[4]
                                                obj.dispelCost = entry[5]
                                                
                                                values.mageProfiles.append(obj)
                                        
                                        self.state = 2
                                        self.screenSetUp = False
                                        self.playerArmy.faction = self.playerArmy.faction.storage.ID
                                    
                                elif button.code == 5:
                                    self.state = 0
                                    self.screenSetUp = False
                                    self.playerArmy.faction = None
                                    
                                elif button.code == 6:
                                    self.typing = True #Turn on typing flag
                                    self.typingButton = button #Set button for easy access
                                    self.textInput.value = "" #Empty inputter value
                                    sprites.update_typed_text(values, self.textInput, 
                                                              button) #Update text sprite
                                
                                #save current army
                                elif button.code == 7:
                                    
                                    #create or connect to database
                                    db = sqlite3.connect('Save Data/save data')
                                    cursor = db.cursor()
                                    #set up saved armies table
                                    try:
                                        cursor.execute('''CREATE TABLE armies(name TEXT PRIMARY KEY, 
                                        bossTrait INTEGER, faction INTEGER, totalSP INTEGER, totalPoints INTEGER, 
                                        detachments TEXT)''')
                                    except sqlite3.OperationalError:
                                        pass
                                    #Set detachments up as stringed-list
                                    detachments = []
                                    for d in self.playerArmy.detachments:
                                        a = []
                                        a.append(d.name)
                                        a.append(d.detachmentType)
                                        a.append(d.points)
                                        a.append([])
                                        
                                        for u in d.units:
                                            b = []
                                            b.append(u.data)
                                            if u.dispelLevel == None:
                                                b.append(-1)
                                            else:
                                                b.append(u.dispelLevel)
                                            if u.dispelRate == None:
                                                b.append(-1)
                                            else:
                                                b.append(u.dispelRate)
                                            b.append(int(u.isBoss))
                                            b.append(tuple(u.keywords))
                                            b.append(tuple(u.options))
                                            b.append(int(u.sharedKeywords))
                                            b.append(tuple(u.spells))
                                            if u.currentMana == None:
                                                b.append(-1)
                                                b.append(-1)
                                            else:
                                                b.append(u.currentMana)
                                                b.append(u.maxMana)
                                            b.append(u.modelPoints)
                                            b.append(u.wargearPoints)
                                            b.append(u.totalPoints)
                                            b.append([])
                                            
                                            for m in u.models:
                                                c = []
                                                c.append(m.armour)
                                                c.append(m.attackSpeed)
                                                c.append(m.currentHP)
                                                c.append(m.data)
                                                c.append(m.fort)
                                                c.append(m.invul)
                                                c.append(tuple(m.keywords))
                                                c.append(m.mSkill)
                                                c.append(m.maxHP)
                                                c.append(m.maxMove)
                                                c.append(m.minMove)
                                                c.append(m.rSkill)
                                                c.append(m.strength)
                                                c.append(tuple(m.wargear))
                                                c.append(m.wargearPoints)
                                                c.append(m.will)
                                                
                                                c = tuple(c)
                                                b[13].append(c)
                                            
                                            b[13] = tuple(b[13])
                                            b = tuple(b)
                                            a[3].append(b)
                                        
                                        a[3] = tuple(a[3])
                                        a = tuple(a)
                                        detachments.append(a)
                                        
                                    detachments = tuple(detachments)
                                    print("Lets take a look!")
                                    #write army to database
                                    try:
                                        save_army(self.playerArmy, detachments, cursor)
                                    except sqlite3.IntegrityError:
                                        print("Army name taken. Overwriting.")
                                        cursor.execute('''DELETE FROM armies WHERE name = ? ''', 
                                                       (self.playerArmy.name,))
                                        save_army(self.playerArmy, detachments, cursor)
                                    db.commit()
                                        #if name is taken, delete old army and save new one
                                    print("Army saved")
                                elif button.code == 10:
                                    
                                    self.state = 0
                                    self.screenSetUp = False
                                    self.typing = False
                                    self.textInput = None
                                    
                                elif button.code == 11:
                                    if len(self.playerArmy.detachments) < 20:
                                        self.state = 3
                                        self.screenSetUp = False
                                    
                                #Select a detachment on the detachment creation screen
                                elif button.code == 12:
                                    #Empty the text group
                                    self.textGroup.empty()
                                    #Change previous selected detachment's colour to white
                                    if self.currentDetachment != None:
                                        image = values.font30.render(self.currentDetachment.storage.detachmentName,
                                                                     True, values.colours["White"])
                                        self.currentDetachment.sprites[1].image = image
                                        
                                    self.currentDetachment = button
                                    #Highlight current detachment text lime green
                                    image = values.font30.render(self.currentDetachment.storage.detachmentName,
                                                                     True, values.colours["Lime"])
                                    self.currentDetachment.sprites[1].image = image
                                    
                                    #Write out the detachment info
                                    text = self.currentDetachment.storage.detachmentName + " (+" + str(self.currentDetachment.storage.sp) + " SP)"
                                    image = values.font60.render(text, True, 
                                                                 values.colours["Black"])
                                    spr = sprites.GameSprite(image, (950, 150, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    
                                    if self.currentDetachment.storage.leaderMax == 0:
                                        text = "Leaders: None"
                                    else:
                                        text = "Leaders: " + str(self.currentDetachment.storage.leaderMin) + "-" + str(self.currentDetachment.storage.leaderMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 225, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.troopsMax == 0:
                                        text = "Troops: None"
                                    else:
                                        text = "Troops: " + str(self.currentDetachment.storage.troopsMin) + "-" + str(self.currentDetachment.storage.troopsMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 250, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.elitesMax == 0:
                                        text = "Elites: None"
                                    else:
                                        text = "Elites: " + str(self.currentDetachment.storage.elitesMin) + "-" + str(self.currentDetachment.storage.elitesMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 275, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.fastAttackMax == 0:
                                        text = "Fast Attack: None"
                                    else:
                                        text = "Fast Attack: " + str(self.currentDetachment.storage.fastAttackMin) + "-" + str(self.currentDetachment.storage.fastAttackMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 300, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.heavyMax == 0:
                                        text = "Heavy Support: None"
                                    else:
                                        text = "Heavy Support: " + str(self.currentDetachment.storage.heavyMin) + "-" + str(self.currentDetachment.storage.heavyMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 325, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.flyerMax == 0:
                                        text = "Air: None"
                                    else:
                                        text = "Air: " + str(self.currentDetachment.storage.flyerMin) + "-" + str(self.currentDetachment.storage.flyerMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 350, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.ultraMax == 0:
                                        text = "Ultras: None"
                                    else:
                                        text = "Ultras: " + str(self.currentDetachment.storage.ultraMin) + "-" + str(self.currentDetachment.storage.ultraMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 375, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.structureMax == 0:
                                        text = "Structures: None"
                                    else:
                                        text = "Structures: " + str(self.currentDetachment.storage.structureMin) + "-" + str(self.currentDetachment.storage.structureMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 400, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    if self.currentDetachment.storage.transportRule:
                                        text = "Transports: 1 per other unit"
                                    elif self.currentDetachment.storage.transportMax == 0:
                                        text = "Transports: None"
                                    else:
                                        text = "Transports: " + str(self.currentDetachment.storage.transportMin) + "-" + str(self.currentDetachment.storage.transportMax)
                                    image = values.font30.render(text, True, values.colours["Black"])
                                    spr = sprites.GameSprite(image, (850, 425, image.get_width(), image.get_height()))
                                    self.textGroup.add(spr)
                                    
                                #Confirm detachment
                                elif button.code == 13:
                                    if self.currentDetachment != None:
                                        self.state = 4
                                        self.screenSetUp = False
                                        self.currentDetachment = self.currentDetachment.storage
                                        self.playerArmy.detachments.append(self.currentDetachment)
                                
                                elif button.code == 14:
                                    self.state = 2
                                    self.screenSetUp = False
                                    self.currentDetachment = None
                                    
                                elif button.code == 15:
                                    self.typing = True #Turn on typing flag
                                    self.typingButton = button #Set button for easy access
                                    self.textInput.value = "" #Empty inputter value
                                    sprites.update_typed_text(values, self.textInput, 
                                                              button) #Update text sprite
                                
                                #deleting a detachment    
                                elif button.code == 16:
                                    self.state = 2
                                    self.screenSetUp = False
                                    self.typing = False
                                    self.textInput.value = self.playerArmy.name
                                    if self.playerArmy.boss in self.currentDetachment.units:
                                        self.playerArmy.boss.isBoss = False
                                        self.playerArmy.boss = None
                                    self.playerArmy.detachments.remove(self.currentDetachment)
                                    self.currentDetachment = None
                                    
                                elif button.code == 17:
                                    self.state = 2
                                    self.screenSetUp = False
                                    self.typing = False
                                    self.textInput.value = self.playerArmy.name
                                    self.currentDetachment = None
                                    
                                #Selecting a created detachment from the army display screen
                                elif button.code == 18:
                                    self.state = 4
                                    self.screenSetUp = False
                                    self.typing = False
                                    self.textInput.value = self.playerArmy.name
                                    self.currentDetachment = button.storage
                                    
                                #Add unit to detachment
                                elif button.code == 19:
                                    #Check if any units can be added at all
                                    counts, uniques = self.get_role_counts(True)
                                    allowed = {}
                                    
                                    if counts[0] in range(0, self.currentDetachment.leaderMax):
                                        allowed[0] = True
                                    else:
                                        allowed[0] = False
                                    if counts[1] in range(0, self.currentDetachment.troopsMax):
                                        allowed[1] = True
                                    else:
                                        allowed[1] = False
                                    if counts[2] in range(0, self.currentDetachment.elitesMax):
                                        allowed[2] = True
                                    else:
                                        allowed[2] = False
                                    if counts[3] in range(0, self.currentDetachment.fastAttackMax):
                                        allowed[3] = True
                                    else:
                                        allowed[3] = False
                                    if counts[4] in range(0, self.currentDetachment.heavyMax):
                                        allowed[4] = True
                                    else:
                                        allowed[4] = False
                                    if self.currentDetachment.transportRule:
                                        maxTransport = counts[9]
                                    else:
                                        maxTransport = self.currentDetachment.transportMax
                                    if counts[5] in range(0, maxTransport):
                                        allowed[5] = True
                                    else:
                                        allowed[5] = False
                                    if counts[6] in range(0, self.currentDetachment.flyerMax):
                                        allowed[6] = True
                                    else:
                                        allowed[6] = False
                                    if counts[7] in range(0, self.currentDetachment.structureMax):
                                        allowed[7] = True
                                    else:
                                        allowed[7] = False
                                    if counts[8] in range(0, self.currentDetachment.ultraMax):
                                        allowed[8] = True
                                    else:
                                        allowed[8] = False
                                    
                                    self.availableUnits = []
                                    
                                    for unit in self.playerArmy.codex.units:
                                        role = self.playerArmy.codex.units[unit].bfRole
                                        if allowed[role]:
                                            approved = True
                                            for model in self.playerArmy.codex.units[unit].defaultModels:
                                                modelData = self.playerArmy.codex.models[(self.playerArmy.faction, model)]
                                                for keyword in uniques:
                                                    if keyword in modelData.keywords:
                                                        approved = False
                                                        break
                                            if approved:
                                                self.availableUnits.append(unit)
                                            
                                            
                                    #If so, proceed to unit creation
                                    if len(self.availableUnits) > 0:
                                        self.state = 5
                                        self.screenSetUp = False
                                        
                                #Select a unit on the creation screen
                                elif button.code == 20:
                                    #Change previous selected unit's colour to white
                                    if self.currentUnit != None:
                                        image = values.font30.render(self.currentUnit.storage.title,
                                                                     True, values.colours["White"])
                                        self.currentUnit.sprites[1].image = image
                                        
                                    self.currentUnit = button
                                    #Highlight current unit text lime green
                                    image = values.font30.render(self.currentUnit.storage.title,
                                                                     True, values.colours["Lime"])
                                    self.currentUnit.sprites[1].image = image
                                    
                                #Confirm unit selection
                                elif button.code == 21:
                                    if self.currentUnit != None:
                                        self.state = 6
                                        self.screenSetUp = False
                                        self.currentUnit = Unit(self.currentUnit.storage, self.playerArmy.codex,
                                                                values.mageProfiles)
                                        self.currentDetachment.units.append(self.currentUnit)
                                        
                                    
                                #Back out of unit creation    
                                elif button.code == 22:
                                    self.state = 4
                                    self.screenSetUp = False
                                    self.currentUnit = None
                                    
                                #Confirm unit on unit display screen
                                elif button.code == 23:
                                    
                                    #recalculate points
                                    self.currentDetachment.calculate_points()
                                    
                                    self.state = 4
                                    self.screenSetUp = False
                                    self.currentUnit = None
                                    
                                #Make unit the boss
                                elif button.code == 24:
                                    #If player has already picked a unit to be the boss, set their boss flag to false
                                    if self.playerArmy.boss != None:
                                        self.playerArmy.boss.isBoss = False
                                    self.playerArmy.boss = self.currentUnit
                                    self.playerArmy.boss.isBoss = True
                                
                                #Delete unit
                                elif button.code == 26:
                                    
                                    self.state = 4
                                    self.screenSetUp = False
                                    self.currentDetachment.units.remove(self.currentUnit)
                                    #recalculate points
                                    self.currentDetachment.calculate_points()
                                    if self.currentUnit == self.playerArmy.boss:
                                        self.playerArmy.boss = None
                                    self.currentUnit = None
                                  
                                #Selecting a created unit from the detachment display screen  
                                elif button.code == 27:
                                    self.state = 6
                                    self.screenSetUp = False
                                    self.typing = False
                                    self.textInput.value = self.currentDetachment.name
                                    self.currentUnit = button.storage
                                    
                                #Adding a model to a unit
                                elif button.code == 28:
                                    #Count the number of times this option has been used
                                    count = 0
                                    for o in self.currentUnit.options:
                                        if o == button.storage.ID:
                                            count += 1
                                    if count < button.storage.maximum:
                                        #Add model to unit if below maximum
                                        for m in button.storage.gaining:
                                            modelData = self.playerArmy.codex.models[(self.playerArmy.faction, m)]
                                            model = Model(modelData, self.playerArmy.codex)
                                            self.currentUnit.models.append(model)
                                        self.currentUnit.reset_points(self.playerArmy.codex)
                                        self.currentDetachment.calculate_points()
                                        #Add option code to unit's options
                                        self.currentUnit.options.append(button.storage.ID)
                                        #Refresh screen
                                        self.screenSetUp = False
                                        
                                #Add wargear to a unit
                                elif button.code == 29:
                                    #count the number of times this option has been used
                                    count = 0
                                    for o in self.currentUnit.options:
                                        if o == button.storage.ID:
                                            count += 1
                                    if count < button.storage.maximum or button.storage.maximum == 0:
                                        #count the number of receiving models in the current unit
                                        rm = 0
                                        for m in self.currentUnit.models:
                                            approved = True
                                            for wargear in button.storage.requires:
                                                if wargear not in m.wargear:
                                                    approved = False
                                            for wargear in button.storage.replacing:
                                                if wargear not in m.wargear:
                                                    approved = False
                                            if approved and m.data[1] == button.storage.receivingModel:
                                                rm += 1
                                                model = m
                                        #if there is only one receiving model in the unit and only one type of wargear is being given
                                        if rm == 1 and button.storage.optionType == 1:
                                            #Replace the old wargear, if needed
                                            for wargear in button.storage.replacing:
                                                if wargear in model.wargear:
                                                    model.wargear.remove(wargear)
                                            #If new wargear is a invul shield, check to see if model has a shield already
                                            isShield = False
                                            if self.playerArmy.codex.wargear[self.playerArmy.codex.ID, button.storage.gaining[0]].gearType == 7:
                                                isShield = True
                                                hasShield = False
                                                for wargear in model.wargear:
                                                    if self.playerArmy.codex.wargear[self.playerArmy.codex.ID, wargear].gearType == 7:
                                                        hasShield = True
                                                        shield = self.playerArmy.codex.wargear[self.playerArmy.codex.ID, wargear]
                                                        break
                                                #If so, remove shield from inventory and set invul save to default
                                                if hasShield:
                                                    model.wargear.remove(shield.ID[1])
                                                    model.invul = self.playerArmy.codex.models[model.data].invul
                                            #Apply bonus from new shield
                                            if isShield:
                                                model.invul = self.playerArmy.codex.wargear[self.playerArmy.codex.ID, button.storage.gaining[0]].strength
                                            #Add the new wargear
                                            for wargear in button.storage.gaining:
                                                model.wargear.append(wargear)
                                            #Update mage profile if necessary
                                            if 'MAGE' in self.currentUnit.keywords:
                                                for mp in values.mageProfiles:
                                                    if (mp.ID == self.currentUnit.data and 
                                                        mp.itemNeeded == (self.playerArmy.codex.ID, button.storage.gaining[0])):
                                                        print("Received!")
                                                        self.currentUnit.dispelLevel = mp.dispelLevel
                                                        self.currentUnit.dispelRate = mp.dispelCost
                                                        self.currentUnit.currentMana = self.currentUnit.maxMana = mp.mana
                                                        break
                                            model.reset_points(self.playerArmy.codex)
                                            self.currentUnit.reset_points(self.playerArmy.codex)
                                            self.currentDetachment.calculate_points()
                                            #Add option code to unit's options
                                            self.currentUnit.options.append(button.storage.ID)
                                            #Refresh screen
                                            self.screenSetUp = False
                                            
                                        #If multiple models can receive wargear or the target is a list, move to next screen
                                        elif rm > 1 or (button.storage.optionType == 2 and rm > 0):
                                            self.currentOption = button.storage
                                            self.state = 8
                                            self.screenSetUp = False
                                            
                                        
                                #Add a spell to a unit
                                elif button.code == 30:
                                    if (len(self.currentUnit.spells) < 3 and 
                                        button.storage.ID not in self.currentUnit.spells):
                                        self.currentUnit.spells.append(button.storage.ID)
                                        #Refresh screen
                                        self.screenSetUp = False
                                        
                                #Army selected from load menu
                                elif button.code == 31:
                                    self.playerArmy = button.storage
                                    self.state = 2
                                    self.screenSetUp = False
                                    
                                #Confirm button on wargear selection screen
                                elif button.code == 32:
                                    
                                    if self.currentModel != None and self.currentWargear != None:
                                        
                                        #If new wargear is a invul shield, check to see if model has a shield already
                                        isShield = False
                                        if self.playerArmy.codex.wargear[self.playerArmy.codex.ID, self.currentWargear.storage[0]].gearType == 7:
                                            isShield = True
                                            hasShield = False
                                            for wargear in self.currentModel.storage[0].wargear:
                                                if self.playerArmy.codex.wargear[self.playerArmy.codex.ID, wargear].gearType == 7:
                                                    hasShield = True
                                                    shield = self.playerArmy.codex.wargear[self.playerArmy.codex.ID, wargear]
                                                    break
                                            #If so, remove shield from inventory and set invul save to default
                                            if hasShield:
                                                self.currentModel.storage[0].wargear.remove(shield.ID[1])
                                                self.currentModel.storage[0].invul = self.playerArmy.codex.models[self.currentModel.storage[0].data].invul
                                        #Apply bonus from new shield
                                        if isShield:
                                            self.currentModel.storage[0].invul = self.playerArmy.codex.wargear[self.playerArmy.codex.ID, 
                                                                                                    self.currentWargear.storage[0]].strength
                                    
                                        #Replace the old wargear, if needed
                                        for wargear in self.currentOption.replacing:
                                            if wargear in self.currentModel.storage[0].wargear:
                                                self.currentModel.storage[0].wargear.remove(wargear)
                                        #Add the new wargear
                                        self.currentModel.storage[0].wargear.append(self.currentWargear.storage[0])
                                        self.currentModel.storage[0].reset_points(self.playerArmy.codex)
                                        self.currentUnit.reset_points(self.playerArmy.codex)
                                        self.currentDetachment.calculate_points()
                                        #Add option code to unit's options
                                        self.currentUnit.options.append(self.currentOption.ID)
                                        
                                        #Clean up variables
                                        self.currentOption = None
                                        self.currentModel = None
                                        self.currentWargear = None
                                        
                                        #Refresh screen
                                        self.state = 6
                                        self.screenSetUp = False
                                    
                                #Back button on wargear selection screen
                                elif button.code == 33:
                                    
                                    #Clean up variables
                                    self.currentOption = None
                                    self.currentModel = None
                                    self.currentWargear = None
                                    
                                    #Refresh screen
                                    self.state = 6
                                    self.screenSetUp = False
                                    
                                #Select model to receive wargear
                                elif button.code == 34:
                                    #If selected button is not the current model
                                    if self.currentModel != button:
                                        if self.currentModel != None:
                                            image = values.font20.render(self.currentModel.storage[1], True, values.colours["White"])
                                            self.currentModel.sprites[1].image = image
                                            
                                        #Set button as current model
                                        self.currentModel = button
                                        image = values.font20.render(self.currentModel.storage[1], True, values.colours["Lime"])
                                        self.currentModel.sprites[1].image = image
                                        
                                        self.get_wargear_screen_info(values)
                                        
                                #Select wargear to give to model
                                elif button.code == 35:
                                    #If selected button is not the current wargear
                                    if self.currentWargear != button:
                                        if self.currentWargear != None:
                                            image = values.font20.render(self.currentWargear.storage[1], True, values.colours["White"])
                                            self.currentWargear.sprites[1].image = image
                                            
                                        #Set button as current wargear
                                        self.currentWargear = button
                                        image = values.font20.render(self.currentWargear.storage[1], True, values.colours["Lime"])
                                        self.currentWargear.sprites[1].image = image
                                        
                                        self.get_wargear_screen_info(values)
                                                                    
                elif event.type == KEYDOWN:
                    if event.key == K_UP:
                        self.downPressed = False
                        self.upPressed = True
                    elif event.key == K_DOWN:
                        self.upPressed = False
                        self.downPressed = True
                    elif event.key == ord('y'):
                        print(self.yOffset)
                
                elif event.type == KEYUP:
                    if event.key == K_UP:
                        self.upPressed = False
                    elif event.key == K_DOWN:
                        self.downPressed = False
                        
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.upPressed = True
                        self.scroll(values, 20)
                        self.upPressed = False
                    elif event.button == 5:
                        self.downPressed = True
                        self.scroll(values, 20)
                        self.downPressed = False
                        
            else:
                #Scrolling
                self.scroll(values, 10)
        
        else:
            self.group.empty()
            self.textGroup.empty()
            values.buttons = []
            self.bgColour = None
            self.bgImage = None
            self.yOffset = 0
            self.camera = self.surface.subsurface(0, self.yOffset, 1280, 720)
            
            if self.state == 0:
                
                if self.textInput == None:
                    self.textInput = eztext.Input(maxlength=25, color=values.colours["White"],
                                                  prompt='_', font=values.font30)
                
                self.set_up_army_main_screen(values)
                
            elif self.state == 1:
                self.set_up_army_faction_screen(values)
                
            elif self.state == 2:
                self.set_up_army_display_screen(values)
                
            elif self.state == 3:
                self.set_up_detachment_creation_screen(values)
                
            elif self.state == 4:
                self.set_up_detachment_display_screen(values)
                
            elif self.state == 5:
                self.set_up_unit_creation_screen(values)
                
            elif self.state == 6:
                self.set_up_unit_display_screen(values)
            
            elif self.state == 7:
                self.set_up_army_load_screen(values)
                
            elif self.state == 8:
                self.set_up_wargear_screen(values)
                
            self.screenSetUp = True
        
        if self.typing:
            
            #Update the text sprite
            sprites.update_typed_text(values, self.textInput, self.typingButton)
            
            if typeText != None:
                #Only reset the string if the user typed something new in
                if typeText != "":
                    if self.state == 2:
                        self.playerArmy.name = typeText
                    elif self.state == 4:
                        self.currentDetachment.name = typeText
                else:
                    if self.state == 2:
                        self.textInput.value = self.playerArmy.name
                    elif self.state == 4:
                        self.textInput.value = self.currentDetachment.name
                    sprites.update_typed_text(values, self.textInput, self.typingButton)
                    
                self.typing = False
                self.typingButton = None
            
    def set_up_army_main_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        image = values.font90.render("Army Setup", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (400, 100))
        x = sprites.centre_x(400, values.settings.width, 0)
        
        button = sprites.Button(0, 1, image, (x, 200, 400, 100), "Create Army", values.font60, values)
        button = sprites.Button(1, 1, image, (x, 325, 400, 100), "Load Army", values.font60, values)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (300, 50))
        x = sprites.centre_x(300, values.settings.width, 0)
        
        button = sprites.Button(2, 1, image, (x, 600, 300, 50), "Quit", values.font30, values)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
        if values.mageProfiles == None:
            db = sqlite3.connect('Game Data/game database') #connect to database
            cursor = db.cursor()
            
            cursor.execute('''SELECT id, itemNeeded, tier, mana, dispelLevel, 
            dispelCost FROM mage_profiles''')
            data = cursor.fetchall()
            values.mageProfiles = []
            for entry in data:
                obj = codex.MageProfile()
                obj.ID = misc.string_to_list(entry[0], True, True)
                obj.itemNeeded = misc.string_to_list(entry[1], True, True)
                obj.tier = entry[2]
                obj.mana = entry[3]
                obj.dispelLevel = entry[4]
                obj.dispelCost = entry[5]
                
                values.mageProfiles.append(obj)
            
    def set_up_army_faction_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        image = values.font90.render("Select a faction", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (200, 100))
        x = 50
        y = 200
        
        for faction in values.factions:
            
            button = sprites.Button(3, 1, image, (x, y, 200, 100), faction.name, 
                                    values.font30, values, storage=faction)
        
            y += 100
            if y > 600:
                y = 200
                x += 225
                
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (150, 50))
                
        button = sprites.Button(4, 1, image, (1100, 600, 150, 50), "Confirm", values.font20, values)
        button = sprites.Button(5, 1, image, (1100, 650, 150, 50), "Back", values.font20, values)
            
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def set_up_army_display_screen(self, values):
        
        self.bgColour = values.colours["Beige"]

        text = self.playerArmy.name
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (400, 100))
        x = sprites.centre_x(400, values.settings.width, 0)
        
        button = sprites.Button(6, 1, image, (x, 50, 400, 100), text, values.font30, values)
        
        buttonImage = resources.load_secondary_sprite("button01.png")
        buttonImage01 = pygame.transform.scale(buttonImage, (150, 50))
        
        button = sprites.Button(7, 1, buttonImage01, (900, 0, 150, 50), "Save Army", values.font20, values)
        button = sprites.Button(8, 1, buttonImage01, (900, 70, 150, 50), "Delete Army", values.font20, values)
        button = sprites.Button(9, 1, buttonImage01, (1070, 0, 150, 50), "Copy Army", values.font20, values)
        button = sprites.Button(10, 1, buttonImage01, (1070, 70, 150, 50), "Back", values.font20, values)
            
        spriteList = []   
            
        #Add faction text
        text = "Faction: " + values.factions[self.playerArmy.faction].name
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 25, image.get_width(), image.get_height())))
        
        #Add boss text
        if self.playerArmy.boss == None:
            text = "None"
        else:
            unitData = self.playerArmy.codex.units[self.playerArmy.boss.data]
            text = unitData.title
        text2 = "Boss: " + text
        image = values.font30.render(text2, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 50, image.get_width(), image.get_height())))
        
        self.playerArmy.totalSP = 3
        
        for d in self.playerArmy.detachments:
            self.playerArmy.totalSP += d.sp
        
        text = "Total SP: " + str(self.playerArmy.totalSP)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 75, image.get_width(), image.get_height())))
        
        self.playerArmy.totalPoints = 0
        
        for d in self.playerArmy.detachments:
            self.playerArmy.totalPoints += d.points
        
        text = "Total Army Points: " + str(self.playerArmy.totalPoints)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 100, image.get_width(), image.get_height())))
        
        image = values.font60.render("DETACHMENTS", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spriteList.append(sprites.GameSprite(image, (x, 250, image.get_width(), image.get_height())))
        
        if len(self.playerArmy.detachments) == 0:
            y = 350
        else:
            #Set up table headings
            image = values.font30.render("Name", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (20, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("Type", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (320, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("SP", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (620, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("Points", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (920, 350, image.get_width(), image.get_height())))
            
            y = 400
            #Set up each detachment as data
            for d in self.playerArmy.detachments:
                buttonImage01 = pygame.transform.scale(buttonImage, (280, 40))
                button = sprites.Button(18, 1, buttonImage01, (20, y - 10, 280, 50), d.name, values.font20, values, storage=d)
                image = values.font30.render(d.detachmentName, True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (320, y, image.get_width(), image.get_height())))
                image = values.font30.render(str(d.sp), True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (620, y, image.get_width(), image.get_height())))
                image = values.font30.render(str(d.points), True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (920, y, image.get_width(), image.get_height())))
                
                y += 50
        
        buttonImage01 = pygame.transform.scale(buttonImage, (800, 50))
        x = sprites.centre_x(800, values.settings.width, 0)
        button = sprites.Button(11, 1, buttonImage01, (x, y + 20, 800, 50), "Create Detachment", values.font20, values)
        
        self.group.add(spriteList)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def set_up_army_load_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        longPanelImage = resources.load_secondary_sprite("long_panel01.png")
        panel01Image = pygame.transform.scale(longPanelImage, (270, 595))
        self.group.add(sprites.GameSprite(panel01Image, (50, 75, 270, 595)))
        
        image = values.font90.render("Select an army to load", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        widePanelImage = resources.load_secondary_sprite("wide_panel01.png")
        buttonImage = pygame.transform.scale(widePanelImage, (255, 25))
        x = sprites.centre_x(255, 270, 50)
        y = 85
        
        db = sqlite3.connect('Save Data/save data') #connect to database
        cursor = db.cursor()
        
        cursor.execute('''SELECT name, bossTrait, faction, totalSP, totalPoints, detachments FROM armies''')
        data = cursor.fetchall()
        self.armies = get_army_lists(data)
        
        #Set up buttons for list
        for a in self.armies:
            button = sprites.Button(31, 1, buttonImage, (x, y, 255, 25), a.name, values.font20, values, storage=a)
            y += 25
            self.group.add(button.sprites)
            
    def set_up_detachment_creation_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        detachments = get_detachment_list()
        
        image = values.font90.render("Select a detachment", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (200, 50))
        x = 50
        y = 200
        
        for d in detachments:
            button = sprites.Button(12, 1, image, (x, y, 200, 50), d.detachmentName, 
                                    values.font30, values, storage=d)
        
            y += 50
            if y > 600:
                y = 200
                x += 225
                
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (150, 50))
                
        button = sprites.Button(13, 1, image, (1100, 600, 150, 50), "Confirm", values.font20, values)
        button = sprites.Button(14, 1, image, (1100, 650, 150, 50), "Back", values.font20, values)
            
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def set_up_detachment_display_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        text = self.currentDetachment.name
            
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (400, 100))
        x = sprites.centre_x(400, values.settings.width, 0)
        
        button = sprites.Button(15, 1, image, (x, 50, 400, 100), text, values.font30, values)
        
        buttonImage = resources.load_secondary_sprite("button01.png")
        buttonImage01 = pygame.transform.scale(buttonImage, (150, 50))
        
        button = sprites.Button(16, 1, buttonImage01, (900, 0, 150, 50), "Delete Detachment", values.font20, values)
        button = sprites.Button(17, 1, buttonImage01, (1070, 0, 150, 50), "Back", values.font20, values)
        
        spriteList = []
        
        #Display Detachment type
        text = "Detachment Type: " + self.currentDetachment.detachmentName
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 25, image.get_width(), image.get_height())))
        
        #Display SP
        text = "SP: " + str(self.currentDetachment.sp)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 50, image.get_width(), image.get_height())))
        
        #Display Points
        text = "Total Points: " + str(self.currentDetachment.points)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 75, image.get_width(), image.get_height())))
        
        #Display role quotas
        
        #Loop through units to count quotas
        
        counts = self.get_role_counts()
                
        #Display counts against quotas
        if counts[0] < self.currentDetachment.leaderMin:
            diff = self.currentDetachment.leaderMin - counts[0]
            text = "Leaders: " + str(counts[0]) + "/" + str(self.currentDetachment.leaderMax) + " (" + str(diff) + " more leaders needed)"
        else:
            text = "Leaders: " + str(counts[0]) + "/" + str(self.currentDetachment.leaderMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 175, image.get_width(), image.get_height())))
        
        if counts[1] < self.currentDetachment.troopsMin:
            diff = self.currentDetachment.troopsMin - counts[1]
            text = "Troops: " + str(counts[1]) + "/" + str(self.currentDetachment.troopsMax) + " (" + str(diff) + " more troops needed)"
        else:
            text = "Troops: " + str(counts[1]) + "/" + str(self.currentDetachment.troopsMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 200, image.get_width(), image.get_height())))
        
        if counts[2] < self.currentDetachment.elitesMin:
            diff = self.currentDetachment.elitesMin - counts[2]
            text = "Elites: " + str(counts[2]) + "/" + str(self.currentDetachment.elitesMax) + " (" + str(diff) + " more elites needed)"
        else:
            text = "Elites: " + str(counts[2]) + "/" + str(self.currentDetachment.elitesMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 225, image.get_width(), image.get_height())))
        
        if counts[3] < self.currentDetachment.fastAttackMin:
            diff = self.currentDetachment.fastAttackMin - counts[3]
            text = "Fast Attack: " + str(counts[3]) + "/" + str(self.currentDetachment.fastAttackMax) + " (" + str(diff) + " more fast attackers needed)"
        else:
            text = "Fast Attack: " + str(counts[3]) + "/" + str(self.currentDetachment.fastAttackMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 250, image.get_width(), image.get_height())))
        
        if counts[4] < self.currentDetachment.heavyMin:
            diff = self.currentDetachment.heavyMin - counts[4]
            text = "Heavy Support: " + str(counts[4]) + "/" + str(self.currentDetachment.heavyMax) + " (" + str(diff) + " more heavies needed)"
        else:
            text = "Heavy Support: " + str(counts[4]) + "/" + str(self.currentDetachment.heavyMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 275, image.get_width(), image.get_height())))
        
        if counts[6] < self.currentDetachment.flyerMin:
            diff = self.currentDetachment.flyerMin - counts[6]
            text = "Air: " + str(counts[6]) + "/" + str(self.currentDetachment.flyerMax) + " (" + str(diff) + " more air units needed)"
        else:
            text = "Air: " + str(counts[6]) + "/" + str(self.currentDetachment.flyerMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (500, 175, image.get_width(), image.get_height())))
        
        if self.currentDetachment.transportRule:
            text = "Transports: " + str(counts[5]) + "/" + str(counts[9])
        else:
            text = "Transports: " + str(counts[5]) + "/" + str(self.currentDetachment.transportMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (500, 200, image.get_width(), image.get_height())))
        
        if counts[7] < self.currentDetachment.structureMin:
            diff = self.currentDetachment.structureMin - counts[7]
            text = "Structures: " + str(counts[7]) + "/" + str(self.currentDetachment.structureMax) + " (" + str(diff) + " more structures needed)"
        else:
            text = "Structures: " + str(counts[7]) + "/" + str(self.currentDetachment.structureMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (500, 225, image.get_width(), image.get_height())))
        
        if counts[8] < self.currentDetachment.ultraMin:
            diff = self.currentDetachment.ultraMin - counts[8]
            text = "Ultras: " + str(counts[8]) + "/" + str(self.currentDetachment.ultraMax) + " (" + str(diff) + " more ultras needed)"
        else:
            text = "Ultras: " + str(counts[8]) + "/" + str(self.currentDetachment.ultraMax)
        image = values.font30.render(text, True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (500, 250, image.get_width(), image.get_height())))
        
        if len(self.currentDetachment.units) == 0:
            y = 350
        else:
            #Set up table headings
            image = values.font30.render("Title", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (20, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("Role", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (320, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("No. of Models", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (520, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("Model Points", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (720, 350, image.get_width(), image.get_height())))
            
            image = values.font30.render("Wargear Points", True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (920, 350, image.get_width(), image.get_height())))
            
            y = 400
            #Set up each unit as data
            for u in self.currentDetachment.units:
                unitData = self.playerArmy.codex.units[u.data]
                buttonImage01 = pygame.transform.scale(buttonImage, (280, 40))
                button = sprites.Button(27, 1, buttonImage01, (20, y - 10, 280, 50), unitData.title, values.font20, values, storage=u)
                image = values.font30.render(unitData.bfRoleText, True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (320, y, image.get_width(), image.get_height())))
                image = values.font30.render(str(len(u.models)), True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (520, y, image.get_width(), image.get_height())))
                image = values.font30.render(str(u.modelPoints), True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (720, y, image.get_width(), image.get_height())))
                image = values.font30.render(str(u.wargearPoints), True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (920, y, image.get_width(), image.get_height())))
                
                y += 50
                
        buttonImage01 = pygame.transform.scale(buttonImage, (800, 50))
        x = sprites.centre_x(800, values.settings.width, 0)
        button = sprites.Button(19, 1, buttonImage01, (x, y + 20, 800, 50), "Add unit", values.font20, values)
        
        self.group.add(spriteList)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
    def set_up_unit_creation_screen(self, values):
         
        self.bgColour = values.colours["Beige"]
        
        spriteList = []
        
        image = values.font90.render("Select a unit", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spr = sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height()))
        self.group.add(spr)
        
        #Set up table headings
        image = values.font30.render("Title", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (180, 200, image.get_width(), image.get_height())))
        
        image = values.font30.render("Role", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (440, 200, image.get_width(), image.get_height())))
        
        image = values.font30.render("No. of models", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (680, 200, image.get_width(), image.get_height())))
        
        image = values.font30.render("Base points", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (920, 200, image.get_width(), image.get_height())))
        
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (300, 50))
        y = 250
        
        for u in self.availableUnits:
            unit = self.playerArmy.codex.units[u]
            button = sprites.Button(20, 1, image, (50, y, 300, 50), unit.title, 
                                    values.font30, values, storage=unit)
            image2 = values.font30.render(unit.bfRoleText, True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image2, (440, y + 15, image2.get_width(), image2.get_height())))
            image2 = values.font30.render(str(len(unit.defaultModels)), True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image2, (730, y + 15, image2.get_width(), image2.get_height())))
            image2 = values.font30.render(str(unit.basePoints), True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image2, (960, y + 15, image2.get_width(), image2.get_height())))
        
            y += 50
                
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (150, 50))
                
        button = sprites.Button(21, 1, image, (1100, 0, 150, 50), "Confirm", values.font20, values)
        button = sprites.Button(22, 1, image, (1100, 50, 150, 50), "Back", values.font20, values)
        
            
        for button in values.buttons:
            self.group.add(button.sprites)
            
        self.group.add(spriteList)
        
    def set_up_unit_display_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        spriteList = []
        unitData = self.playerArmy.codex.units[self.currentUnit.data]
        
        image = values.font60.render(unitData.title, True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spriteList.append(sprites.GameSprite(image, (x, 50, image.get_width(), image.get_height())))
        
        text = unitData.bfRoleText + " - " + str(len(self.currentUnit.models)) + " model(s) - " + str(self.currentUnit.modelPoints) + " model points - " + str(self.currentUnit.wargearPoints) + " wargear points - " + str(self.currentUnit.totalPoints) + " total points - "
        image = values.font30.render(text, True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spriteList.append(sprites.GameSprite(image, (x, 120, image.get_width(), image.get_height())))
        
        image = values.font20.render("Name", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("HP", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (200, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("Move", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (270, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("M Skill", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (340, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("R Skill", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (410, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("AS", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (480, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("Str", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (550, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("Fort", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (620, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("Will", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (690, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("Armour", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (760, 180, image.get_width(), image.get_height())))
        
        image = values.font20.render("Invul", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (830, 180, image.get_width(), image.get_height())))
        
        models = []
        y = 210
        for model in self.currentUnit.models:
            if model.data not in models:
                models.append(model.data)
                md = self.playerArmy.codex.models[model.data]
                quant = 0
                for ml in self.currentUnit.models:
                    if ml.data == model.data:
                        quant += 1
                if md.minMove == 0:
                    move = str(md.maxMove)
                else:
                    move = str(md.minMove) + "-" + str(md.maxMove)
                name = md.name + " x" + str(quant)
                text = [name, str(md.hp), move, str(md.mSkill), str(md.rSkill), str(md.attackSpeed), str(md.strength),
                        str(md.fort), str(md.will), str(md.armour), str(md.invul)]
                x = [15, 205, 280, 355, 425, 485, 555, 630, 700, 770, 840]
                for i in range(0, 11):
                    image = values.font20.render(text[i], True, values.colours["Black"])
                    spriteList.append(sprites.GameSprite(image, (x[i], y, image.get_width(), image.get_height())))
                
                y += 20
            
        #Black seperator bar
        image = pygame.Surface((1280, 5))
        spriteList.append(sprites.GameSprite(image, (0, y, 1280, 5)))
        
        y += 20
        
        image = values.font20.render("Weapon", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (20, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("Type", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (200, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("Range", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (270, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("Shots", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (340, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("Strength", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (410, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("AP", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (550, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("Damage", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (620, y, image.get_width(), image.get_height())))
        
        image = values.font20.render("Abilities", True, values.colours["Black"])
        spriteList.append(sprites.GameSprite(image, (690, y, image.get_width(), image.get_height())))
        
        wargear = []
        quantity = {}
        y += 20
        for model in self.currentUnit.models:
            for weapon in model.wargear:
                if weapon not in wargear:
                    wargear.append(weapon)
                    quantity[weapon] = 1
                else:
                    quantity[weapon] += 1
                    
        for weapon in wargear:
            weaponData = self.playerArmy.codex.wargear[(self.playerArmy.faction, weapon)]
            name = weaponData.name + " x" + str(quantity[weapon])
            if weaponData.gearType == 0:
                attackRange = "Melee"
                weaponType = "Melee"
                shots = "N/A"
                if weaponData.userStrength:
                    if weaponData.strengthPlus != 0:
                        strength = "User STR + " + str(weaponData.strengthPlus)
                    elif weaponData.strengthMultiplier != 0:
                        strength = "User STR x " + str(weaponData.strengthMultiplier)
                    else:
                        strength = "User STR"
                else:
                    strength = str(weaponData.strength)
                
            else:
                attackRange = str(weaponData.attackRange)
                shots = str(weaponData.shots)
                strength = str(weaponData.strength)
                if weaponData.gearType == 1:
                    weaponType = "Assault"
                elif weaponData.gearType == 2:
                    weaponType = "Heavy"
                elif weaponData.gearType == 3:
                    weaponType = "Rapid Fire"
                elif weaponData.gearType == 4:
                    weaponType = "Grenade"
                elif weaponData.gearType == 5:
                    weaponType = "Pistol"
                else:
                    weaponType = "Other"
                    attackRange = "N/A"
                    shots = "N/A"
                    strength = "N/A"
                    
            abilities = ""
            for ab in weaponData.abilities:
                abilities += ab
                abilities += ", "
            
            text = [name, weaponType, attackRange, shots, strength, str(weaponData.ap), str(weaponData.damage),
                    abilities]
            x = [15, 205, 280, 355, 425, 555, 630, 700, 770, 840]
            for i in range(0, 8):
                image = values.font20.render(text[i], True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (x[i], y, image.get_width(), image.get_height())))
                
            y += 20
            
        if len(self.currentUnit.spells) > 0:
            #Black separator bar
            image = pygame.Surface((1280, 5))
            spriteList.append(sprites.GameSprite(image, (0, y, 1280, 5)))
            
            #Add abilities header
            image = values.font30.render("Spells", True, values.colours["Black"])
            x = sprites.centre_x(image.get_width(), values.settings.width, 0)
            spriteList.append(sprites.GameSprite(image, (x, y+20, image.get_width(), image.get_height())))
            
            y += 40
            
            for spell in self.currentUnit.spells:
                text = self.playerArmy.codex.spells[spell].name
                image = values.font20.render(text, True, values.colours["Black"])
                spriteList.append(sprites.GameSprite(image, (20, y, image.get_width(), image.get_height())))
            
                y += 20
            
        #Black separator bar
        image = pygame.Surface((1280, 5))
        spriteList.append(sprites.GameSprite(image, (0, y, 1280, 5)))
        
        #Add abilities header
        image = values.font30.render("Abilities", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spriteList.append(sprites.GameSprite(image, (x, y+20, image.get_width(), image.get_height())))
        
        y += 40
        
        abilities1 = {}
        abilities2 = {}
        #Loop through models and look at their abilities
        for model in self.currentUnit.models:
            #Store abilities with model's ID and name
            modelData = self.playerArmy.codex.models[model.data]
            for ab in modelData.abilities:
                if ab in abilities1:
                    #Ignore duplicate abilities unless they are under a new ID
                    if modelData.ID in abilities1[ab]:
                        pass
                    else:
                        abilities1[ab].append(modelData.ID)
                        abilities2[modelData.ID] = modelData.name
                else:
                    abilities1[ab] = [modelData.ID]
                    abilities2[modelData.ID] = modelData.name
                    
        #Display abilities an each unit who has them
        for ab in abilities1:
            names = ""
            for id in abilities1[ab]:
                names += str(abilities2[id])
                names += ", "
            text = ab + " (" + names + "):"
            image = values.font20.render(text, True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (20, y, image.get_width(), image.get_height())))
            
            y += 20
            
        #Black separator bar
        image = pygame.Surface((1280, 5))
        spriteList.append(sprites.GameSprite(image, (0, y, 1280, 5)))
        
        #Add keywords header
        image = values.font30.render("Keywords", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spriteList.append(sprites.GameSprite(image, (x, y+20, image.get_width(), image.get_height())))
        
        keywords = {}
        ids = []
        
        #If shared keywords is on
        if self.currentUnit.sharedKeywords:
            #Grab first set of keywords and display
            keywords["All models"] = self.currentUnit.keywords
        else:
            #Else loop through models and look at their keywords
            for model in self.currentUnit.models:
                #Store keywords with model's ID and name
                if model.data not in ids:
                    ids.append(model.data)
                    modelData = self.playerArmy.codex.models[model.data]
                    keywords[modelData.name] = model.keywords
                #Ignore duplicate models
                
        y += 40
                
        #Display each model and the keywords they have
        for model in keywords:
            if len(ids) > 0:
                text = " (" + model + "): "
            else:
                text = ""
            for k in keywords[model]:
                text += k
                text += ", "
            image = values.font20.render(text, True, values.colours["Black"])
            spriteList.append(sprites.GameSprite(image, (20, y, image.get_width(), image.get_height())))
            
            y += 20
            
        #Black separator bar
        image = pygame.Surface((1280, 5))
        spriteList.append(sprites.GameSprite(image, (0, y, 1280, 5)))
        
        #Add options header
        image = values.font30.render("Customisation Options", True, values.colours["Black"])
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        spriteList.append(sprites.GameSprite(image, (x, y+20, image.get_width(), image.get_height())))
        
        #Set up option buttons
        y += 50
        unitData = self.playerArmy.codex.units[self.currentUnit.data]
        image = resources.load_secondary_sprite("button01.png")
        image = pygame.transform.scale(image, (700, 50))
        x = sprites.centre_x(image.get_width(), values.settings.width, 0)
        
        #Loop through options and create buttons
        for option in unitData.options:
            o = self.playerArmy.codex.options[(self.playerArmy.faction, option)]
            if o.optionType == 0:
                newModel = self.playerArmy.codex.models[(self.playerArmy.faction, o.gaining[0])].name
                text = "Add " + newModel + " model"
            elif o.optionType in (1, 2):
                if len(o.replacing) > 0:
                    text = "Replace "
                    text += self.playerArmy.codex.models[(self.playerArmy.faction, o.receivingModel)].name
                    text += "'s "
                    first = True
                    for wargear in o.replacing:
                        if not first:
                            text += "and "
                        else:
                            first = False
                        text += self.playerArmy.codex.wargear[(self.playerArmy.faction, wargear)].name
                        text += " "
                    text += "with "
                    if o.optionType == 1:
                        first = True
                        for wargear in o.gaining:
                            if not first:
                                text += "and "
                            else:
                                first = False
                            text += self.playerArmy.codex.wargear[(self.playerArmy.faction, wargear)].name
                            text += " "
                    else:
                        first = True
                        text += "items from the "
                        for wargear in o.gaining:
                            if not first:
                                text += "and "
                            else:
                                first = False
                            text += self.playerArmy.codex.wargearLists[(self.playerArmy.faction, wargear)].name
                            text += " list "
                else:
                    text = "Give "
                    text += self.playerArmy.codex.models[(self.playerArmy.faction, o.receivingModel)].name
                    text += " a "
                    if o.optionType == 1:
                        first = True
                        for wargear in o.gaining:
                            if not first:
                                text += "and "
                            else:
                                first = False
                            text += self.playerArmy.codex.wargear[(self.playerArmy.faction, wargear)].name
                            text += " "
                    else:
                        first = True
                        text += "an item from the "
                        for wargear in o.gaining:
                            if not first:
                                text += "and "
                            else:
                                first = False
                            text += self.playerArmy.codex.wargearLists[(self.playerArmy.faction, wargear)].name
                            text += " list "
            
            if o.optionType == 0:
                code = 28
            elif o.optionType in (1, 2):
                code = 29
                
            button = sprites.Button(code, 1, image, (x, y, 700, 50), text, values.font20, values, storage=o)
            
            y += 60
            
        #set up spell buttons
        isMage = False
        if self.currentUnit.sharedKeywords:
            if 'MAGE' in self.currentUnit.keywords:
                isMage = True 
        else:
            for model in self.currentUnit.keywords:
                if 'MAGE' in model.keywords:
                    isMage = True
                    break
                
        if isMage:
            for spell in self.playerArmy.codex.spells:
                text = "Add spell: " + self.playerArmy.codex.spells[spell].name
                
                button = sprites.Button(30, 1, image, (x, y, 700, 50), text, values.font20, values, 
                                        storage=self.playerArmy.codex.spells[spell])
            
                y += 60
        
        #Set up top buttons
        buttonImage = resources.load_secondary_sprite("button01.png")
        buttonImage01 = pygame.transform.scale(buttonImage, (150, 50))
        
        button = sprites.Button(23, 1, buttonImage01, (900, 0, 150, 50), "Confirm", values.font20, values)
        button = sprites.Button(24, 1, buttonImage01, (900, 60, 150, 50), "Make Boss", values.font20, values)
        button = sprites.Button(25, 1, buttonImage01, (1070, 0, 150, 50), "Reset Options", values.font20, values)
        button = sprites.Button(26, 1, buttonImage01, (1070, 60, 150, 50), "Delete Unit", values.font20, values)
                
        for button in values.buttons:
            self.group.add(button.sprites)
            
        self.group.add(spriteList)
        
    def set_up_wargear_screen(self, values):
        
        self.bgColour = values.colours["Beige"]
        
        spriteList = []
        
        longPanelImage = resources.load_secondary_sprite("long_panel01.png")
        longPanelImage01 = pygame.transform.scale(longPanelImage, (300, 700))
        
        widePanelImage = resources.load_secondary_sprite("wide_panel02.png")
        widePanelImage01 = pygame.transform.scale(widePanelImage, (600, 300))
        
        spriteList.append(sprites.GameSprite(longPanelImage01, (10, 10, 300, 700)))
        spriteList.append(sprites.GameSprite(longPanelImage01, (320, 10, 300, 700)))
        spriteList.append(sprites.GameSprite(widePanelImage01, (650, 100, 600, 300)))
        spriteList.append(sprites.GameSprite(widePanelImage01, (650, 410, 600, 300)))
        
        buttonImage = resources.load_secondary_sprite("button01.png")
        buttonImage01 = pygame.transform.scale(buttonImage, (150, 50))
        buttonImage02 = pygame.transform.scale(buttonImage, (280, 20))
        
        #Set up models in first list

        y = 20
        i = 0

        for model in self.currentUnit.models:
            
            approved = True
            for wargear in self.currentOption.requires:
                if wargear not in model.wargear:
                    approved = False
            for wargear in self.currentOption.replacing:
                if wargear not in model.wargear:
                    approved = False
                    
            if model.data[1] != self.currentOption.receivingModel:
                approved = False
            
            if approved:
            
                name = self.playerArmy.codex.models[model.data].name + " #" + str(i)
                
                button = sprites.Button(34, 0, buttonImage02, (20, y, buttonImage02.get_width(), buttonImage02.get_height()), 
                                        name, values.font20, values, storage=[model, name])
                
                y += buttonImage02.get_height()
                i += 1
                
        #If only one model is eligible, make this the current model
        if i == 1:
            self.currentModel = button
            image = values.font20.render(name, True, values.colours["Lime"])
            self.currentModel.sprites[1].image = image
                
        #Set up wargear in second list
                
        wargearList = []
        
        if self.currentOption.optionType == 1:
            for wargear in self.currentOption.gaining:
                wargearList.append(wargear)
        elif self.currentOption.optionType == 2:
            for wargear in self.playerArmy.codex.wargearLists[self.playerArmy.faction, self.currentOption.gaining[0]].wargear:
                wargearList.append(wargear)
                
        y = 20
        i = 0
        for wargear in wargearList:
            
            name = self.playerArmy.codex.wargear[self.playerArmy.faction, wargear].name
            
            button = sprites.Button(35, 0, buttonImage02, (330, y, buttonImage02.get_width(), buttonImage02.get_height()), 
                                        name, values.font20, values, storage=[wargear, name])
                
            y += buttonImage02.get_height()
            i += 1
            
        #If only one wargear is in the list, make this the current wargear
        if i == 1:
            self.currentWargear = button
            image = values.font20.render(name, True, values.colours["Lime"])
            self.currentWargear.sprites[1].image = image
        
        button = sprites.Button(32, 1, buttonImage01, (900, 0, 150, 50), "Confirm", values.font20, values)
        button = sprites.Button(33, 1, buttonImage01, (1070, 0, 150, 50), "Back", values.font20, values)
        
        for button in values.buttons:
            self.group.add(button.sprites)
            
        self.group.add(spriteList)
        
        self.get_wargear_screen_info(values)
        
    def get_wargear_screen_info(self, values):
        
        self.textGroup.empty()
        
        if self.currentWargear != None:
            
            #Set up text for wargear first
            
            image = values.font30.render(self.currentWargear.storage[1], True, values.colours["White"])
            self.textGroup.add(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 600, 650), 
                                                          130, image.get_width(), image.get_height())))
            
            text = ["Type", "Range", "Shots", "Strength", "AP", "Damage", "Points"]
            x = [680, 760, 840, 920, 1040, 1120, 1200]
            for i in range(0, 7):
                image = values.font20.render(text[i], True, values.colours["White"])
                self.textGroup.add(sprites.GameSprite(image, (x[i], 160, image.get_width(), image.get_height())))
                
            weaponData = self.playerArmy.codex.wargear[(self.playerArmy.faction, self.currentWargear.storage[0])]
            if weaponData.gearType == 0:
                attackRange = "Melee"
                weaponType = "Melee"
                shots = "N/A"
                if weaponData.userStrength:
                    if weaponData.strengthPlus != 0:
                        strength = "User STR + " + str(weaponData.strengthPlus)
                    elif weaponData.strengthMultiplier != 0:
                        strength = "User STR x " + str(weaponData.strengthMultiplier)
                    else:
                        strength = "User STR"
                else:
                    strength = str(weaponData.strength)
                
            else:
                attackRange = str(weaponData.attackRange)
                shots = str(weaponData.shots)
                strength = str(weaponData.strength)
                if weaponData.gearType == 1:
                    weaponType = "Assault"
                elif weaponData.gearType == 2:
                    weaponType = "Heavy"
                elif weaponData.gearType == 3:
                    weaponType = "Rapid Fire"
                elif weaponData.gearType == 4:
                    weaponType = "Grenade"
                elif weaponData.gearType == 5:
                    weaponType = "Pistol"
                else:
                    weaponType = "Other"
                    attackRange = "N/A"
                    shots = "N/A"
                    strength = "N/A"
            
            text = [weaponType, attackRange, shots, strength, str(weaponData.ap), str(weaponData.damage), str(weaponData.points)]
            x = [680, 760, 840, 920, 1040, 1120, 1200]
            for i in range(0, 7):
                image = values.font20.render(text[i], True, values.colours["White"])
                self.textGroup.add(sprites.GameSprite(image, (x[i], 180, image.get_width(), image.get_height())))
                
            y = 260
            for ability in weaponData.abilities:
                image = values.font20.render(ability, True, values.colours["White"])
                self.textGroup.add(sprites.GameSprite(image, (680, y, image.get_width(), image.get_height())))
                
                y += 20
                
        if self.currentModel != None:
            
            image = values.font30.render(self.currentModel.storage[1], True, values.colours["White"])
            self.textGroup.add(sprites.GameSprite(image, (sprites.centre_x(image.get_width(), 600, 650), 
                                                          440, image.get_width(), image.get_height())))
            
            y = 480
            for wargear in self.currentModel.storage[0].wargear:
                weaponData = self.playerArmy.codex.wargear[(self.playerArmy.faction, wargear)]
                image = values.font20.render(weaponData.name, True, values.colours["White"])
                self.textGroup.add(sprites.GameSprite(image, (680, y, image.get_width(), image.get_height())))
                
                y += 20
            
            
    def get_role_counts(self, unique=False):
    
        counts = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        uniques = []
        
        for unit in self.currentDetachment.units:
            unitData = self.playerArmy.codex.units[unit.data]
            counts[unitData.bfRole] += 1
            
            if counts[unitData.bfRole] != 5:
                counts[9] += 1
                
            #If the unit is unique, add it to the unique list
            if unique and unit.sharedKeywords:
                if 'UNIQUE' in unit.keywords:
                    uniques.append(unit.keywords[-1])
                
            elif unique and not unit.sharedKeywords:
                for model in unit.models:
                    if 'UNIQUE' in model.keywords:
                        uniques.append(model.keywords[-1])
                        break
        
        if unique:
            return counts, uniques
        else:
            return counts
            
    def scroll(self, values, speed):
        if self.state in (2, 4, 5, 6):
            if self.upPressed:
                self.yOffset = max(self.yOffset - speed, 0)
                self.camera = self.surface.subsurface(0, self.yOffset, 1280, 720)
            elif self.downPressed:
                self.yOffset = min(self.yOffset + speed, 770)
                self.camera = self.surface.subsurface(0, self.yOffset, 1280, 720)
    
class Detachment:
    def __init__(self):
        self.sp = 0
        self.detachmentName = None #e.g. (Vanguard)
        self.detachmentType = None
        """
        0 = Patrol, 1 = Battalion, 2 = Brigade, 3 = Vanguard, 4 = Spearhead,
        5 = Outrider, 6 = Supreme Command, 7 = Super Heavy, 8 = Air-Wing, 9 = Super-heavy Auxiliary,
        10 = Fortification Network, 11 = Auxiliary Support
        """
        self.elitesMin = 0
        self.elitesMax = 0
        self.fastAttackMin = 0
        self.fastAttackMax = 0
        self.flyerMin = 0
        self.flyerMax = 0
        self.structureMin = 0
        self.structureMax = 0
        self.heavyMin = 0
        self.heavyMax = 0
        self.leaderMin = 0
        self.leaderMax = 0
        self.ID = None
        self.name = "Enter Name"
        self.points = 0
        self.transportMin = 0
        self.transportMax = 0
        self.transportRule = True
        self.troopsMin = 0
        self.troopsMax = 0
        self.ultraMin = 0
        self.ultraMax = 0
        self.units = []
        
    def calculate_points(self):
        
        self.points = 0
        for unit in self.units:
            self.points += unit.totalPoints
        
class Model:
    def __init__(self, data=None, factionCodex=None, newModel=True):
        self.attackSpeed = None
        self.armour = None
        if data != None:
            self.data = data.ID
        else:
            self.data = data
        self.ID = None
        self.unitID = None
        self.invul = None
        self.keywords = []
        self.will = None
        self.minMove = None
        self.maxMove = None
        self.currentHP = None
        self.maxHP = None
        self.mSkill = None
        self.rSkill = None
        self.sprite = None
        self.strength = None
        self.fort = None
        self.wargear = []
        self.hpPercentage = None #Only used for morale testing
        self.wargearPoints = 0
        self.totalPoints = 0
        
        self.attackTargets = []
        self.cover = 0
        self.currentNodes = []
        self.fled = False
        self.dead = False
        self.grenadesUsed = False
        self.meleeUsed = False
        self.otherWeaponsUsed = False
        self.pistolsUsed = False
        self.previousNodes = []
        self.weaponsFired = []
        
        self.availableNodes = []
        self.nodes = []
        self.targetNode = None
        self.topLeftNode = None
        self.oldNodes = []
        self.H = 0
        
        if newModel:
            self.set_up(factionCodex)
        
    def set_up(self, factionCodex):
        
        data = factionCodex.models[self.data]
        
        self.attackSpeed = data.attackSpeed
        self.armour = data.armour
        self.invul = data.invul
        self.keywords = copy.copy(data.keywords)
        self.will = data.will
        self.minMove = data.minMove
        self.maxMove = data.maxMove
        self.currentHP = self.maxHP = data.hp
        self.mSkill = data.mSkill
        self.rSkill = data.rSkill
        self.strength = data.strength
        self.fort = data.fort
        self.wargear = copy.copy(data.wargear)
        
        self.reset_points(factionCodex)
        
    def reset_points(self, factionCodex):
        
        self.wargearPoints = 0
        
        for wargear in self.wargear:
            self.wargearPoints += factionCodex.wargear[(factionCodex.ID, wargear)].points
            
        self.totalPoints = self.wargearPoints + factionCodex.models[self.data].points
        
class Unit:
    def __init__(self, data=None, factionCodex=None, mageProfiles=None, newUnit=True):
        if data != None:
            self.data = data.ID
        else:
            self.data = data
        self.dispelLevel = None
        self.dispelRate = None
        self.keywords = []
        self.options = []
        self.sharedKeywords = True
        self.spells = []
        self.ID = None
        self.isBoss = False
        self.currentMana = None
        self.maxMana = None
        self.models = []
        self.modelPoints = 0
        self.name = None
        self.totalPoints = 0
        self.wargearPoints = 0
        
        self.advanced = False
        self.chargedUnit = None
        self.chargeRange = 0
        self.destroyed = False
        self.endPhase = False
        self.fellBack = False
        self.flags = []
        self.inMelee = False
        self.modelsLost = 0
        self.moved = False
        self.thrownGrenade = False
        
        self.closestVisible = []
        self.spellTargets = []
        self.targetUnit = None
        
        if newUnit:
            self.set_up(factionCodex, mageProfiles)
        
    def set_up(self, factionCodex, mageProfiles):
            
        unitData = factionCodex.units[self.data]
        for dm in unitData.defaultModels:
            
            modelData = factionCodex.models[(factionCodex.ID, dm)]
            model = Model(modelData, factionCodex)
            self.models.append(model)
            
            self.modelPoints += modelData.points
            self.wargearPoints += model.wargearPoints
            
        self.totalPoints = self.modelPoints + self.wargearPoints
            
        self.sharedKeywords = unitData.sharedKeywords
        if self.sharedKeywords:
            
            self.keywords = copy.copy(self.models[0].keywords)
            
        #Set up mage profile
        if 'MAGE' in self.keywords:
            profiles = []
            for mp in mageProfiles:
                if mp.ID == self.data and mp.tier == 1:
                    self.dispelLevel = mp.dispelLevel
                    self.dispelRate = mp.dispelCost
                    self.currentMana = self.maxMana = mp.mana
                    break
            
            
            
    def reset_points(self, factionCodex):
        
        self.modelPoints = self.wargearPoints = 0
        
        for model in self.models:
            
            modelPoints = factionCodex.models[model.data].points
            
            self.modelPoints += modelPoints
            self.wargearPoints += model.wargearPoints
            
        self.totalPoints = self.modelPoints + self.wargearPoints

def get_army_lists(data):
    
    #Get detachment list
    detachmentList = get_detachment_list()
    
    #Get codexes
    codexes = []
    for i in range(0, 2):
        codexes.append(get_codex(i))
    
    #Loop through data and create Army objects
    armies = []
    for entry1 in data:
        playerArmy = Army()
        playerArmy.name = entry1[0]
        playerArmy.bossTrait = entry1[1]
        if playerArmy.bossTrait == -1:
            playerArmy.bossTrait = None
        playerArmy.faction = entry1[2]
        playerArmy.totalSP = entry1[3]
        playerArmy.totalPoints = entry1[4]
        
        playerArmy.codex = codexes[playerArmy.faction]
        
        #Set up detachments
        detachments = misc.string_to_list(entry1[5])
        
        for detachment in detachments:
            d = misc.string_to_list(detachment)
            
            currentDetachment = copy.deepcopy(detachmentList[int(d[1])])
            currentDetachment.name = d[0]
            currentDetachment.points = int(d[2])
            
            units = misc.string_to_list(d[3])
            
            for unit in units:
                u = misc.string_to_list(unit)
                currentUnit = Unit(newUnit = False)
                
                currentUnit.data = misc.string_to_list(u[0], True, True)
                
                currentUnit.dispelLevel = int(u[1])
                if currentUnit.dispelLevel == -1:
                    currentUnit.dispelLevel = None
                    
                currentUnit.dispelRate = float(u[2])
                if currentUnit.dispelRate == -1.0:
                    currentUnit.dispelRate = None
                    
                currentUnit.isBoss = bool(int(u[3]))
                if currentUnit.isBoss:
                    playerArmy.boss = currentUnit
                    
                currentUnit.keywords = misc.string_to_list(u[4])
                currentUnit.options = misc.string_to_list(u[5])
                for option in currentUnit.options[:]:
                    currentUnit.options.remove(option)
                    option = misc.string_to_list(option, True, True)
                    currentUnit.options.append(option)
                
                currentUnit.sharedKeywords = bool(int(u[6]))
                
                currentUnit.spells = misc.string_to_list(u[7])
                for spell in currentUnit.spells[:]:
                    currentUnit.spells.remove(spell)
                    spell = misc.string_to_list(spell, True, True)
                    currentUnit.spells.append(spell)
                    
                currentUnit.currentMana = int(u[8])
                if currentUnit.currentMana == -1:
                    currentUnit.currentMana = None
                    
                currentUnit.maxMana = int(u[9])
                if currentUnit.maxMana == -1:
                    currentUnit.maxMana = None
                    
                currentUnit.modelPoints = int(u[10])
                currentUnit.wargearPoints = int(u[11])
                currentUnit.totalPoints = int(u[12])
                
                models = misc.string_to_list(u[13])
                
                for model in models:
                    m = misc.string_to_list(model)
                    currentModel = Model(newModel = False)
                    
                    currentModel.armour = int(m[0])
                    currentModel.attackSpeed = int(m[1])
                    currentModel.currentHP = int(m[2])
                    currentModel.data = misc.string_to_list(m[3], True, True)
                    currentModel.fort = int(m[4])
                    currentModel.invul = int(m[5])
                    currentModel.keywords = misc.string_to_list(m[6])
                    currentModel.mSkill = int(m[7])
                    currentModel.maxHP = int(m[8])
                    currentModel.maxMove = int(m[9])
                    currentModel.minMove = int(m[10])
                    currentModel.rSkill = int(m[11])
                    currentModel.strength = int(m[12])
                    currentModel.wargear = misc.string_to_list(m[13], intValues = True)
                    currentModel.wargearPoints = int(m[14])
                    currentModel.will = int(m[15])
                    
                    currentUnit.models.append(currentModel)
                
                currentDetachment.units.append(currentUnit)   
            
            playerArmy.detachments.append(currentDetachment)
            
        armies.append(playerArmy)
        
    return armies

def get_codex(factionID):
    
    c = codex.Codex()
    c.ID = factionID
    
    db = sqlite3.connect('Game Data/game database') #connect to database
    cursor = db.cursor()
    
    #Grab data
    if factionID == 0:
        cursor.execute('''SELECT id, name, abilities, ap, range, damage, type, points, shots, 
        strength, strengthMultiplier, strengthPlus, uni, userStrength FROM paladins_wargear''')
    elif factionID == 1:
        cursor.execute('''SELECT id, name, abilities, ap, range, damage, type, points, shots, 
        strength, strengthMultiplier, strengthPlus, uni, userStrength FROM orcs_wargear''')
        
    #Set up wargear
    data = cursor.fetchall()
    for entry in data:
        obj = codex.Wargear()
        obj.ID = misc.string_to_list(entry[0], True, True)
        obj.name = entry[1]
        obj.abilities = misc.string_to_list(entry[2])
        obj.ap = entry[3]
        obj.attackRange = entry[4]
        obj.damage = entry[5]
        obj.gearType = entry[6]
        obj.points = entry[7]
        obj.shots = entry[8]
        obj.strength = entry[9]
        obj.strengthMultiplier = entry[10]
        obj.strengthPlus = entry[11]
        obj.unique = bool(entry[12])
        obj.userStrength = bool(entry[13])
        
        c.wargear[tuple(obj.ID)] = obj
        
    #Add close combat weapon
    obj = codex.get_close_combat_weapon()
    obj.ID = (factionID, -1)
    c.wargear[(factionID, -1)] = obj
        
    if factionID == 0:
        cursor.execute('''SELECT id, name, faction, wargear FROM paladins_lists''')
    elif factionID == 1:
        cursor.execute('''SELECT id, name, faction, wargear FROM orcs_lists''')
        
    data = cursor.fetchall()
    for entry in data:
        obj = codex.WargearList()
        obj.ID = misc.string_to_list(entry[0], True, True)
        obj.name = entry[1]
        obj.faction = entry[2]
        obj.wargear = misc.string_to_list(entry[3], True)
        
        c.wargearLists[tuple(obj.ID)] = obj
        
    #set up spells
    if factionID == 0:
        cursor.execute('''SELECT id, name, level, mana, target, range, damage, use1 FROM paladins_spells''')
    elif factionID == 1:
        cursor.execute('''SELECT id, name, level, mana, target, range, damage, use1 FROM orcs_spells''')
        
    data = cursor.fetchall()
    for entry in data:
        obj = codex.Spell()
        obj.ID = misc.string_to_list(entry[0], True, True)
        obj.name = entry[1]
        obj.level = entry[2]
        obj.mana = entry[3]
        obj.target = entry[4]
        obj.targetRange = entry[5]
        obj.damage = entry[6]
        obj.use1 = entry[7]
        
        c.spells[tuple(obj.ID)] = obj
        
    if factionID == 0:
        cursor.execute('''SELECT id, name, abilities, attackSpeed, armour, hp, invul, keywords, will, minMove, 
        maxMove, mSkill, points, portraitPrimary, portraitSprite, rSkill, size, spriteName, spritePrimary, 
        spriteRect, strength, fortitude, wargear FROM paladins_models''')
    elif factionID == 1:
        cursor.execute('''SELECT id, name, abilities, attackSpeed, armour, hp, invul, keywords, will, minMove, 
        maxMove, mSkill, points, portraitPrimary, portraitSprite, rSkill, size, spriteName, spritePrimary, 
        spriteRect, strength, fortitude, wargear FROM orcs_models''')
    
    #Set up models
    data = cursor.fetchall()
    for entry in data:
        obj = codex.ModelDataSheet()
        obj.ID = misc.string_to_list(entry[0], True, True)
        obj.name = entry[1]
        obj.abilities = misc.string_to_list(entry[2])
        obj.attackSpeed = entry[3]
        obj.armour = entry[4]
        obj.hp = entry [5]
        obj.invul = entry[6]
        obj.keywords = misc.string_to_list(entry[7])
        obj.will = entry[8]
        obj.minMove = entry[9]
        obj.maxMove = entry[10]
        obj.mSkill = entry[11]
        obj.points = entry[12]
        obj.portraitPrimary = bool(entry[13])
        obj.portraitSprite = entry[14]
        obj.rSkill = entry[15]
        obj.size = misc.string_to_list(entry[16], True)
        obj.spriteName = entry[17]
        obj.spritePrimary = bool(entry[18])
        obj.spriteRect = misc.string_to_list(entry[19], True)
        obj.strength = entry[20]
        obj.fort = entry[21]
        obj.wargear = misc.string_to_list(entry[22], True)
        
        c.models[tuple(obj.ID)] = obj
    
    if factionID == 0:
        cursor.execute('''SELECT id, gaining, maximum, type, receivingModel, replacing, requires, 
        uni FROM paladins_options''')
    elif factionID == 1:
        cursor.execute('''SELECT id, gaining, maximum, type, receivingModel, replacing, requires, 
        uni FROM orcs_options''')
    
    data = cursor.fetchall()
    for entry in data:
        obj = codex.Option()
        obj.ID = misc.string_to_list(entry[0], True, True)
        obj.gaining = misc.string_to_list(entry[1], True)
        obj.maximum = entry[2]
        obj.optionType = entry[3]
        obj.receivingModel = entry[4]
        obj.replacing = misc.string_to_list(entry[5], True)
        obj.requires = misc.string_to_list(entry[6], True)
        obj.unique = bool(entry[7])
        
        c.options[tuple(obj.ID)] = obj
        
    if factionID == 0:
        cursor.execute('''SELECT id, title, role, models, options, sharedKeywords FROM 
        paladins_units''')
    elif factionID == 1:
        cursor.execute('''SELECT id, title, role, models, options, sharedKeywords FROM 
        orcs_units''')
        
    data = cursor.fetchall()
    for entry in data:
        obj = codex.UnitDataSheet()
        obj.ID = misc.string_to_list(entry[0], True, True)
        obj.title = entry[1]
        obj.bfRole = entry[2]
        obj.defaultModels = misc.string_to_list(entry[3], True)
        obj.options = misc.string_to_list(entry[4], True)
        obj.sharedKeywords = bool(entry[5])
        
        #loop through default models
        for model in obj.defaultModels:
            obj.basePoints += c.models[(factionID, model)].points #add model point to base points
            for gear in c.models[(factionID, model)].wargear: #loop through model's wargear
                obj.basePoints += c.wargear[(factionID, gear)].points#add wargear points to base points
        
        if obj.bfRole == 0:
            obj.bfRoleText = "Leader"
        elif obj.bfRole == 1:
            obj.bfRoleText = "Troops"
        elif obj.bfRole == 2:
            obj.bfRoleText = "Elites"
        elif obj.bfRole == 3:
            obj.bfRoleText = "Fast Attack"
        elif obj.bfRole == 4:
            obj.bfRoleText = "Heavy Support"
        elif obj.bfRole == 5:
            obj.bfRoleText = "Transport"
        elif obj.bfRole == 6:
            obj.bfRoleText = "Air"
        elif obj.bfRole == 7:
            obj.bfRoleText = "Structure"
        else:
            obj.bfRoleText = "Ultra"
        
        c.units[tuple(obj.ID)] = obj
    
    return c
        
def get_detachment_list():
    
    detachments = []
    
    d = Detachment()
    d.detachmentName = "Patrol"
    d.detachmentType = 0
    d.elitesMax = 2
    d.fastAttackMax = 2
    d.flyerMax = 2
    d.heavyMax = 2
    d.leaderMin = 1
    d.leaderMax = 2
    d.troopsMin = 1
    d.troopsMax = 3
    
    detachments.append(d)
    
    d = Detachment()
    d.detachmentName = "Battalion"
    d.detachmentType = 1
    d.sp = 3
    d.elitesMax = 6
    d.fastAttackMax = 3
    d.flyerMax = 2
    d.heavyMax = 3
    d.leaderMin = 2
    d.leaderMax = 3
    d.troopsMin = 3
    d.troopsMax = 6
    
    detachments.append(d)
    
    d = Detachment()
    d.detachmentName = "Brigade"
    d.detachmentType = 2
    d.sp = 9
    d.elitesMin = 3
    d.elitesMax = 8
    d.fastAttackMin = 3
    d.fastAttackMax = 5
    d.flyerMax = 2
    d.heavyMin = 3
    d.heavyMax = 5
    d.leaderMin = 3
    d.leaderMax = 5
    d.troopsMin = 6
    d.troopsMax = 12
    
    detachments.append(d)
    
    d = Detachment()
    d.detachmentName = "Vanguard"
    d.detachmentType = 3
    d.sp = 1
    d.elitesMin = 3
    d.elitesMax = 6
    d.fastAttackMax = 2
    d.flyerMax = 2
    d.heavyMax = 2
    d.leaderMin = 1
    d.leaderMax = 2
    d.troopsMax = 3
    
    detachments.append(d)
    
    d = Detachment()
    d.sp = 1
    d.detachmentName = "Spearhead"
    d.detachmentType = 4
    d.elitesMax = 2
    d.fastAttackMax = 2
    d.flyerMax = 2
    d.heavyMin = 3
    d.heavyMax = 6
    d.leaderMin = 1
    d.leaderMax = 2
    d.troopsMax = 3
    
    detachments.append(d)
    
    d = Detachment()
    d.sp = 1
    d.detachmentName = "Outrider"
    d.detachmentType = 5
    d.elitesMax = 2
    d.fastAttackMin = 3
    d.fastAttackMax = 6
    d.flyerMax = 2
    d.heavyMax = 2
    d.leaderMin = 1
    d.leaderMax = 2
    d.troopsMax = 3

    detachments.append(d)
    
    d = Detachment()
    d.sp = 1
    d.detachmentName = "Supreme"
    d.detachmentType = 6
    d.elitesMax = 1
    d.leaderMin = 3
    d.leaderMax = 5
    d.ultraMax = 1
        
    detachments.append(d)
    
    d = Detachment()
    d.sp = 3
    d.detachmentName = "Champions" #e.g. (Vanguard)
    d.detachmentType = 7
    d.transportRule = False
    d.ultraMin = 3
    d.ultraMax = 5
        
    detachments.append(d)
    
    d = Detachment()
    d.sp = 1
    d.detachmentName = "Air support" #e.g. (Vanguard)
    d.detachmentType = 8
    d.flyerMin = 3
    d.flyerMax = 5
    d.transportRule = False
        
    detachments.append(d)
    
    d = Detachment()
    d.detachmentName = "Support Champion" #e.g. (Vanguard)
    d.detachmentType = 9
    d.transportRule = False
    d.ultraMin = 1
    d.ultraMax = 1
    
    detachments.append(d)
    
    d = Detachment()
    d.sp = 0
    d.detachmentName = "Buildings" #e.g. (Vanguard)
    d.detachmentType = 10
    d.structureMin = 1
    d.structureMax = 3
    d.transportRule = False
    
    detachments.append(d)
        
    return detachments

def save_army(playerArmy, detachments, cursor):
    detachments = str(detachments)
    print(detachments)
    print(type(detachments))
    if playerArmy.bossTrait == None:
        bossTrait = -1
    else:
        bossTrait = playerArmy.bossTrait
    cursor.execute('''INSERT INTO armies(name, bossTrait, faction, totalSP,
    totalPoints, detachments) VALUES(?,?,?,?,?,?)''', 
    (playerArmy.name, bossTrait, playerArmy.faction, 
     playerArmy.totalSP, playerArmy.totalPoints, detachments))