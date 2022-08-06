## Part I: Army Customisation/Game Setup

1. Battlefields
2. Detachments
3. Factions
4. Heroes and Unique Units
5. Magic and Spells
6. Missions
7. Models
8. Saving/Loading Armies
9. Strategy Points
10. Units
11. Unit Options

## Part II: Wargaming

1. Deployment
2. Charge Phase
3. Magic Phase
4. Melee Phase
5. Morale Phase
6. Movement Phase
7. Objective Markers
8. Post-game screen
9. Primary Objectives
10. Radiant Objectives
11. Shooting Phase
12. Terrain
13. Timed turns
14. Transports
15. UI/Controls
16. Unit Abilities
17. Victory Points

## Part III: Online Play

1. Direct P2P
2. Rankings
3. Server Login
4. Server Lobby
5. Server Matchmaking
6. Three or more players

## Part IV: General/Misc

1. Save data
1. Start game screens






# Part I: Army Customisation

## Battlefields

class Battlefield:

- name (string)
- size (tuple of ints) – contains two values: width (int) and height (int)
- tileset (int)
- map (3D array of strings) – Each list within the array represents a row of tiles, and each character within a list represents a tile.
- deploymentMap (int) – Determines which deployment map this battlefield uses. 
- objective1 (tuple of ints) – contains two values: x (int) and y (int)
- objective2 (tuple of ints) – contains two values: x (int) and y (int)
- objective3 (tuple of ints) – contains two values: x (int) and y (int)
- objective4 (tuple of ints) – contains two values: x (int) and y (int)
- objective5 (tuple of ints) – contains two values: x (int) and y (int)
- objective6 (tuple of ints) – contains two values: x (int) and y (int)

## Magic and Spells

class Spell:

- ID (tuple)
- name (string)
- damage (int)
- level (int)
- mana (int)
- target (int)
- targetRange (int)
- use1 (int)

class MageProfile:

- ID (tuple) #this ID refers to the mage the profile is for, not the profile itself
- itemNeeded (tuple) #id of item needed to obtain this profile
- tier (int) #indicates if this is the default profile for the mage, or one of its upgrades. Used to determine which profile to use if the mage has their upgrade wargear.
- Mana (int)
- dispelLevel (int)
- dispelCost (float)

# Part II: Wargaming

class Battle:

- commandListCounter (int – used so that the game knows how far down a list to display in terms of Commands (e.g. deployment))
- commandListSurface (pygame Surface – 420 x 200, at location 860, 520)
- chatLogBottomLine (int – determines the last string in the chat log. Is increased or decreased by scrolling)
- chatLogSurface (pygame Surface – 420 x 200, at location 0, 520)
- chatLogText (list of strings)
- controlPointGroup (pygame Group)
- currentCommands (list of Command objects)
- currentUnit (tuple)
- eventLogBottomLine (int – determines the last string in the event log. Is increased or decreased by scrolling)
- eventLogSurface (pygame Surface – 420 x 200, at location 430, 520)
- eventLogText (list of strings)
- headerSurface (pygame Surface – 1280 x 50, at location 0, 0)
- hideUI (bool)
- highlightGroup (pygame Group)
- leftPanelSurface (pygame Surface – 150 x 450, at location 0, 60)
- modelsGroup (pygameGroup)
- nodes (dict – co-ordinates as key, Node object as value)
- objective1 (int, marks the status of an objective marker (0 = unclaimed, 1 = player1, 2 = player2, 3 = contested)
- objective2 (int)
- objective3 (int)
- objective4 (int)
- objective5 (int)
- objective6 (int)
- overwatch (bool)
- rightPanelSurface (pygame Surface – 150 x 450, at location 1130, 60)
- squaresGroup (pygame Group)
- state (int)
- targetNode (tuple – Node co-ordinates. Used to move models as a group)
- terrainCamera (pygame Subsurface)
- terrainGroup (pygame Group)
- terrainSurface (pygame Surface – needs to be the same size as unitSurface)
- unitCamera (pygameSubsurface)
- unitSurface (pygame Surface – needs to be the same size as terrainSurface)
- unitsToDeploy (list of tuples – contains Ids of units still in need of deployment)
- xOffset (int)
- yOffset (int)

class Command (maybe use a Button instead?):

- action (int)
- key (string)
- sprite (GameSprite object)
- storage (varies – depending on the data being stored)
- text (string)

class Model (attributes to add):

- currentNodes (list of Nodes)
- dead (bool)
- grenadesUsed (bool)
- meleeUsed (bool)
- otherWeaponsUsed (bool)
- pistolsUsed (bool)
- previousNodes (list of Nodes)
- weaponsFired (list of ints)

class Node:

- x (int)
- y (int)
- walkable (bool)
- terrain (string)
- sprite (GameSprite)
- cover (int – either 0, 1 or 2)
- blocksLOS (bool)
- takenBy (Model)

class Player:

- army (Army)
- name (string)
- currentSP (int)
- finishedDeploymentFirst (bool)
- victoryPoints (int)
- objectivesAchieved (list)
- currentObjectives (list)
- objectivesDeck (stack)
- discardedObjectives (list)
- spellsUsed (list of ints)
- models (tuple of Models)
- units (tuple of Units)

class Unit (attributes to add):

- advanced (bool)
- charged (bool)
- chargedUnit (tuple – Unit ID)
- destroyed (bool)
- fellBack (bool)
- endPhase (bool)
- inMelee (bool)
- modelsLost (int)
- moved (bool)

assign_IDs (Method):

- create dictionaries for units and models
- loop through units and assign them Ids as follows: (player number, count). Also give them names (e.g. “Ground Squad #2).
- loop through models and assign them Ids as follows: (player number, count)

check_unit_coherency (Method):

- Loop through models in a unit
- If model has already been marked as in range, skip them.
- Grab all nodes within 2 squares.
- Loop through each node and see if a friendly model has taken it. If so, mark the friendly model as in range.
- If the model has at least one friendly model in range of it, mark it as in range. Otherwise, break out of the loop and return false.

## Unit/Model deaths

- Mark models/units as dead rather than removing them from lists.
- Dead models add to a unit's model's lost count for that turn.
- After an attack on a unit which results in the death of models has been resolved, each control point checks to see if control of it has changed.
- Whenever a unit dies, the game checks to see if it can award the “King Slayer” or “First Blood” objectives. It also checks if that was the last unit in the player's army to die (excluding buildings), which would result in a major victory for the opponent.

## Charge Phase

- Loop through units and mark those who have advanced, fell back, are in melee range, or have the AIRBORNE keyword as having completed the phase.
- Player must select a unit.
- Player must then select a target within 10 squares.
- Overwatch occurs. Opposing player gets a shooting phase using only the target unit firing with a range skill of 1.
- If the charging unit survives the overwatch, they roll charge range and report it as an event. If the charge range is too short to reach, this is reported and the unit has failed its charge.
- If the unit can charge, at least one model in the unit must end its move within 1 square of an enemy. The player can reset movement as normal and can cancel their move, which marks the charging unit as having completed the phase.
- Units who complete a successful charge are marked as such.
- Once the player ends their charge phase, the opposing player may move any of their CHARACTERS who are not locked in melee, up to three squares if this will put them in melee contact. During this move, CHARACTERS can walk freely into a melee. All other movement restrictions still apply.

## Deployment

- A player is randomly selected to be the first to deploy.
- Command list displays units to choose from, with the final options displaying as “More”.
- Selecting a unit now allows the player to click a node on the map to deploy that unit.
- Once a space is selected, the game places all models within that unit around the node, providing they can fit.
- The player can then select individual models and move them around – hitting confirm when done. A unit can only be confirmed if it is in coherency (2 squares away from any other model).
- Once a unit is confirmed deployed, the other player must then deploy a unit. If the opposing player has no more units left to deploy, then the current player must continue deploying their units.

## Magic Phase

- Loop through units and flag non-MAGES as having completed the phase.
- Select a friendly unit for spellcasting.
- Command list displays one command per spell and Back.
- Once an eligible spell is selected (enough mana, hasn't been used this turn), the player must select a target.
- If target is eligible, spend mana.
- If an enemy MAGE is in range, give the choice to dispel if they are able to (enough mana, dispel level high enough).
- If spell was not dispelled, resolve spell and report to event log.
- If spell was dispelled, mark the caster as having completed the phase.
- Store spell ID as having been used this phase.

## Melee Phase

- Loop through all units (including enemy units) and flag all who are not in melee as having completed the phase.
- Place all units who can fight in the melee phase in 6 lists, one for each priority level. No player can end this phase prematurely. 
- Players alternate controlling units within a priority list, starting with the player who's turn it is.
- Command list shows a list of units who can fight in the current priority list.
- Selecting a unit allows the player to move models in that unit up to three squares. A model that starts the pile in in base contact must end its movement in base contact, even if this is with a different enemy model. The player has the options to confirm of reset movement.
- After movement, the command list shows melee weapon options for attacking as in the shooting phase. Any model that does not have a melee weapon attacks with a “Close Combat Weapon” which is removed during the end phase.
- Player then selects a target unit in range. To be in range, the target must be 1 square away or 1 square away from another model in the attacking unit. If the attacking unit charged, then it can only attack the unit it charged that turn. To attack a AIRBORNE unit, the attacking unit must have FLY. Damage calculated as in the shooting phase.
- After all attacks have been made, the unit can consolidate another 3 squares. Same rules apply as in the pile in.
- Move between players, units and priority levels until phase is over.

## Morale Phase

Phase automatically run upon ending the previous phase. Morale checks are and their results reported in the event log (e.g. 1 Gunner(s) flees from Gunner Squad #1! 2 Worg(s) flee from Worg Pack #3! Worg Pack #3 is destroyed!).
Player can only select “end phase”.

## Movement Phase

- Loop through units and flag those that cannot move as having completed the phase.
- Select a unit to move.
- Command list displays four options: Move, Advance, Fall Back and Back.
- Selecting any of the above leads to the next three options: Move unit – maintain position, Move unit – towards point, Move unit, individual models.
- Walkable nodes appear as lime green.
- For “Move unit – maintain position”, the player selects a model within a unit and the game generates its movement range. The player then selects a node within that movement range to move to. Once that model has moved, the game tries to move each model into the correspondent square to maintain position. If a desired square cannot be moved to for whatever reason, the model then aims to move to the closest square within its movement range. If this is not possible, then the model does not move. Any models that do not move can be moved individually.
- For “Move unit – towards point”, the player selects a model within a unit and the game generates its movement range. The player then selects a node within that movement range to move to. Once that model has moved, the game tries to move each model as close to that node as possible.
- After moving a unit or any model in a unit, the player can select either “confirm” or “reset unit” in the command list. 
- Selecting “confirm” results in a coherency check. If this is passed, the unit is marked as having moved (or advanced or fell back) and cannot move again this phase. If a model in the unit has moved less than its minimum movement, it is destroyed.
- Selecting “reset unit” sets every model in the unit to its original position.
- Only one unit can move at a time. Once a model in a unit has moved, another unit cannot be selected until the current unit has confirmed its moves.
- Selecting “end phase” will destroy all units that have moved less than their minimum movement.
- **Stage 2** – Add an “embark” button if the current unit is INFANTRY and its the movement phase. This should be added alongside “Move”, “Advance”, “Fall Back” and “Back”, and on the “Confirm/Back” screen following unit movement.
- **Stage 2** – Selecting “embark” leads to another state where the player is asked to select a transport to embark onto, with the option to back out. The player must click on a friendly transport, which causes the game to check if the select unit is actually a friendly transport, whether or not it has capacity to carry the full unit, and finally whether or not every model in the current unit is in range of it. If all of these checks are passed, the player will be asked to confirm if they would like to embark on that transport, with the option to back out.
- **Stage 2** – When a unit embarks on a transport, its nodes are cleared and its unit ID is added to the transports “onboard” list.
- **Stage 2** – As well as “Move”, “Advance”, “Fall Back” and “Back”, a unit will have “Disembark” as an option if its onboard list length is greater than 0. The next state then sets up each unit inside the transport as a button (as well as a back option), and asks the player to select a unit to disembark.
- **Stage 2** – Once the player selects a unit, they must click in a square within a 3 square radius of the transport. Squares that are within one square of an enemy unit are invalid for disembarking, and will not appear as an option. 
- **Stage 2** – If the player selects a valid square, the game will attempt to deploy models as it would during the deployment phase, but will warn the player if it fails. In addition to the deployment phase deployment, the game will also check to see if the unit is in coherency.
- **Stage 2** – If deployment is successful, the deployed unit will be flagged as having disembarked that phase, the event log will be updated, and the game will loop back to allowing the transport to move or allow more units to disembark.

### Generating movement range

A model cannot move through or end its movement on the following nodes:

- Non-walkable nodes (unless it can FLY).
- Taken nodes (units with FLY can move through these, as can any unit if the taken node belongs to an AIRBORNE model).
- Nodes that are within 1 square of an enemy model (units with FLY can move through these, as can any unit if the taken node belongs to an AIRBORNE model).

## Objective Markers

After a unit completes its movement, a model dies or flees, and at the start of the game (post-deployment), each objective marker checks all nodes within 3 squares of it to see how many models are placed on those nodes. If one player has more than they other, then they control that marker. If they have an equal amount of models in range, the marker is contested. If no one has models in range, the marker is unclaimed. Only announce a markers status if it has changed since last checked.

## Shooting Phase

- Loop through units and flag those that cannot shoot as having completed the phase.
- Select a friendly unit to fire.
- Command list displays one item per weapon. Only eligible weapons can be shown here (e.g. no heavy weapons in the unit advanced).
- Selecting a weapon gives the option of firing all weapons of that type, all excluding custom, or to select models to fire with. If the selected weapon is owned by a single model, this screen is skipped. If a grenade was selected, the player must select one model to throw the grenade, skipping this screen.
- Selecting to fire with an individual model brings up a list of weapons (including grenades) and Back.
- Once weapons have been selected, player must select a target that is in range, in line of sight (CHARACTER rule is considered here), and not in melee (unless pistols are used, the shooting unit is in melee and the target is closest visible unit).
- Resolve attacks and report shots, hits, damage and kills (e.g. Ground Squad #2 fire 12 shots from their burst rifles into Brawler Squad #1! 7 shots hit, dealing 2 damage and killing 1 Brawler(s) and 1 Brawler Leader(s)! Brawler Squad #1 has been destroyed!).
- Individual models must keep track of which weapons they have fired, as well as use flags to keep track of having fired pistols, grenades or other weapons.
- A unit can fire again providing it can still create a weapons command list. If it can't, its marked as completed the phase.


## Terrain

draw_field (Method):

- Set up terrain images as pygame Surface objects.
- Loop through lists in battlefield, and string in line.
- Each character is created as Node object, with terrain data and sprites.
- Each node is saved in a nodes dictionary with its co-ordinates as a key.

### Terrain group layers

1. Background
2. Terrain features
3. Highlighting
4. Movement squares
5. Control point markers
6. Models

## Transports

- Need to include a bool on units to flag that they started the movement phase in a transport. This is only used for heavy weapon usage.
- Need a list of unit ids for all units held in the vehicle.
- When deploying a unit inside a transport, a new state should be created to ask the player if they would like to deploy in that transport (in case of misclicks).
- Should add a new ui element to show units within transports.
- When a transport is destroyed and after calculating normal explosion damage, additional explosion damage is calculated against each model in all units inside the transport. Here, one attack object is created per model, with that model set as the main target, and no additional targets.
- If any models have survived the explosion, the game will loop through units and models, and try to deploy them in the top-left square where the transport once was, using only the transport's squares as valid deployment squares (providing that they are not adjacent to enemy models). Units will also be checked for coherency after being successfully placed.
- If a unit cannot be successfully placed, the game places the cheapest model with the lowest HP percentage in a separate list, and tries to deploy again without this model. This loop continues until all models are in the separate list, or the unit is able to successfully deploy.
- Once a unit is successfully deployed, any models in the separate list are flagged as dead and the event is updated to read like “3 Knights and 1 Initiate were able to escape the wreckage! 2 Initiates were unable to escape and were slain!”.

## UI/Controls

Mouse button up event. Game computes world position of click. Get node clicked in (if possible). Show desired info for that node (e.g. unit info, terrain info). 

- Allow a button which disables UI temporarily (left-control button).
- “u” selects unit info (Name, portrait, mage profile, boss status, models lost, flags including advanced, charged etc.) - Player 1 at left panel, player 2 at right panel
- “t” select terrain info (Name, cover bonus, walkable, blocks LOS) – Left panel only
- “o” shows objectives info (Score by turn, current objectives, completed objectives, discarded objectives) – Both panels
- “m” shows model info (Name, portrait, characteristics, keywords, wargear, flags) – Player 1 at left panel, player 2 at right panel
- “p” shows control point info (List control points and current status) – Left panel only
- Stage 2 – “n” shows transport info (unit and model list of what's in a transport e.g. “Veteran squad: veteran sergeant x1, paladin veteran x2)
- Additionally, arrow keys are used to scroll the battlefield. 
- Scrolling the mouse wheel on the chat or event log causes them to scroll up/down.
- Pressing the space bar moves the camera to the current unit.
- Pressing keys 1-6 moves the camera to that respective marker.
- Need to include space in the chat log to type.
- Command list items are assigned letters (QWER, ASDF, ZXCV) which control their actions.
- Pressing “h” toggles unit highlighting: friendly units that haven't taken their turns are in blue, those that have are in grey, enemies that haven't moved are in red, and those that have are in orange. The current model/unit in a situation is purple.
- Holding ctrl+alt+c causes the player who is currently in control to concede. 

## Unit abilities

**Explodes** – Each model has a exploded flag which is set to False by default. After any point where a model with the Explodes ability is destroyed, the game turns on an explosion checking flag and adds the model to a list 
of models to check. The game then iterates through a copy of this list rather than carry out its normal behaviour, executing explosions and adding new exploding models to the list. Only once the game iterates through the 
entire list without finding a new explosion will the checkExplosions flag be turned off. 

The checks involve iterating through a copy of the exploding list and checking to see if each model's exploded flag is false. If so, the game will create one attack for each model within the explosion range and handle the 
attacks in the standard way. Attacks will be grouped by unit for execution, with each attack assigning its model as the primary target. The game will also check to see if the model is part of a unit that has passengers,
and if so, allocated increased damage explosion attacks.

## Victory Points

- At the end of a turn, the game checks to see which objectives have been achieved and gives points accordingly.
- Ownership of control points are checked any time a unit moves or models in a unit die. These changes are always announced in the event log (e.g. Player 1 loses control of point #4! Point #4 is now contested!).
- The game only checks if “Conquest” and “Full Distance” have been achieved on the final turn of the game.
- “First Blood” and “Kingslayer” are announced as events as soon as they are achieved, but points are awarded at the end of the turn. 
- The player can only select “end turn”

# Part I: General/Misc

## Save data

Save data structure for armies is stated below. **Bold** indicates a file/database, *Italics* indicate a table, and bullet points indicate columns

**Army list**

*Army list**

- Name (PK)
- BossName
- BossTrait
- Faction
- TotalPoints
- TotalSP

**[Army Name]** (One file/DB per saved army)

*Detachments*

- DetachmentName
- DetachmentID
- DetachmentType

*Units*

- DetachmentID
- UnitID
- UnitData
- options
- spells

*Models*

- UnitID
- ModelData
- Invul
- Wargear

