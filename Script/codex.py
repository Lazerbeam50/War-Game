'''
Created on 3 Sep 2018

@author: Femi
'''

class Codex:
    def __init__(self):
        self.ID = None
        self.spells = {}
        self.models = {}
        self.options = {}
        self.units = {}
        self.wargear = {}
        self.wargearLists = {}
      
class Faction:
    def __init__(self):
        self.description = None
        self.ID = None #0 = Paladins, 1 = Orcs
        self.name = None
        self.wargearLists = []
        
class Spell:
    def __init__(self):
        self.ID = None
        self.name = None
        self.damage = None
        self.level = None
        self.mana = None
        """0 = friendly unit, 1 = enemy unit, 2 = friendly CHARACTER"""
        self.target = None
        self.targetRange = None
        self.use1 = None
        """0 = Direct Damage, 1 = Other for now"""
        
class MageProfile:
    def __init__(self):
        self.ID = None
        self.itemNeeded = None
        self.tier = None
        self.mana = None
        self.dispelLevel = None
        self.dispelCost = None
        
class ModelDataSheet:
    def __init__(self):
        self.abilities = []
        self.attackSpeed = None
        self.armour = None
        self.hp = None
        self.ID = None
        self.invul = None
        self.keywords = []
        self.will = None
        self.minMove = None
        self.maxMove = None
        self.mSkill = None
        self.name = None
        self.points = None
        self.portraitPrimary = None
        self.portraitSprite = None
        self.rSkill = None
        self.size = ()
        self.spriteName = None
        self.spritePrimary = True
        self.spriteRect = []
        self.strength = None
        self.fort = None
        self.wargear = []
        
class Option:
    def __init__(self):
        self.gaining = [] #Wargear/models received
        self.ID = None
        self.maximum = None #Maximum amount of times this option can be used
        self.optionType = None #0 = Add model, 1 = add/replace wargear, 2 = add/replace list, 3 = spell
        self.receivingModel = None #Model who receives the wargear
        self.replacing = [] #wargear/models replaced
        self.requires = [] #wargear/models required but NOT replaced
        self.unique = False
        self.uses = 0 #amount of times this option has been used
        
class UnitDataSheet:
    def __init__(self):
        self.basePoints = 0
        self.bfRole = None
        self.bfRoleText = None
        """
        0 = Leader, 1 = Troops, 2 = Elites, 3 = Fast Attack, 4 = Heavy Support, 5 = Transport, 6 = Air
        7 = Structure, 8 = Ultra
        """
        self.defaultModels = []
        self.ID = None
        self.options = []
        self.points = None
        self.sharedKeywords = True
        self.title = None
        
class Wargear:
    def __init__(self):
        self.abilities = []
        self.ap = None
        self.attackRange = None
        self.damage = None
        self.gearType = None #0 = Melee, 1 = Assault, 2 = Heavy, 3 = Rapid Fire, 4 = Grenade, 5 = Pistol, 6 = Other
        self.ID = None
        self.name = None
        self.points = None
        self.shots = None
        self.strength = None
        self.strengthMultiplier = None
        self.strengthPlus = None
        self.unique = False
        self.userStrength = False
        
class WargearList:
    def __init__(self):
        self.faction = None
        self.ID = None
        self.name = None
        self.wargear = []
        
def get_close_combat_weapon():
    wargear = Wargear()
    wargear.ap = 0
    wargear.attackRange = 0
    wargear.damage = 1
    wargear.gearType = 0
    wargear.ID = None
    wargear.name = "Close Combat Weapon"
    wargear.points = 0
    wargear.shots = 0
    wargear.strength = 0
    wargear.strengthMultiplier = 0
    wargear.strengthPlus = 0
    wargear.userStrength = True
    
    return wargear