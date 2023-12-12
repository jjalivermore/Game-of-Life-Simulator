# Game of Life Simulator
Welcome to my Game of Life Simulator!
This is an implementation of Conway's Game of Life in Python using Pygame

## Features
- Configuration editor with a set of built-in shapes
- Various options accessible by menu
- Customisable rule sets
- Customisable display colours
- Loading and saving configurations
- Antimatter mode

## Getting started
- Run Game_of_Life.py to start at the main menu
- Alternatively import as a module and run main (accepts configuration file name to load as argument)
- Main function returns two values: list of cell numbers and list of historical configurations

## Instructions
- From main menu, choose starting configuration or options
- Simulation starts from editor view, where the configuration can be edited
- Spacebar runs/pauses (returns to editor)

## Saving configurations
- Saving can be done from the editor
- Save files are pickled (.pkl) in working directory
- Configuration and options are saved

## Options
1. Toggle whether simulation areas edges wrap around (toroidal simulation area)
2. Choose block size in pixels
3. Change maximum frames per second
4. Cycle through coour sets
5. Choose rule set in Birth/Survival notation (https://conwaylife.com/wiki/Rulestring) e.g. Conway's ruleset is B2/S23
6. Toggle antimatter mode - this mode features cells with -1 life value, updating with negative neighbour numbers
