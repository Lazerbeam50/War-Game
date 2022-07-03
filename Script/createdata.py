'''
Created on 3 Sep 2018

@author: Femi
'''

import sqlite3

db = sqlite3.connect('Game Data/game database') #create or connect to database
cursor = db.cursor()

factionsTotal = 0
spellsTotal = 0
wargearTotal = 0
wargearListsTotal = 0
modelsTotal = 0
unitsTotal = 0

#---------------------------------Set up factions-----------------------------------------------------

cursor.execute('''CREATE TABLE factions(id INTEGER PRIMARY KEY, name TEXT unique, description TEXT)''')


factions = [
    (0, "Paladins", "A holy order"),
    (1, "Orcs", "Large, arrogant warriors"),
    (2, "Sorcerers", "Warrior-Scholars of the Mage Realm"),
    (3, "Earthlings", "Forces of the planet Earth"),
    (4, "Valkyries", "The Great Sisterhood"),
    (5, "Titans", "Demi-God Race"),
    (6, "Elves", "Tall, slim warriors of the forest planets"),
    (7, "Undead", "The cursed, walking dead"),
    (8, "Hobgoblins", "Cruel, militant soldiers"),
    (9, "The Kraaw", "Insect-warriors of the Hive"),
    (10, "Demonic Legion", "World conquerors from the Dark Dimension")
    ]

factionsTotal += len(factions)

cursor.executemany(''' INSERT INTO factions(id, name, description) VALUES(?,?,?)''', factions)


#---------------------------------Set up mage profiles-----------------------------------------------------

cursor.execute('''CREATE TABLE mage_profiles(id TEXT, itemNeeded TEXT, tier INTEGER, mana INTEGER, 
dispelLevel INTEGER, dispelCost REAL)''')

mageProfiles = [
    ("(0, 1)", "(0, 0)", 1, 25, 3, 2.0),
    ("(0, 1)", "(0, 36)", 2, 35, 3, 1.5),
    ("(0, 1)", "(0, 37)", 3, 40, 4, 1.5),
    ("(1, 1)", "(0, 0)", 1, 20, 3, 1.75),
    ("(1, 1)", "(1, 13)", 2, 30, 3, 1.25),
    ("(1, 1)", "(1, 14)", 3, 35, 4, 1.25)
    ]

cursor.executemany('''INSERT INTO mage_profiles(id, itemNeeded, tier, mana, dispelLevel, dispelCost) VALUES(
?,?,?,?,?,?)''', mageProfiles)

#--------------------------------------Set up spells--------------------------------------------------

#Paladins spells
cursor.execute('''CREATE TABLE paladins_spells(id TEXT PRIMARY KEY, name TEXT, level INTEGER, mana INTEGER,
target INTEGER, range INTEGER, damage INTEGER, use1 INTEGER)''')

spells = [
    ("(0, 0)", "Power boost", 3, 8, 0, 12, 0, 1),
    ("(0, 1)", "Holy Wrath", 2, 6, 0, 12, 0, 1),
    ("(0, 2)", "Defensive Blessing", 4, 10, 0, 6, 0, 1),
    ("(0, 3)", "Cleansing Fire", 1, 2, 1, 18, 3, 0),
    ("(0, 4)", "Judgement", 4, 6, 1, 12, 5, 0),
    ("(0, 5)", "God's Light", 3, 8, 2, 12, 0, 1)
    ]

spellsTotal += len(spells)

cursor.executemany(''' INSERT INTO paladins_spells(id, name, level, mana, target, range, damage, use1) 
VALUES(?,?,?,?,?,?,?,?)''', spells)

#Orcs spells

cursor.execute('''CREATE TABLE orcs_spells(id TEXT PRIMARY KEY, name TEXT, level INTEGER, mana INTEGER,
target INTEGER, range INTEGER, damage INTEGER, use1 INTEGER)''')

spells = [
    ("(1, 0)", "Surge of the Hurricane", 2, 4, 0, 12, 0, 1),
    ("(1, 1)", "Thunder Torrent", 1, 2, 1, 18, 3, 0),
    ("(1, 2)", "Shield Disrupt", 3, 6, 1, 12, 0, 1),
    ("(1, 3)", "Rush!", 2, 4, 0, 12, 0, 1),
    ("(1, 4)", "Stromfury", 4, 6, 1, 12, 5, 0),
    ("(1, 5)", "Frenzy", 3, 6, 0, 12, 0, 1)
    ]

spellsTotal += len(spells)

cursor.executemany(''' INSERT INTO orcs_spells(id, name, level, mana, target, range, damage, use1) 
VALUES(?,?,?,?,?,?,?,?)''', spells)

#--------------------------------------Set up wargear-------------------------------------------------

#Paladins wargear
cursor.execute('''CREATE TABLE paladins_wargear(id TEXT PRIMARY KEY, name TEXT unique, abilities TEXT, 
ap INTEGER, range INTEGER, damage INTEGER, type INTEGER, points INTEGER, shots INTEGER, 
strength INTEGER, strengthMultiplier INTEGER, strengthPlus INTEGER, uni INTEGER, 
userStrength INTEGER)''')

wargear = [
    ("(0, 0)", "Standard pistol", "()", 0, 12, 1, 5, 0, 1, 4, 0, 0, 0, 0),
    ("(0, 1)", "Laser pistol", "()", 3, 12, 1, 5, 5, 1, 7, 0, 0, 0, 0),
    ("(0, 2)", "Holy pistol", "()", 3, 12, 2, 5, 8, 1, 5, 0, 0, 0, 0),
    ("(0, 3)", "Steel blade", "('+1 AS')", 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1),
    ("(0, 4)", "Holy sword", "()", 3, 0, 1, 0, 4, 0, 0, 0, 0, 0, 1),
    ("(0, 5)", "Holy waraxe", "()", 2, 0, 1, 0, 5, 0, 0, 0, 1, 0, 1),
    ("(0, 6)", "Holy warhammer", "()", 1, 0, 2, 0, 7, 0, 0, 0, 2, 0, 1),
    ("(0, 7)", "Holy lance", "()", 1, 0, 1, 0, 4, 0, 0, 0, 2, 0, 1),
    ("(0, 8)", "Holy gauntlet", "('-1 Melee Skill')", 3, 0, 2, 0, 20, 0, 0, 2, 0, 0, 1),
    ("(0, 9)", "Thor's hammer", "('-1 Melee Skill')", 3, 0, 3, 0, 25, 0, 0, 2, 0, 0, 1),
    ("(0, 10)", "Flamethrower", "('Auto hit', 'Ground only')", 0, 8, 1, 1, 9, 3, 4, 0, 0, 0, 0),
    ("(0, 11)", "Laser rifle", "()", 3, 24, 1, 3, 10, 1, 7, 0, 0, 0, 0),
    ("(0, 12)", "Ultragun", "()", 4, 12, 5, 1, 17, 1, 8, 0, 0, 0, 0),
    ("(0, 13)", "Laser carbine", "()", 3, 18, 2, 3, 15, 1, 5, 0, 0, 0, 0),
    ("(0, 14)", "Grenade launcher", "()", 0, 48, 1, 2, 19, 4, 4, 0, 0, 0, 0),
    ("(0, 15)", "Rocket launcher", "()", 2, 48, 4, 2, 19, 1, 8, 0, 0, 0, 0),
    ("(0, 16)", "Heavy blaster", "()", 1, 36, 1, 2, 10, 3, 5, 0, 0, 0, 0),
    ("(0, 17)", "Vaporiser", "()", 4, 24, 5, 2, 27, 1, 8, 0, 0, 0, 0),
    ("(0, 18)", "Pyrocannon", "()", 3, 48, 4, 2, 25, 1, 9, 0, 0, 0, 0),
    ("(0, 19)", "Golden cannon", "()", 3, 24, 2, 2, 28, 4, 5, 0, 0, 0, 0),
    ("(0, 20)", "Laser cannon", "()", 3, 36, 1, 2, 16, 2, 7, 0, 0, 0, 0),
    ("(0, 21)", "Holy rifle", "()", 1, 24, 2, 3, 3, 1, 4, 0, 0, 0, 0),
    ("(0, 22)", "Frag grenade", "()", 0, 6, 1, 4, 0, 4, 3, 0, 0, 0, 0),
    ("(0, 23)", "Light grenade", "()", 1, 6, 2, 4, 0, 1, 6, 0, 0, 0, 0),
    ("(0, 24)", "Staff of discipline", "()", 1, 0, 2, 0, 14, 0, 0, 0, 2, 0, 1),
    ("(0, 25)", "Burst rifle", "()", 0, 24, 1, 3, 0, 1, 4, 0, 0, 0, 0),
    ("(0, 26)", "Laser scattergun", "('Shotgun')", 0, 12, 1, 1, 0, 2, 4, 0, 0, 0, 0),
    ("(0, 27)", "Sniper rifle", "('Targets characters', 'Sniper')", 0, 36, 1, 2, 8, 1, 4, 0, 0, 0, 0),
    ("(0, 28)", "Holy grenade", "()", 4, 4, 4, 4, 5, 1, 8, 0, 0, 0, 0),
    ("(0, 29)", "Gatling gun", "()", 0, 24, 1, 3, 2, 2, 4, 0, 0, 0, 0),
    ("(0, 30)", "Pyro Blaster", "('Ignores LOS')", 0, 60, 1, 2, 30, 8, 5, 0, 0, 0, 0),
    ("(0, 31)", "Tank rapidcannon", "()", 1, 48, 3, 2, 49, 6, 7, 0, 0, 0, 0),
    ("(0, 32)", "Heavy-duty Minigun", "()", 1, 24, 1, 2, 35, 6, 6, 0, 0, 0, 0),
    ("(0, 33)", "Skycleanser", "('+1 Range Skill vs FLY', 'Air only')", 1, 48, 2, 2, 17, 3, 7, 0, 0, 0, 0),
    ("(0, 34)", "Golden Ray", "()", 2, 24, 3, 1, 0, 1, 7, 0, 0, 0, 0),
    ("(0, 35)", "Great Lord's Hammer", "()", 4, 0, 4, 0, 0, 0, 0, 0, 2, 0, 1),
    ("(0, 36)", "Adept's Amulet", "()", 0, 0, 0, 6, 10, 0, 0, 0, 0, 0, 0),
    ("(0, 37)", "Master's Spellbook", "()", 0, 0, 0, 6, 10, 0, 0, 0, 0, 0, 0),
    ("(0, 38)", "Flame Shield", "()", 0, 0, 0, 7, 5, 0, 4, 0, 0, 0, 0)
    ]

wargearTotal += len(wargear)

cursor.executemany('''INSERT INTO paladins_wargear(id, name, abilities, ap, range, damage, type,
points, shots, strength, strengthMultiplier, strengthPlus, uni, userStrength) VALUES(?, ?, ?, ?, ?,
?, ?, ?, ?, ?, ?, ?, ?, ?)''', wargear)

#Orcs wargear
cursor.execute('''CREATE TABLE orcs_wargear(id TEXT PRIMARY KEY, name TEXT unique, abilities TEXT, 
ap INTEGER, range INTEGER, damage INTEGER, type INTEGER, points INTEGER, shots INTEGER, 
strength INTEGER, strengthMultiplier INTEGER, strengthPlus INTEGER, uni INTEGER, 
userStrength INTEGER)''')

wargear = [
    ("(1, 0)", "Iron Axe", "('+1 AS')", 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1),
    ("(1, 1)", "Glock", "()", 0, 12, 1, 5, 0, 1, 4, 0, 0, 0, 0),
    ("(1, 2)", "Pineapples", "()", 0, 6, 1, 4, 0, 5, 3, 0, 0, 0, 0),
    ("(1, 3)", "Steel Axe", "('+1 AS')", 1, 0, 1, 0, 2, 0, 0, 0, 0, 0, 1),
    ("(1, 4)", "Raw Axe", "()", 3, 0, 2, 0, 4, 0, 0, 0, 0, 0, 1),
    ("(1, 5)", "Auto-Rifle", "()", 0, 24, 1, 3, 0, 1, 4, 0, 0, 0, 0),
    ("(1, 6)", "Rapid Axe", "('+2 AS')", 0, 1, 0, 0, 5, 0, 0, 0, -1, 0, 1),
    ("(1, 7)", "Magic Axe", "('Ignore invul save')", 0, 0, 1, 0, 9, 0, 0, 0, 0, 0, 1),
    ("(1, 8)", "Addamite Axe", "('-1 Melee Skill')", 3, 0, 3, 0, 20, 0, 0, 2, 0, 0, 1),
    ("(1, 9)", "Sledgehammer", "('-1 Melee Skill', '+1 to wound vs VEHICLES')", 2, 0, 2, 0, 13, 0, 0, 0, 2, 0, 1),
    ("(1, 10)", "Cleaver", "('+3 AS')", 0, 0, 1, 0, 12, 0, 0, 0, 0, 0, 1),
    ("(1, 11)", "Hand Cannon", "()", 1, 12, 2, 5, 8, 1, 5, 0, 0, 0, 0),
    ("(1, 12)", "Power Pistol", "()", 3, 12, 2, 5, 15, 1, 7, 0, 0, 0, 0),
    ("(1, 13)", "Adept's Amulet", "()", 0, 0, 0, 6, 10, 0, 0, 0, 0, 0, 0),
    ("(1, 14)", "Master's Spellbook", "()", 0, 0, 0, 6, 10, 0, 0, 0, 0, 0, 0),
    ("(1, 15)", "Flamer", "('Auto hit', 'Ground only')", 0, 8, 1, 1, 14, 4, 4, 0, 0, 0, 0),
    ("(1, 16)", "Shock Shooter", "()", 3, 24, 1, 3, 18, 1, 7, 0, 0, 0, 0),
    ("(1, 17)", "Stormer", "()", 4, 12, 4, 1, 25, 1, 8, 0, 0, 0, 0),
    ("(1, 18)", "Shock Carbine", "()", 3, 18, 2, 3, 22, 1, 5, 0, 0, 0, 0),
    ("(1, 19)", "Sniper Rifle", "('Targets characters', 'Sniper')", 0, 36, 1, 2, 10, 1, 4, 0, 0, 0, 0),
    ("(1, 20)", "Bite", "()", 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1),
    ("(1, 21)", "RPG", "()", 0, 48, 3, 2, 23, 1, 8, 0, 0, 0, 0),
    ("(1, 22)", "Gattler", "()", 0, 36, 1, 2, 27, 5, 5, 0, 0, 0, 0),
    ("(1, 23)", "Thundergun", "()", 2, 48, 4, 2, 34, 1, 8, 0, 0, 0, 0),
    ("(1, 24)", "Wotan Cannon", "()", 2, 48, 3, 2, 38, 1, 10, 0, 0, 0, 0),
    ("(1, 25)", "Mini-turret", "()", 0, 36, 1, 3, 13, 3, 5, 0, 0, 0, 0),
    ("(1, 26)", "Side Cannon", "()", 1, 1, 2, 2, 20, 1, 7, 0, 0, 0, 0),
    ("(1, 27)", "Zap Tapper", "()", 1, 36, 2, 3, 20, 1, 6, 0, 0, 0, 0),
    ("(1, 28)", "Shock Bombs", "()", 0, 6, 1, 1, 38, 8, 5, 0, 0, 0, 0),
    ("(1, 29)", "Volt Strike", "()", 0, 6, 5, 1, 30, 1, 9, 0, 0, 0, 0),
    ("(1, 30)", "Skyguard", "('Air only')", 2, 36, 3, 2, 42, 4, 7, 0, 0, 0, 0),
    ("(1, 31)", "Thunder Shield", "()", 0, 0, 0, 7, 5, 0, 4, 0, 0, 0, 0)
    ]

wargearTotal += len(wargear)

cursor.executemany('''INSERT INTO orcs_wargear(id, name, abilities, ap, range, damage, type,
points, shots, strength, strengthMultiplier, strengthPlus, uni, userStrength) VALUES(?, ?, ?, ?, ?,
?, ?, ?, ?, ?, ?, ?, ?, ?)''', wargear)

#----------------------------------Set up wargear lists-----------------------------------------------

#Paladin's wargear lists
cursor.execute('''CREATE TABLE paladins_lists(id TEXT PRIMARY KEY, name TEXT unique, faction INTEGER,
wargear TEXT)''')

wargearLists = [
    ("(0, 0)", "Pistols", 0, "(0, 1, 2)"),
    ("(0, 1)", "Melee Weapons", 0, "(3, 4, 5, 6, 7, 8, 9)"),
    ("(0, 2)", "Special Weapons", 0, "(10, 11, 12, 13)"),
    ("(0, 3)", "Heavy Weapons", 0, "(14, 15, 16, 17, 18, 19, 20)")
    ]

wargearListsTotal += len(wargearLists)

cursor.executemany('''INSERT INTO paladins_lists(id, name, faction, wargear) VALUES(?, ?, ?, ?)''',
                   wargearLists)

#Orc's wargear lists
cursor.execute('''CREATE TABLE orcs_lists(id TEXT PRIMARY KEY, name TEXT unique, faction INTEGER,
wargear TEXT)''')

wargearLists = [
    ("(1, 0)", "Basic Melee Weapons", 1, "(0, 3, 4)"),
    ("(1, 1)", "Advanced Melee Weapons", 1, "(6, 7, 8, 9, 10)"),
    ("(1, 2)", "Pistols", 1, "(1, 11, 12)"),
    ("(1, 3)", "Ranged Weapons", 1, "(15, 16, 17, 18)")
    ]

wargearListsTotal += len(wargearLists)

cursor.executemany('''INSERT INTO orcs_lists(id, name, faction, wargear) VALUES(?, ?, ?, ?)''',
                   wargearLists)

#------------------------------------Set up models----------------------------------------------------

#Paladin's models
cursor.execute('''CREATE TABLE paladins_models(id TEXT PRIMARY KEY, name TEXT, abilities TEXT, 
attackSpeed INTEGER, armour INTEGER, hp INTEGER, invul INTEGER, keywords TEXT, 
will INTEGER, minMove INTEGER, maxMove INTEGER, mSkill INTEGER, points INTEGER, portraitPrimary INTEGER, 
portraitSprite TEXT, rSkill INTEGER, size TEXT, spriteName TEXT, spritePrimary INTEGER, spriteRect TEXT, 
strength INTEGER, fortitude INTEGER, wargear TEXT)''')

models = [
    ("(0, 0)", "Captain", "('Focus Aura')", 4, 4, 5, 3, "('CHARACTER', 'INFANTRY', 'CAPTAIN')", 9, 0, 6, 5, 75, 1,
     "portrait_sprite.png", 5, "(1, 1)", "paladins_captain_sprite.png", 1, "(32, 32)", 4, 4, "(21, 3, 22, 23)"),
    ("(0, 1)", "Invoker", "('Novice Invoker', 'Adept Invoker', 'Master Invoker')", 3, 4, 4, 0, 
     "('CHARACTER', 'INFANTRY', 'MAGE', 'INVOKER')", 9, 0, 6, 4, 95, 1, "portrait_sprite.png", 4, "(1, 1)", 
     "paladins_invoker_sprite.png", 1, "(32, 32)", 4, 4, "(24, 0, 22, 23)"),
    ("(0, 2)", "Paladin Veteran", "()", 2, 4, 1, 0, "('INFANTRY', 'BROTHERHOOD VETERANS')", 8, 0, 6,
     4, 15, 1, "portrait_sprite.png", 4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 3, 22, 23)"),
    ("(0, 3)", "Veteran Sergeant", "()", 2, 4, 1, 0, "('INFANTRY', 'BROTHERHOOD VETERANS')", 9, 0, 6,
     4, 15, 1,"portrait_sprite.png", 4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 3, 22, 23)"),
    ("(0, 4)", "Medicant", "()", 3, 4, 4, 0, "('CHARACTER', 'INFANTRY', 'MEDICANT')", 8, 0, 6, 4, 55, 1,
     "portrait_sprite.png", 4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 3, 22, 23)"),
    ("(0, 5)", "Initiate", "()", 1, 4, 1, 0, "('INFANTRY', 'GROUND SQUAD')", 7, 0, 6, 4, 13, 1, 
     "portrait_sprite.png", 4, "(1, 1)", "paladins_initiate_sprite.png", 1, "(32, 32)", 4, 4, "(25, 0, 22, 23)"),
    ("(0, 6)", "Knight", "()", 2, 4, 1, 0, "('INFANTRY', 'GROUND SQUAD')", 8, 0, 6, 4, 20, 1,
     "portrait_sprite.png", 4, "(1, 1)", "paladins_knight_sprite.png", 1, "(32, 32)", 4, 4, "(25, 0, 22, 23)"),
    ("(0, 7)", "Scout", "()", 1, 3, 1, 0, "('INFANTRY', 'SCOUT SQUAD')", 7, 0, 6, 4, 12, 1, "portrait_sprite.png", 
     4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(25, 0, 22, 23)"),
    ("(0, 8)", "Scout Leader", "()", 2, 3, 1, 0, "('INFANTRY', 'SCOUT SQUAD')", 8, 0, 6, 4, 12, 1,
     "portrait_sprite.png", 4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(25, 0, 22, 23)"),
    ("(0, 9)", "Striker", "()", 1, 4, 1, 0, "('INFANTRY', 'STRIKER SQUAD')", 7, 0, 7, 4, 16, 1,
     "portrait_sprite.png", 4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 3, 22, 23)"),
    ("(0, 10)", "Striker Leader", "()", 2, 4, 1, 0, "('INFANTRY', 'STRIKER SQUAD')", 8, 0, 7, 4, 16, 
     1, "portrait_sprite.png", 4, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 3, 22, 23)"),
    ("(0, 11)", "Biker", "()", 1, 4, 2, 0, "('BIKER', 'BIKER SQUAD')", 7, 0, 14, 4, 30, 1, "portrait_sprite.png",
      4, "(2, 2)", "paladins_biker_sprite.png", 1, "(64, 64)", 4, 5, "(29, 0, 22, 23)"),
    ("(0, 12)", "Bike Squad Leader", "()", 2, 4, 2, 0, "('BIKER', 'BIKER SQUAD')", 8, 0, 14, 4, 30, 1,
     "portrait_sprite.png", 4, "(2, 2)", "paladins_biker_leader_sprite.png", 1, "(64, 64)", 4, 5, "(29, 0, 22, 23)"),
    ("(0, 13)", "Pyro-Tech Gun", "('Artillery', 'Fearless')", 0, 4, 4, 0, 
     "('ARTILLERY', 'PYRO-TECH GUN')", 8, 0, 3, 0, 28, 1, "portrait_sprite.png", 4, "(2, 2)", 
     "paladins_pyro_tech_gun_sprite.png", 1, "(64, 64)", 3, 6, "(30)"),
    ("(0, 14)", "Pyro-Tech Gunner", "('Repair artillery')", 1, 4, 2, 0, 
     "('INFANTRY', 'ARTILLERY GUNNER', 'PYRO-TECH GUNNER')", 8, 0, 6, 4, 18, 1, "portrait_sprite.png", 4, 
     "(1, 1)", "paladins_pyro_tech_gunner_sprite.png", 1, "(32, 32)", 4, 4, "(0, 3, 22, 23)"),
    ("(0, 15)", "Brotherhood Tank", "('Explodes', 'Degrades')", 3, 4, 11, 0, 
     "('VEHICLE', 'BROTHERHOOD TANK')", 8, 0, 12, 1, 102, 1, "portrait_sprite.png", 4, "(5, 5)", 
     "placeholder_sprite.png", 1, "(32, 32)", 6, 7, "(31)"),
    ("(0, 16)", "Brotherhood APC", "('Explodes', 'Degrades')", 3, 4, 10, 0, 
     "('VEHICLE', 'TRANSPORT', 'BROTHERHOOD APC')", 8, 0, 12, 1, 70, 1, "portrait_sprite.png", 4, "(4, 4)", 
     "paladins_brotherhood_apc_sprite.png", 1, "(128, 128)", 6, 8, "(25)"),
    ("(0, 17)", "Pyro-Heavy Chopper", "('Explodes', 'Degrades', 'Steady')", 3, 4, 10, 0, 
     "('VEHICLE', 'FLY', 'AIRBORNE', 'PYRO-HEAVY CHOPPER')", 8, 0, 50, 1, 110, 1, "portrait_sprite.png", 4, 
     "(6, 6)", "paladins_pyro_heavy_chopper_sprite.png", 1, "(195, 192)", 6, 6, "(16, 16, 32, 32)"),
    ("(0, 18)", "Pyro-Heavy Interceptor", 
     "('Explodes', 'Degrades', 'Hard to hit', 'Interceptor')", 3, 4, 10, 0, 
     "('VEHICLE', 'FLY', 'AIRBORNE', 'PYRO-HEAVY INTERCEPTOR')", 8, 20, 60, 1, 85, 1, "portrait_sprite.png", 
     4, "(6, 6)", "placeholder_sprite.png", 1, "(32, 32)", 6, 6, "(16, 16, 32, 32, 33)"),
    ("(0, 19)", "Great Lord Auldoon", "('Fearless')", 6, 5, 9, 5, 
     "('CHARACTER', 'INFANTRY', 'HERO', 'UNIQUE', 'AULDOON')", 10, 0, 10, 5, 330, 1, "portrait_sprite.png", 5, 
     "(2, 2)", "placeholder_sprite.png", 1, "(32, 32)", 6, 6, "(34, 35)")
    ]

modelsTotal += len(models)

cursor.executemany('''INSERT INTO paladins_models(id, name, abilities, attackSpeed, armour, hp, invul, 
keywords, will, minMove, maxMove, mSkill, points, portraitPrimary, portraitSprite, rSkill, size, spriteName, 
spritePrimary, spriteRect, strength, fortitude, wargear) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', models)

#Orc's models
cursor.execute('''CREATE TABLE orcs_models(id TEXT PRIMARY KEY, name TEXT, abilities TEXT, 
attackSpeed INTEGER, armour INTEGER, hp INTEGER, invul INTEGER, keywords TEXT, 
will INTEGER, minMove INTEGER, maxMove INTEGER, mSkill INTEGER, points INTEGER, portraitPrimary INTEGER, 
portraitSprite TEXT, rSkill INTEGER, size TEXT, spriteName TEXT, spritePrimary INTEGER, spriteRect TEXT, 
strength INTEGER, fortitude INTEGER, wargear TEXT)''')

models = [
    ("(1, 0)", "Worg Lord", "('Orcish Pride', 'In the hunt')", 4, 4, 5, 3, "('CHARACTER', 'CAVALRY', 'WORG LORD')",
     9, 0, 11, 5, 85, 1, "portrait_sprite.png", 4, "(2, 2)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, 
     "(0, 1, 2)"),
    ("(1, 1)", "Storm Caller", "('Orcish Pride', 'Novice Storm Caller', 'Adept Storm Caller', 'Master Storm Caller')",
     3, 4, 4, 0, "('CHARACTER', 'INFANTRY', 'MAGE', 'STORM CALLER')", 9, 0, 6, 4, 85, 1, "portrait_sprite.png", 
     3, "(1, 1)", "orc_storm_caller_sprite.png", 1, "(32, 32)", 4, 4, "(0, 1, 2)"),
    ("(1, 2)", "Spec Ops Orc", "('Orcish Pride', 'Undercover')", 2, 4, 1, 0, "('INFANTRY', 'SPEC OPS SQUAD')",
     8, 0, 7, 4, 13, 1, "portrait_sprite.png", 4, "(1, 1)", "orc_spec_ops_orc_sprite.png", 1, "(32, 32)", 4, 4, 
     "(5, 1, 2)"),
    ("(1, 3)", "Spec Ops Leader", "('Orcish Pride', 'Undercover')", 3, 4, 1, 0, "('INFANTRY', 'SPEC OPS SQUAD')",
     9, 0, 7, 4, 13, 1, "portrait_sprite.png", 4, "(1, 1)", "orc_spec_ops_leader_sprite.png", 1, "(32, 32)", 4, 4,
      "(5, 1, 2)"),
    ("(1, 4)", "Doom Orc", "('Orcish Pride')", 4, 4, 4, 2, "('INFANTRY', 'DOOM ORC')", 9, 0, 6, 5, 65, 1,
     "portrait_sprite.png", 3, "(2, 2)", "placeholder_sprite.png", 1, "(32, 32)", 5, 5, "(0, 1, 2)"),
    ("(1, 5)", "Brawler", "('Orcish Pride')", 2, 4, 1, 0, "('INFANTRY', 'BRAWLER')", 8, 0, 6, 4, 15, 1,
     "portrait_sprite.png", 3, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 1, 2)"),
    ("(1, 6)", "Brawler Leader", "('Orcish Pride')", 3, 4, 1, 0, "('INFANTRY', 'BRAWLER')", 9, 0, 6, 4, 15, 1,
     "portrait_sprite.png", 3, "(1, 1)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 1, 2)"),
    ("(1, 7)", "Gunner", "('Orcish Pride')", 1, 4, 1, 0, "('INFANTRY', 'GUNNER SQUAD')", 8, 0, 6, 4, 13, 1,
     "portrait_sprite.png", 4, "(1, 1)", "orc_gunner_sprite.png", 1, "(32, 32)", 4, 4, "(5, 1, 2)"),
    ("(1, 8)", "Gunner Leader", "('Orcish Pride')", 2, 4, 1, 0, "('INFANTRY', 'GUNNER SQUAD')", 9, 0, 6, 4, 13, 1,
     "portrait_sprite.png", 4, "(1, 1)", "orc_gunner_leader_sprite.png", 1, "(32, 32)", 4, 4, "(5, 1, 2)"),
    ("(1, 9)", "Worg Rider", "('Orcish Pride', 'Charge!')", 2, 4, 2, 0, "('CAVALRY', 'WORG CAVALRY')", 8, 0, 10, 4,
      35, 1, "portrait_sprite.png", 3, "(2, 2)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 1, 2)"),
    ("(1, 10)", "Worg Rider Leader", "('Orcish Pride', 'Charge!')", 3, 4, 2, 0, "('CAVALRY', 'WORG CAVALRY')", 9, 0, 
     10, 4, 35, 1, "portrait_sprite.png", 3, "(2, 2)", "placeholder_sprite.png", 1, "(32, 32)", 4, 4, "(0, 1, 2)"),
    ("(1, 11)", "Worg", "('Charge!')", 2, 1, 1, 0, "('BEAST', 'WORG PACK')", 4, 0, 10, 4, 7, 1, 
     "portrait_sprite.png", 0, "(1, 1)", "orc_worg_sprite.png", 1, "(32, 32)", 4, 3, "(20)"),
    ("(1, 12)", "Orc Heavy", "('Orcish Pride')", 2, 4, 1, 0, "('INFANTRY', 'DEMOLITIONS SQUAD')", 8, 0, 6, 4, 18, 1,
     "portrait_sprite.png", 3, "(1, 1)", "orc_heavy_sprite.png", 1, "(32, 32)", 4, 4, "(21, 0, 2)"),
    ("(1, 13)", "Orc Heavy Leader", "('Orcish Pride')", 3, 4, 2, 0, "('INFANTRY', 'DEMOLITIONS SQUAD')", 9, 0, 6, 4,
      18, 1, "portrait_sprite.png", 3, "(1, 1)", "orc_heavy_leader_sprite.png", 1, "(32, 32)", 4, 4, "(21, 0, 2)"),
    ("(1, 14)", "Turbo-Tank", "('Explodes', 'Degrades', 'Steady')", 3, 4, 14, 0, "('VEHICLE', 'TURBO-TANK')",
     8, 0, 14, 1, 140, 1, "portrait_sprite.png", 4, "(5, 5)", "placeholder_sprite.png", 1, "(32, 32)", 7, 8, "(24)"),
    ("(1, 15)", "Speedwagon", "('Explodes', 'Degrades')", 3, 4, 10, 0, "('VEHICLE', 'TRANSPORT', 'SPEEDWAGON')",
     8, 0, 14, 1, 55, 1, "portrait_sprite.png", 3, "(4, 4)", "placeholder_sprite.png", 1, "(32, 32)", 6, 7, 
     "(5, 5)"),
    ("(1, 16)", "Duster", "('Explodes', 'Degrades', 'Hard to hit')", 3, 4, 8, 0, 
     "('VEHICLE', 'FLY', 'AIRBORNE', 'DUSTER')", 8, 20, 50, 1, 65, 1, "portrait_sprite.png", 4, "(5, 5)", 
     "orc_duster_sprite.png", 1, "(160, 160)", 6, 6, "(5, 5)"),
    ("(1, 17)", "Big-Bomber", "('Explodes', 'Degrades', 'Hard to hit')", 3, 4, 14, 0, 
     "('VEHICLE', 'FLY', 'AIRBORNE', 'BIG-BOMBER')", 8, 15, 40, 1, 100, 1, "portrait_sprite.png", 3, "(7, 7)", 
     "placeholder_sprite.png", 1, "(32, 32)", 6, 7, "(29, 28)"),
    ("(1, 18)", "Fortified Guard Tower", "('Immobile', 'Auto-Attack')", 0, 4, 20, 0, 
     "('VEHICLE', 'STRUCTURE', 'FORTIFIED GUARD TOWER')", 0, 0, 0, 0, 170, 1, "portrait_sprite.png", 2, "(6, 6)", 
     "placeholder_sprite.png", 1, "(32, 32)", 0, 8, "(22)")
    ]

modelsTotal += len(models)

cursor.executemany('''INSERT INTO orcs_models(id, name, abilities, attackSpeed, armour, hp, invul, 
keywords, will, minMove, maxMove, mSkill, points, portraitPrimary, portraitSprite, rSkill, size, spriteName, 
spritePrimary, spriteRect, strength, fortitude, wargear) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', models)

#--------------------------------------Set up options------------------------------------------------

#Paladin's options
cursor.execute('''CREATE TABLE paladins_options(id TEXT PRIMARY KEY, gaining TEXT,
maximum INTEGER, type INTEGER, receivingModel INTEGER, replacing TEXT, requires TEXT, uni INTEGER)
''')

options = [
    ("(0, 0)", "(0)", 1, 2, 0, "(21)", "()", 0),
    ("(0, 1)", "(1)", 1, 2, 0, "(21)", "()", 0),
    ("(0, 2)", "(1)", 1, 2, 0, "(3)", "()", 0),
    ("(0, 3)", "(0)", 1, 2, 1, "(0)", "()", 0),
    ("(0, 4)", "(25)", 1, 1, 1, "(0)", "()", 0),
    ("(0, 5)", "(4)", 1, 1, 1, "(24)", "()", 0),
    ("(0, 6)", "(5)", 1, 1, 1, "(24)", "()", 0),
    ("(0, 7)", "(2)", 3, 0, 0, "()", "()", 0),
    ("(0, 8)", "(0)", 1, 2, 3, "(0)", "()", 0),
    ("(0, 9)", "(1)", 1, 2, 3, "(0)", "()", 0),
    ("(0, 10)", "(2)", 1, 2, 3, "(0)", "()", 0),
    ("(0, 11)", "(3)", 1, 2, 3, "(0)", "()", 0),
    ("(0, 12)", "(1)", 1, 2, 3, "(3)", "()", 0),
    ("(0, 13)", "(1)", 0, 2, 2, "(0)", "()", 0),
    ("(0, 14)", "(0)", 0, 2, 2, "(0)", "()", 0),
    ("(0, 15)", "(25)", 0, 1, 2, "(3)", "()", 0),
    ("(0, 16)", "(0)", 0, 2, 2, "(3)", "()", 0),
    ("(0, 17)", "(1)", 0, 2, 2, "(3)", "()", 0),
    ("(0, 18)", "(2)", 0, 2, 2, "(3)", "()", 0),
    ("(0, 19)", "(5)", 4, 0, 0, "()", "()", 0),
    ("(0, 20)", "(6)", 3, 0, 0, "()", "()", 0),
    ("(0, 21)", "(0)", 1, 2, 6, "(0)", "()", 0),
    ("(0, 22)", "(1)", 1, 2, 6, "(0)", "()", 0),
    ("(0, 23)", "(2)", 1, 2, 6, "(25)", "()", 0),
    ("(0, 24)", "(3)", 1, 2, 6, "(25)", "()", 0),
    ("(0, 25)", "(3)", 0, 1, 5, "(25)", "()", 0),
    ("(0, 26)", "(2)", 1, 2, 5, "(25)", "()", 0),
    ("(0, 27)", "(3)", 1, 2, 5, "(25)", "()", 0),
    ("(0, 28)", "(4)", 1, 1, 5, "(25)", "()", 0),
    ("(0, 29)", "(26)", 0, 1, 5, "(25)", "()", 0),
    ("(0, 30)", "(7)", 5, 0, 0, "()", "()", 0),
    ("(0, 31)", "(0)", 1, 2, 8, "(0)", "()", 0),
    ("(0, 32)", "(1)", 1, 2, 8, "(0)", "()", 0),
    ("(0, 33)", "(1)", 1, 2, 8, "(25)", "()", 0),
    ("(0, 34)", "(2)", 1, 2, 8, "(25)", "()", 0),
    ("(0, 35)", "(3)", 1, 2, 8, "(25)", "()", 0),
    ("(0, 36)", "(27)", 1, 1, 8, "(25)", "()", 0),
    ("(0, 37)", "(26)", 1, 1, 8, "(25)", "()", 0),
    ("(0, 38)", "(26)", 1, 1, 7, "(25)", "()", 0),
    ("(0, 39)", "(27)", 1, 1, 7, "(25)", "()", 0),
    ("(0, 40)", "(9)", 5, 0, 0, "()", "()", 0),
    ("(0, 41)", "(1)", 1, 2, 10, "(0)", "()", 0),
    ("(0, 42)", "(0)", 1, 2, 10, "(0)", "()", 0),
    ("(0, 43)", "(1)", 1, 2, 10, "(3)", "()", 0),
    ("(0, 44)", "(28)", 1, 1, 10, "()", "()", 0),
    ("(0, 45)", "(10)", 2, 1, 9, "(0)", "()", 0),
    ("(0, 46)", "(1)", 2, 1, 9, "(0)", "()", 0),
    ("(0, 47)", "(11)", 3, 0, 0, "()", "()", 0),
    ("(0, 48)", "(0)", 1, 2, 12, "(0)", "()", 0),
    ("(0, 49)", "(1)", 1, 2, 12, "(0)", "()", 0),
    ("(0, 50)", "(2)", 1, 2, 12, "(0)", "()", 0),
    ("(0, 51)", "(3)", 1, 1, 11, "(0)", "()", 0),
    ("(0, 52)", "(2)", 2, 2, 11, "(0)", "()", 0),
    ("(0, 53)", "(18)", 1, 1, 15, "(31)", "()", 0),
    ("(0, 54)", "(18)", 1, 1, 15, "()", "()", 0),
    ("(0, 55)", "(16)", 1, 1, 15, "()", "()", 0),
    ("(0, 56)", "(29)", 1, 1, 15, "()", "()", 0),
    ("(0, 57)", "(25)", 1, 1, 16, "()", "()", 0),
    ("(0, 58)", "(18)", 2, 1, 17, "(16)", "()", 0),
    ("(0, 59)", "(36)", 1, 1, 1, "()", "()", 0),
    ("(0, 60)", "(37)", 1, 1, 1, "()", "(36)", 0),
    ("(0, 61)", "(38)", 1, 1, 0, "()", "()", 0),
    ("(0, 62)", "(38)", 0, 1, 2, "()", "()", 0),
    ("(0, 63)", "(38)", 0, 1, 3, "()", "()", 0)
    ]

cursor.executemany('''INSERT INTO paladins_options(id, gaining, maximum, type, receivingModel, 
replacing, requires, uni) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', options)

#Orcs' options
cursor.execute('''CREATE TABLE orcs_options(id TEXT PRIMARY KEY, gaining TEXT,
maximum INTEGER, type INTEGER, receivingModel INTEGER, replacing TEXT, requires TEXT, uni INTEGER)
''')

options = [
    ("(1, 0)", "(0)", 1, 2, 0, "(0)", "()", 0),
    ("(1, 1)", "(1)", 1, 2, 0, "(0)", "()", 0),
    ("(1, 2)", "(2)", 1, 2, 0, "(1)", "()", 0),
    ("(1, 3)", "(0)", 1, 2, 0, "(1)", "()", 0),
    ("(1, 4)", "(5)", 1, 1, 1, "(1)", "()", 0),
    ("(1, 5)", "(2)", 1, 2, 1, "(1)", "()", 0),
    ("(1, 6)", "(0)", 1, 2, 1, "(1)", "()", 0),
    ("(1, 7)", "(0)", 1, 2, 1, "(0)", "()", 0),
    ("(1, 8)", "(2)", 5, 0, 0, "()", "()", 0),
    ("(1, 9)", "(2)", 0, 2, 3, "(1)", "()", 0),
    ("(1, 10)", "(2)", 0, 2, 2, "(1)", "()", 0),
    ("(1, 11)", "(3)", 0, 2, 3, "(5)", "()", 0),
    ("(1, 12)", "(3)", 0, 2, 2, "(5)", "()", 0),
    ("(1, 13)", "(19)", 0, 1, 3, "(5)", "()", 0),
    ("(1, 14)", "(19)", 0, 1, 2, "(5)", "()", 0),
    ("(1, 15)", "(4)", 2, 0, 0, "()", "()", 0),
    ("(1, 16)", "(0)", 0, 2, 4, "(0)", "()", 0),
    ("(1, 17)", "(1)", 0, 2, 4, "(0)", "()", 0),
    ("(1, 18)", "(5)", 5, 0, 0, "()", "()", 0),
    ("(1, 19)", "(0)", 1, 2, 6, "(0)", "()", 0),
    ("(1, 20)", "(1)", 1, 2, 6, "(0)", "()", 0),
    ("(1, 21)", "(3)", 0, 1, 5, "(0)", "()", 0),
    ("(1, 22)", "(7)", 5, 0, 0, "()", "()", 0),
    ("(1, 23)", "(3)", 1, 2, 8, "(5)", "()", 0),
    ("(1, 24)", "(2)", 1, 2, 8, "(1)", "()", 0),
    ("(1, 25)", "(0)", 1, 2, 8, "(1)", "()", 0),
    ("(1, 26)", "(0)", 0, 1, 7, "(1)", "()", 0),
    ("(1, 27)", "(11)", 0, 1, 7, "(1)", "()", 0),
    ("(1, 28)", "(9)", 4, 0, 0, "()", "()", 0),
    ("(1, 29)", "(0)", 0, 2, 10, "(0)", "()", 0),
    ("(1, 30)", "(1)", 0, 2, 10, "(0)", "()", 0),
    ("(1, 31)", "(2)", 0, 2, 10, "(1)", "()", 0),
    ("(1, 32)", "(15)", 0, 1, 10, "(1)", "()", 0),
    ("(1, 33)", "(17)", 0, 1, 10, "(1)", "()", 0),
    ("(1, 34)", "(0)", 0, 2, 9, "(0)", "()", 0),
    ("(1, 35)", "(1)", 0, 2, 9, "(0)", "()", 0),
    ("(1, 36)", "(2)", 0, 2, 9, "(1)", "()", 0),
    ("(1, 37)", "(15)", 0, 1, 9, "(1)", "()", 0),
    ("(1, 38)", "(17)", 0, 1, 9, "(1)", "()", 0),
    ("(1, 39)", "(11)", 10, 0, 0, "()", "()", 0),
    ("(1, 40)", "(12)", 5, 0, 0, "()", "()", 0),
    ("(1, 41)", "(22)", 1, 1, 13, "(21)", "()", 0),
    ("(1, 42)", "(23)", 1, 1, 13, "(21)", "()", 0),
    ("(1, 43)", "(0)", 1, 2, 13, "(0)", "()", 0),
    ("(1, 44)", "(9)", 1, 1, 13, "(0)", "()", 0),
    ("(1, 45)", "(22)", 2, 1, 12, "(21)", "()", 0),
    ("(1, 46)", "(0)", 2, 2, 12, "(0)", "()", 0),
    ("(1, 47)", "(25)", 2, 1, 14, "()", "()", 0),
    ("(1, 48)", "(26)", 2, 1, 14, "()", "()", 0),
    ("(1, 49)", "(25)", 1, 1, 16, "()", "()", 0),
    ("(1, 50)", "(27)", 1, 1, 16, "()", "()", 0),
    ("(1, 51)", "(22)", 1, 1, 18, "()", "()", 0),
    ("(1, 52)", "(30)", 1, 1, 18, "()", "()", 0),
    ("(1, 53)", "(23)", 1, 1, 18, "()", "()", 0),
    ("(1, 54)", "(13)", 1, 1, 1, "()", "()", 0),
    ("(1, 55)", "(14)", 1, 1, 1, "()", "(13)", 0),
    ("(1, 56)", "(31)", 1, 1, 0, "()", "()", 0),
    ("(1, 57)", "(31)", 0, 1, 4, "()", "()", 0)
    ]

cursor.executemany('''INSERT INTO orcs_options(id, gaining, maximum, type, receivingModel, 
replacing, requires, uni) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', options)

#---------------------------------------Set up units-------------------------------------------------

#Paladin's units
cursor.execute('''CREATE TABLE paladins_units(id TEXT PRIMARY KEY, title TEXT, role INTEGER, 
models TEXT, options TEXT, sharedKeywords INTEGER)''')

units = [
    ("(0, 0)", "Captain", 0, "(0)", "(0, 1, 2, 61)", 1),
    ("(0, 1)", "Invoker", 0, "(1)", "(3, 4, 5, 6, 59, 60)", 1),
    ("(0, 2)", "Veteran Squad", 2, "(3, 2)", "(7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 62, 63)", 1),
    ("(0, 3)", "Medicant", 2, "(4)", "()", 1),
    ("(0, 4)", "Ground Squad", 1, "(5, 5, 5, 5, 5)", "(19, 20, 21, 22, 23, 24, 25, 26, 27, 28)", 1),
    ("(0, 5)", "Scout Squad", 1, "(8, 7, 7, 7, 7)", "(30, 31, 32, 33, 34, 35, 36, 37, 38, 39)", 1),
    ("(0, 6)", "Striker Squad", 3, "(10, 9, 9, 9, 9)", "(40, 41, 42, 43, 44, 45, 46)", 1),
    ("(0, 7)", "Biker Squad", 3, "(12, 11, 11)", "(47, 48, 49, 50, 51, 52)", 1),
    ("(0, 8)", "Pyro-Tech Gun", 4, "(13, 14)", "()", 0),
    ("(0, 9)", "Brotherhood Tank", 4, "(15)", "(53, 54, 55, 56)", 1),
    ("(0, 10)", "Brotherhood APC", 5, "(16)", "(57)", 1),
    ("(0, 11)", "Pyro-Heavy Chopper", 6, "(17)", "(58)", 1),
    ("(0, 12)", "Pyro-Heavy Interceptor", 6, "(18)", "()", 1),
    ("(0, 13)", "Great Lord Auldoon", 8, "(19)", "()", 1)
    ]

unitsTotal += len(units)

cursor.executemany('''INSERT INTO paladins_units(id, title, role, models, options, sharedKeywords)
VALUES (?, ?, ?, ?, ?, ?)''', units)

#Orcs' units
cursor.execute('''CREATE TABLE orcs_units(id TEXT PRIMARY KEY, title TEXT, role INTEGER, 
models TEXT, options TEXT, sharedKeywords INTEGER)''')

units = [
    ("(1, 0)", "Worg Lord", 0, "(0)", "(0, 1, 2, 3, 56)", 1),
    ("(1, 1)", "Storm Caller", 0, "(1)", "(4, 5, 6, 7, 54, 55)", 1),
    ("(1, 2)", "Special Ops Squad", 2, "(3, 2, 2)", "(8, 9, 10, 11, 12, 13, 14)", 1),
    ("(1, 3)", "Doom Orcs", 2, "(4)", "(15, 16, 17, 57)", 1),
    ("(1, 4)", "Brawler Squad", 1, "(6, 5, 5, 5, 5)", "(18, 19, 20, 21)", 1),
    ("(1, 5)", "Gunner Squad", 1, "(8, 7, 7, 7, 7)", "(22, 23, 24, 25, 26, 27)", 1),
    ("(1, 6)", "Worg Cavalry", 3, "(10, 9, 9, 9)", "(28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38)", 1),
    ("(1, 7)", "Worg Pack", 3, "(11, 11, 11, 11, 11, 11, 11, 11, 11, 11)", "(39)", 1),
    ("(1, 8)", "Demolitions Squad", 4, "(13, 12, 12, 12, 12)", "(40, 41, 42, 43, 44, 45, 46)", 1),
    ("(1, 9)", "Turbo-Tank", 4, "(14)", "(47, 48)", 1),
    ("(1, 10)", "Speedwagon", 5, "(15)", "()", 1),
    ("(1, 11)", "Duster", 6, "(16)", "(49, 50)", 1),
    ("(1, 12)", "Big Bomber", 6, "(17)", "()", 1),
    ("(1, 13)", "Fortified Guard Tower", 7, "(18)", "(51, 52, 53)", 1)
    ]

unitsTotal += len(units)

cursor.executemany('''INSERT INTO orcs_units(id, title, role, models, options, sharedKeywords)
VALUES (?, ?, ?, ?, ?, ?)''', units)

db.commit()

cursor.execute('''SELECT id, title FROM paladins_units''')
for row in cursor:
    # row[0] returns the first column in the query (name), row[1] returns email column.
    print('{0} : {1}'.format(row[0], row[1]))
db.close()

print()
print("TOTALS")
print()
print("Factions:", factionsTotal)
print("Spells:", spellsTotal)
print("Wargear:", wargearTotal)
print("Wargear Lists:", wargearListsTotal)
print("Models:", modelsTotal)
print("Units:", unitsTotal)
