"""
Script for loading SQL data
"""

import sqlite3

def load_army(name):
    db = sqlite3.connect(f'Save Data/{name}')
    cursor = db.cursor()

    cursor.execute('''
    SELECT       d.DetachmentID
                ,d.DetachmentName
                ,d.DetachmentType
                ,u.UnitID
                ,u.UnitData
                
                ,u.options
                ,u.spells
                ,m.ModelData
                ,m.Invul
                ,m.Wargear
                
                ,u.isBoss

    FROM        Detachments d
    JOIN        Units u         ON d.DetachmentID = u.DetachmentID
    JOIN        Models m        ON u.UnitID = m.UnitID
    
    ORDER BY     d.DetachmentID
                ,u.UnitID
    ''')

    data = cursor.fetchall()

    db.commit()
    cursor.close()
    db.close()

    return data

def load_army_list():
    db = sqlite3.connect('Save Data/army list')
    cursor = db.cursor()

    cursor.execute('''
        SELECT   Name
                ,BossName
                ,BossTrait
                ,Faction
                ,TotalPoints
                ,TotalSP
                ,NoOfDetachments
                
        FROM    ArmyList
        ''')

    data = cursor.fetchall()

    db.commit()
    cursor.close()
    db.close()

    return data

def load_mage_profiles():
    db = sqlite3.connect('Game Data/game database')  # connect to database
    cursor = db.cursor()

    cursor.execute('''SELECT id, itemNeeded, tier, mana, dispelLevel, dispelCost 
                    FROM mage_profiles
                ''')
    data = cursor.fetchall()

    db.commit()
    cursor.close()
    db.close()

    return data