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
from evennia import DefaultObject

# the symbol is identified with a key "sector_type" on the
# Room. Keys None and "you" must always exist.
# TODO: Expand the symbols dictionary to include nested dicts for all of the
# factors listed above
SYMBOLS = { None : ' . ', # unknown type, outdoors
            'CHAR_INDOOR' : '|=z[@]|n', # the room we're in, if we're indoors
            'CHAR_OUTDOOR' : '|=z @ |n', # the room we're in, if we're indoors
            'SECT_INSIDE': '[.]' }

class Map(object):

    def __init__(self, caller, max_width=15, max_length=15):
        self.caller = caller
        self.caller_location = caller.location
        self.max_width = max_width
        self.max_length = max_length
        self.worm_has_mapped = {}
        self.curX = None
        self.curY = None

        if self.check_grid():
            # we actually have to store the grid into a variable
            self.grid = self.create_grid()
            self.draw_room_on_map(caller.location,
                                 ((min(max_width, max_length) -1 ) / 2))

    def update_pos(self, room, exit_name):
        # this ensures the pointer variables always
        # stays up to date to where the worm is currently at.
        self.curX, self.curY = \
           self.worm_has_mapped[room][0], self.worm_has_mapped[room][1]

        # now we have to actually move the pointer
        # variables depending on which 'exit' it found
        if exit_name == 'east':
            self.curY += 1
        elif exit_name == 'west':
            self.curY -= 1
        elif exit_name == 'north':
            self.curX -= 1
        elif exit_name == 'south':
            self.curX += 1

    def draw_room_on_map(self, room, max_distance):
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
        # draw initial caller location on map first!
        if room == self.caller.location:
            self.start_loc_on_grid()
            self.worm_has_mapped[room] = [self.curX, self.curY]
        else:
            # map all other rooms
            self.worm_has_mapped[room] = [self.curX, self.curY]
            # this will use the sector_type Attribute or None if not set.
            self.grid[self.curX][self.curY] = SYMBOLS[room.db.sector_type]

    def median(self, num):
        lst = sorted(range(0, num))
        n = len(lst)
        m = n -1
        return (lst[n//2] + lst[m//2]) / 2.0

    def start_loc_on_grid(self):
        x = self.median(self.max_width)
        y = self.median(self.max_length)
        # x and y are floats by default, can't index lists with float types
        x, y = int(x), int(y)


        # establish if the caller is indoors or outdoors
        if self.caller_location.db.info['Outdoor Room']:
            # Caller's location is outdoors
            self.grid[x][y] = SYMBOLS['CHAR_OUTDOOR']
        else:
            # Caller's location is indoors
            self.grid[x][y] = SYMBOLS['CHAR_INDOOR']
        self.curX, self.curY = x, y # updating worms current location


    def has_drawn(self, room):
        return True if room in self.worm_has_mapped.keys() else False


    def create_grid(self):
        # This method simply creates an empty grid
        # with the specified variables from __init__(self):
        board = []
        for row in range(self.max_width):
            board.append([])
            for column in range(self.max_length):
                board[row].append('   ')
        return board

    def check_grid(self):
        # this method simply checks the grid to make sure
        # both max_l and max_w are odd numbers
        return True if self.max_length % 2 != 0 or \
                    self.max_width % 2 != 0 else False

    def show_map(self):
        map_string = ""
        for row in self.grid:
            map_string += " ".join(row)
            map_string += "\n"

        return map_string
