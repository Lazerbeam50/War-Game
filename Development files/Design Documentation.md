## Part I: Army Customisation/Game Setup

1. Battlefields
2. Detachments
3. Factions
4. Heroes and Unique Units
5. Magic and Spells
6. Missions
7. Models
8. Point limit
9. Saving/Loading Armies
10. Strategy Points
11. Units
12. Unit Options

## Part II: Wargaming

1. Deployment
2. Charge Phase
3. Magic Phase
4. Melee Phase
5. Morale Phase
6. Movement Phase
7. Objective Markers
8. Post-Game Screen
9. Primary Objectives
10. Radiant Objectives
11. Shooting Phase
12. Terrain
13. Timed turns
14. Transports
15. UI
16. Unit Abilities
17. Victory Points

## Part III: Online Play

1. Direct Play
2. Rankings
3. Server Login
4. Server Lobby
5. Server Matchmaking
6. Spectating
7. Three or more players
8. Usage Statistics

## Part IV: General/Misc

1. Start game screens

# Part I: Army Customisation

## Battlefields

**Stage 1** – Aim is to have a range of battlefields with varying themes. Only one will be included at first but the aim is to have around 6-10 battlefields.

**Stage 2** – Include more battlefields. Battlefields to be stored as SQLite data instead of being created in the script.

**Stage 3+** Include more tilesets.

## Detachments

**Stage 1** – Include all but auxiliary detachments.

## Factions

**Stage 1** – Only Paladins and Orcs. 

**Stage 3** – Add Sorcerers. 

**Stage 4** – Include Earthlings and Amazons.

**Stage 5** – Include Titans and Free Elven Republic.

**Stage 6+** Finally, add Undead, Hobgoblins, The Kraaw and The Demonic Legion.

## Heroes and Unique Units

**Stage 1** – An army may only contain one UNIQUE unit of its type (indicated by the last keyword in its keyword list).

**Stage 3** – An army may only contain two units with the HERO keyword. 

**Stage 5** – Titans may have up to four HEROES. Add more HEROES to factions, with each having around 5.

## Magic and Spells

**Stage 1** – Each mage unit can equip up to three spells. Only include damage spells for now.

**Stage 2** – Include all spells for Paladins and Orcs.

## Models

**Stage 1** – Fully functional but lacking abilities.

**Stage 2+** Add abilities

## Point limit

**Stage 3+** Adjustable point limit available 

## Saving/Loading Armies

**Stage 1** – Army save data to be converted to SQLlite3 format.

**Stage 2** – Ability to load armies for editing.

**Stage 4+** Add save limitations to ban illegal armies.

**Stage 6+** Allow for copying an army.

## Strategy points

**Stage 3+** Can be used in game to recover mana on a MAGE, replace a tactical objective, temporarily increase a unit's speed.

## Units

**Stage 7+** Keep adding units (in particular, HEROES) to maintain balance and add more variety.

## Unit Options

**Stage 1** – All available excluding list wargear and “other” items.

**Stage 2+** All available for each faction.

# Part II: Wargaming

## Deployment

**Stage 1** – Deployment zones to be built into the maps themselves.

**Stage 3** – Include more deployment zones.

## Charge Phase

**Stage 1** – Charge range is calculated as 1d3+7 unless a unit has an ability that changes this. Overwatch can be used but reduces the shooting unit's range skill to 1.

Units with the AIRBORNE keyword cannot charge. They can also only be charged by units with the FLY keyword. In melee, they can only be attacked by units with the FLY keyword.

## Magic Phase

**Stage 1** – Each spell has a mana cost and spell level. Each mage model has a set amount of mana and dispelling capabilities as standard – but can select options to improve these. Flow of the magic phase is as follows:

- Select eligible mage
- Select spell (each spell can only be used once per magic phase)
- Select target.
- Spend mana.
- Enemy mage has the option to dispel if they are within 24 squares, and have the mana/capabilities.
- Spell resolves, unless it was dispelled.

Damage dealing spells deal “Direct Damage” which ignores fortitude and saves. “Mortal Wounds” from 8th edition do not exist in this game. Each point of Direct Damage is a single Attack object, allowing it to transfer if a target model dies.

## Melee Phase

**Stage 1** – Attack priority during this phase is as follows:

1. Boosted priority + charged
2. Boosted priority without charge
3. Normal priority + charged
4. Normal priority without charge
5. Reduced priority + charged
6. Reduced priority without charge

Within each priority stage, players alternate in attacking with units starting with the play who's turn it is.

Any model equipped with two or more melee weapons gains +1 to its Attack Speed.

## Morale Phase

**Stage 1** – The game automatically loops through all living units who have lost models this turn and performs morale checks.

A morale check involves rolling 1d6 + the amount of models lost this turn. If this number is equal or less than the will of the unit, then nothing happens. If the number exceeds the unit's will, some of the unit's models will flee. The number of deserters is equal to: moralRoll – unitWill. 

When determining which models will flee, the game prioritises those with the lowest will first. After that, models with the lowest cost are chosen to flee before higher cost models. In the case of a tie, models with a lower percentage of their health remaining will flee first. For example, if three units need to flee but four have equal value and will stats, the models with 50% health remaining will flee before those with 100% health remaining.

## Movement Phase

**Stage 1** – Advancing allows the unit to add 3 to its movement instead of a dice roll. 

Unit coherency is established when each model in a unit is at least within 2 squares of another model. Coherency checks are skipped for units containing only one model. 

## Objective Markers

**Stage 1** – To be built into the battlefield rather than allow players to place them.

Units with the AIRBORNE keyword cannot capture objectives.

## Post-Game Screen

**Stage 2** – Should display points, completed objectives, discarded objectives, unit kills, model kills, spells cast, successful charges, models fled, units ranked by kills, units ranked by points scored, MVP (most points scored + models killed + units killed), Best Value Unit (MVP/unit cost) and worst performer (reverse of MVP). This screen appears as part of the screen manager, not the battle. 

**Stage 8+** Consider adding dice results.

## Primary Objectives

**Stage 1** – Killing a boss is worth 2 points.

## Radiant objectives

**Stage 3 –** 

## Saves

**Stage 1** – There are three types of save: Armour saves, cover saves and invulnerable saves. All units have armour saves, although they can be reduced by armour piercing weapons. On-field cover grants cover saves of either 1 or 2 depending on the quality of the cover. When making a saving roll, the highest save is always selected automatically.

Units with the AIRBORNE keyword can never use cover saves.

## Shooting Phase

**Stage 1** – Each shot fired by a model creates an “Attack” object, which saves the range skill of the shooter, the strength, armour piercing and damage of the weapon, and any relevant abilities. Each attack object saves the closest model in the target unit as its primary target (the models in the unit are placed in a list based on closeness), and the others in a secondary target list. All targets must be in line of sight. Attack objects are checked in a queue based on how many potential targets they have – those with less targets go first.

Attack objects are removed from the pool as they fail to-hit, to-wound and saving rolls. If a Attack object successfully kills its target model, any other Attack objects which have that model as their primary target must select the next closest model from their secondary list. If they are not able to select another model, then they are removed from the pool.

When choosing who in a unit will shoot, the game will give two options: Shoot each weapon type together (e.g. fire all standard pistols) or shoot each weapon type excluding models with non-standard weapons. Players can also select individual models to shoot.

Players must select range weapons before targets.

Line of sight is calculated as a direct path between attacker and target. The path travels node-by-node, one node at a time. Direction of travel is diagonal then horizontal/vertical for one square if needed. If a line of sight blocker appears in the path, no line of sight can be found. Additionally, AIRBORNE models cannot block LOS.

**Stage 2** – Add shoot with all models excluding custom gear option.

**Stage 3+** Display chance to hit/damage per shot, and chance to remove unit.

## Terrain

**Stage 1** – Woods and line of sight blockers.

**Stage 5** – Craters, tanglewire, and tank traps.

**Stage 6** – Fuel pipes and minefields.

## Timed turns

**Stage 3+** Include a 10-30 minute turn timer. Opponent making decisions on your turn has up to 1 minute per decision. 

## Transports

**Stage 2** – All models inside a transport which is destroyed suffer explosion damage at Strength 5, Armour piercing 1, 2 Damage.

Players can deploy an infantry unit within a transport by deploying the transport first, and then deploying a unit on top of it. 

A single transport can carry one model per point of its maximum HP. A unit must be fully embarked on a transport to be able to use it (e.g. An 11 model unit would not be able to embark on a 10HP transport. A transport can carry multiple units, which can embark and disembark independently.

For a unit to embark onto a transport, all models in that transport must have at least one of their nodes be within 3 squares of the transport. A unit can embark after it moves.

*Standard disembarking*: A unit can disembark from a transport if it begins the movement phase in one. Models that disembark must deploy themselves within 3 squares of the transport. If this is not possible, then they cannot disembark at all. 

*Emergency disembarking*: If a transport is reduced to 0 HP, all units must disembark within 3 squares where the transport was (including the area the transport previously took up). Any models that are unable to disembark are killed automatically. When deciding which models to kill, the game will prioritise lower value models first, and then models with lower HP percentages.

## UI

**Stage 1** – Need the following:

- Event log
- Score (on top)
- SP (on top)
- Current turn (on top)
- Unit portrait (bottom)
- Unit/Terrain info – e.g. stats, flags, keywords. Player can cycle through displays (bottom)
- Command card/list (bottom)
- Markers captured (top)
- Chat log

**Stage 3** – Allow scrolling of the vent log by holding the up/down event log buttons.

**Stage 4** – Add chat log.

## Unit Abilities

**Stage 2**

## Victory Points

**Stage 1**

# Part III: Online Play

## Direct Play

**Stage 4** – Allows players to play against each other using just a name and code. Data is sent between players via a server, which also rolls dice. Include chat log.

## Rankings

**Stage 7+** Points based system similar to Pokemon, which awards (or removes) points based on the rank difference and the in-game point difference. Rankings should refresh every 3 months.

## Server Login

**Stage 5** – Basic sign-up, login system implemented.

**Stage 6** – Password hashing and attempt blocking.

## Server Lobby

**Stage 8+**

## Server Matchmaking

**Stage 5** – Basic matchmaking, essentially random paring.

**Stage 7+** Matchmaking based on player ranking. Essentially, the aim should be for all players in a pot to be matched as closely as possibly.

## Spectating

**Stage 9+**

## Three or more players

**Stage 9+** Might not add this in.

## Usage Statistics

**Stage 9+**