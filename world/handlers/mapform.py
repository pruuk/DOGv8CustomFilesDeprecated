# coding=utf-8
"""
This file contains the form that will be used to show the contents of rooms
plus a mini-map in a side by side format.
"""

# Evform and EvTable will be used to return the map as a side map
DESCCHAR = 'd'
MAPCHAR = 'X'
COORDCHAR = 'c'
ROOM_DISPLAY_FORM = """
*------------------------------------------------.-----------------------------*
|                                                |                             |
|   1ddddddddddddddddddddddddddddddddddddddddd   |   2XXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |   XXXXXXXXXXXXXXXXXXXXX     |
|   dddddddddddddddddddddddddddddddddddddddddd   |                             |
|   dddddddddddddddddddddddddddddddddddddddddd   |   MAP COORDINATES:          |
|   dddddddddddddddddddddddddddddddddddddddddd   |     3cccccccccccccccccc     |
|                                                |                             |
*------------------------------------------------^-----------------------------*
