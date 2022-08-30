
## Army customisation/Game Setup

### Stage 2

- Rework battlefields to be stored as SQLite data instead of being created in the script. 
- ~~Ability to load armies for editing.~~
- ~~Set up all remaining wargear.~~

## Wargaming

### Stage 2

- ~~Add the closest visible unit rule for the magic phase.~~
- Set up all spells for Paladins and Orcs.
- Add model abilities.
- Add weapon abilities.
- ~~Add transports~~.
	- ~~Need to fix bug where transports can move, disembark a unit, and then cancel their move.~~
	- ~~Need to fix bug where unit is embarked onto a transport from the deployment phase, even if the deployment of that unit onto the transport was cancelled~~
	- ~~Need to fix a bug where dead models can disembark from transports.
- ~~Add two weapon attack speed bonus.~~
- Amend get_disembark_nodes and check_explosions methods to cut down on duplicate code
- Double check morale phase code
- Remove references to checking if a model is dead and/fled as only dead needs to be checked

## Game Setup/Other

### Stage 2

- ~~Change font.~~
- Update bad sprites.
- Update UI.
- Look into Cython to speed up pathfinding.

## Content

### Stage 2

- Add second battlefield.
- Add all Paladin and Orc model sprites.