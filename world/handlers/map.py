"""
Map handler

This file contains an object class that 'worms' through the local environment
and displayus an overhead map dynamically to the players. The worm will be
determining the overhead map based upon a number of factors, including:
- The biome of the rooms
- The relative elevation of the rooms
- The weather (affects visibility)
- Status effects on the character, such as blindness
- The time of day
- Indoor vs. outdoor
- Has the character been in the room recently?
- Is the character flying?

All rooms in DOG have a coordinate trait. Outdoor rooms have a self-consistent
set of coordinates that apply globally. Indoor rooms have coordinates that are
self consistent within the local zone.

The room the character is currently occupying will have the '@' symbol in it.
Rooms that are visible from the character's current perspective, but are of an
unknown type will have a '.' symbol for outdoor rooms and '[.]' for indoor
rooms.

Color is used to establish the relative elevation of a room the character can
perceive in relation to where they are standing.

"""
from evennia import create_object
from evennia import DefaultObject
from evennia.utils.logger import log_file
from statistics import median
from evennia import EvForm, EvTable

BASE_MAP_GRID = """\
█████████████████████
██████████ ██████████
████████     ████████
████████ · · ████████
██████         ██████
██████ · · · · ██████
████             ████
████ · · · · · · ████
██                 ██
██ · · · · · · · · ██
█         @         █
██ · · · · · · · · ██
██                 ██
████ · · · · · · ████
████             ████
██████ · · · · ██████
██████         ██████
████████ · · ████████
████████     ████████
██████████ ██████████
█████████████████████
"""
MAPPABLE_ROOM_COORDS = \
[[10,10],[8,10],[6,10],[4,10], [2,10], [0,10], [12,10], [14,10], [16,10], \
[18,10],[20,10], [10,8],[10,6],[10,4],[10,2],[10,0],[10,12],[10,14],[10,16], \
[10,18],[10,20],[8,2],[12,2],[6,4],[8,4],[12,4],[14,4],[4,6],[6,6],[8,6],[12,6], \
[14,6],[16,6],[2,8],[4,8],[6,8],[8,8],[12,8],[14,8],[16,8],[18,8], [8,18], \
[12,18],[6,16],[8,16],[12,16],[14,16],[4,14],[6,14],[8,14],[12,14], \
[14,14],[16,14],[2,12],[4,12],[6,12],[8,12],[12,12],[14,12],[16,12],[18,12]]

# the symbol is identified with a key "sector_type" on the
# Room. Keys None and "you" must always exist.
# TODO: Expand the symbols dictionary to include nested dicts for all of the
# factors listed above
SYMBOLS = { None : ' . ', # unknown type, outdoors
            'CHAR_INDOOR' : '|=z@|n', # the room we're in, if we're indoors
            'CHAR_OUTDOOR' : '|=z@|n', # the room we're in, if we're indoors
            'CROSSROADS': '╬',
            'SECT_INSIDE': '.' }

class Map(object):

    def __init__(self, caller, max_width=21, max_length=21):
        log_file("Starting __init__ func", filename='map_debug.log')
        self.caller = caller
        self.caller_location = caller.location
        self.max_width = max_width
        self.max_length = max_length
        self.worm_has_mapped = {}
        self.curX = None
        self.curY = None

        # we actually have to store the grid into a variable
        self.grid = self.create_grid()
        log_file(f"{type(self.grid)}", filename='map_debug.log')
        log_file(f"{self.grid}", filename='map_debug.log')
        self.draw_room_on_map(caller.location,
                             ((min(max_width, max_length) -1 ) / 2))

    def update_pos(self, room, exit_name):
        log_file("Starting update_pos func", filename='map_debug.log')
        # this ensures the pointer variables always
        # stays up to date to where the worm is currently at.
        self.curX, self.curY = \
           self.worm_has_mapped[room][0], self.worm_has_mapped[room][1]

        # now we have to actually move the pointer
        # variables depending on which 'exit' it found
        if exit_name == 'east':
            if [self.curX, self.curY] in MAPPABLE_ROOM_COORDS:
                self.draw_exit('horizontal', self.curX, (self.curY + 1) )
            self.curY += 2
        elif exit_name == 'west':
            if [self.curX, self.curY] in MAPPABLE_ROOM_COORDS:
                self.draw_exit('horizontal', self.curX, (self.curY - 1) )
            self.curY -= 2
        elif exit_name == 'north':
            if [self.curX, self.curY] in MAPPABLE_ROOM_COORDS:
                self.draw_exit('vertical', (self.curX - 1), self.curY)
            self.curX -= 2
        elif exit_name == 'south':
            if [self.curX, self.curY] in MAPPABLE_ROOM_COORDS:
                self.draw_exit('vertical', (self.curX + 1), self.curY)
            self.curX += 2

    def draw_room_on_map(self, room, max_distance):
        log_file("Starting draw_room_on_map func", filename='map_debug.log')
        self.draw(room)

        if max_distance == 0:
            return

        for exit in room.exits:
            if exit.name not in ("north", "east", "west", "south"):
                # we only map in the cardinal directions. Mapping up/down would be
                # an interesting learning project for someone who wanted to try it.
                continue
            if self.has_drawn(exit.destination):
                # we've been to the destination already, skip ahead.
                continue

            self.update_pos(room, exit.name.lower())
            self.draw_room_on_map(exit.destination, max_distance - 1)


    def draw(self, room):
        log_file("Starting draw func", filename='map_debug.log')
        # draw initial caller location on map first!
        if room == self.caller.location:
            self.start_loc_on_grid()
            self.worm_has_mapped[room] = [self.curX, self.curY]
        else:
            # map all other rooms
            self.worm_has_mapped[room] = [self.curX, self.curY]
            # this will use the sector_type Attribute or None if not set.
            if [self.curX, self.curY] in MAPPABLE_ROOM_COORDS:
                if room.db.map_symbol:
                    log_file(f"Draw... Checking X: {self.curX}, Y: {self.curY}", filename='map_debug.log')
                    self.grid[self.curX][self.curY] = room.db.map_symbol
                else:
                    self.grid[self.curX][self.curY] = SYMBOLS[room.db.sector_type]


    def draw_exit(self, type, ExitX, ExitY):
        log_file("Starting draw exit func", filename='map_debug.log')
        if 0 < ExitX < self.max_width and 0 < ExitY < self.max_length:
            # draw in the exits
            if type == 'vertical':
                self.grid[ExitX][ExitY] = '|'
            elif type == 'horizontal':
                self.grid[ExitX][ExitY] = '-'
            else:
                log_file("Unknown exit type", filename='map_debug.log')


    def median(self, num):
        log_file("Starting median func", filename='map_debug.log')
        list_of_slots = sorted(range(0, num))
        return median(list_of_slots)


    def start_loc_on_grid(self):
        log_file("Starting start_loc_on_grid func", filename='map_debug.log')
        x = self.median(self.max_width)
        y = self.median(self.max_length)
        log_file(f"Median X: {x} Median Y: {y}", filename='map_debug.log')
        # x and y are floats by default, can't index lists with float types
        x, y = int(x), int(y)

        if self.caller_location.db.info['outdoor room']:
            self.grid[x][y] = SYMBOLS['CHAR_OUTDOOR']
        else:
            self.grid[x][y] = SYMBOLS['CHAR_INDOOR']
        self.curX, self.curY = x, y # updating worms current location


    def has_drawn(self, room):
        log_file("Starting has_drawn func", filename='map_debug.log')
        return True if room in self.worm_has_mapped.keys() else False


    def create_grid(self):
        # pull in base map grid and split it so the individual positions
        # can be called by index number
        log_file("Starting create_grid func", filename='map_debug.log')
        board = BASE_MAP_GRID.split('\n')
        index = 0
        for line in board:
        	line = list(line)
        	board[index] = line
        	index += 1

        return board


    def show_map(self):
        map_string = ""
        log_file("Starting show_map func", filename='map_debug.log')
        for row in self.grid:
            map_string += " ".join(row)
            map_string += "\n"

        return map_string
