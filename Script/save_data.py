"""
Handles saving of army data
"""

import sqlite3

def create_save_file():
    db = sqlite3.connect('Save Data/army list')
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ArmyList
    (
     Name TEXT PRIMARY KEY
    ,BossName TEXT
    ,BossTrait TEXT
    ,Faction INTEGER
    ,TotalPoints INTEGER
    ,TotalSP INTEGER
    )
    ''')

    db.commit()
    cursor.close()
    db.close()


def save_army(playerArmy):
    db = sqlite3.connect('Save Data/army list')
    cursor = db.cursor()

    #Delete old entry from army list
    cursor.execute('''
    DELETE FROM ArmyList WHERE Name = ?
    ''', (playerArmy.name,))

    #Get boss name
    if playerArmy.boss is not None:
        bossName = playerArmy.codex.units[playerArmy.boss.data].title
    else:
        bossName = "None"

    #Add new entry to army list
    cursor.execute('''
    INSERT INTO ArmyList (
     Name
    ,BossName
    ,BossTrait
    ,Faction
    ,TotalPoints
    ,TotalSP
    )
    
    VALUES (?,?,?,?,?,?)
    
    ''', (playerArmy.name,bossName,"None",playerArmy.faction,playerArmy.totalPoints,playerArmy.totalSP))

    #Connect to database file for army

    armyDB = sqlite3.connect(f'Save Data/{playerArmy.name}')
    armyCursor = armyDB.cursor()

    #Drop old tables

    armyCursor.execute('''
    DROP TABLE IF EXISTS Detachments
    ''')

    armyCursor.execute('''
    DROP TABLE IF EXISTS Units
    ''')

    armyCursor.execute('''
    DROP TABLE IF EXISTS Models
    ''')

    #Recreate tables

    armyCursor.execute('''
    CREATE TABLE IF NOT EXISTS Detachments
    (
      DetachmentName TEXT
     ,DetachmentID INTEGER
     ,DetachmentType INTEGER
    )
    ''')

    armyCursor.execute('''
    CREATE TABLE IF NOT EXISTS Units
    (
      DetachmentID INTEGER
     ,UnitID INTEGER
     ,UnitData TEXT
     ,options TEXT
     ,spells TEXT
    )
    ''')

    armyCursor.execute('''
    CREATE TABLE IF NOT EXISTS Models
    (
      UnitID INTEGER
     ,ModelData TEXT
     ,Invul INTEGER
     ,Wargear INTEGER
    )
    ''')

    #Insert data
    detachmentID = 0
    detachments = []
    unitID = 0
    units = []
    models = []

    for d in playerArmy.detachments:
        detachments.append((d.name, detachmentID, d.detachmentType))

        for u in d.units:
            units.append((detachmentID, unitID, str(u.data), str(u.options), str(u.spells)))

            for m in u.models:
                models.append((unitID, str(m.data), m.invul, str(m.wargear)))

            unitID += 1

        detachmentID += 1

    armyCursor.executemany('''
    INSERT INTO Detachments (DetachmentName, DetachmentID, DetachmentType)
    VALUES (?, ?, ?)
    ''', detachments)

    armyCursor.executemany('''
    INSERT INTO Units (DetachmentID, UnitID, UnitData, options, spells)
    VALUES (?, ?, ?, ?, ?)
    ''', units)

    armyCursor.executemany('''
    INSERT INTO Models (UnitID, ModelData, Invul, Wargear)
    VALUES (?, ?, ?, ?)
    ''', models)

    #Commit and close

    db.commit()
    cursor.close()
    db.close()

    armyDB.commit()
    armyCursor.close()
    armyDB.close()