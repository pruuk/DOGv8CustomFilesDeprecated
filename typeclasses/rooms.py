# coding=utf-8
"""
Room

Rooms are simple containers that has no location of their own.

"""
from evennia import utils as utils
from evennia import DefaultRoom
from evennia.utils.logger import log_file
from evennia.utils import lazy_property
from world.handlers.traits import TraitHandler
from world.handlers.biomes import apply_biomes
import time
from world.randomness_controller import distro_return_a_roll as roll
from world.randomness_controller import distro_return_a_roll_sans_crits as rarsc
from world.handlers.map import Map
from evennia.utils import evform, evtable
from evennia.utils.utils import (
    class_from_module,
    variable_from_module,
    lazy_property,
    make_iter,
    is_iter,
    list_to_string,
    to_str,
)
from evennia import create_object
from typeclasses.exits import Exit
from collections import defaultdict


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    # pull in handlers for traits, equipment, mutations, talents
    @lazy_property
    def traits(self):
        """TraitHandler that manages room traits."""
        return TraitHandler(self)

    @lazy_property
    def mutations(self):
        """TraitHandler that manages room mutations."""
        # note: These will be used rarely for rooms
        return TraitHandler(self, db_attribute='mutations')

    @lazy_property
    def biomes(self):
        """TraitHandler that manages room biomes."""
        # note: These will be used rarely for rooms
        return TraitHandler(self, db_attribute='biome')

    @lazy_property
    def status_effects(self):
        """TraitHandler that manages room status effects."""
        return TraitHandler(self, db_attribute='status_effects')

    def at_object_creation(self):
        "Called only at object creation and with update command."
        # clear traits and trait-like containers
        self.traits.clear()
        self.mutations.clear()
        self.biomes.clear()
        self.status_effects.clear()

        # Add traits for the standard room. We'll add more room types as
        # subclasses and subclasses to give devs some stock rooms to wor from

        # size is measured in square meters. Default is a large outdoor room
        self.traits.add(key="size", name='Room Size', type='static', base=10000)
        ## note that base encumberance, carrying capacity of a room is set
        ## as a square of the room size
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=(self.traits.size.current ** 2), \
                        extra={'learn' : 0})
        # Elevation is measure in meters above sea level outdoors. Inside, the
        # 'ground' floor is 0. Every floor below is -N and above is +N floors
        self.traits.add(key='elev', name='Elevation Above Sea Level', \
                        type='static', base=100)
        # rather than using latitude and longitude, we're using a coordinate
        # system based upon the number of outdoor rooms away from the main
        # entrance and exit of the newbie school. That room will be 0,0 and all
        # other outdoor rooms *must* confirm to this standard. Indoor rooms
        # will have their own grid that is internally consistent
        self.traits.add(key='xcord', name='X Coordinate', type='static', \
                        base=0) # PLEASE CHANGE THIS AFTER CREATING A ROOM!
        self.traits.add(key='ycord', name='Y Coordinate', type='static', \
                        base=0) # PLEASE CHANGE THIS AFTER CREATING A ROOM!
        # rot is a masure of how steep the terrain is in this room on average
        # This should be a value between 0 and 1. For most rooms, this value
        # shouldn't exceed .25; Only the most extreme environments would be
        # more rugged than that
        self.traits.add(key='rot', name='Ruggedness of Terrain', \
                        type='static', base=0.03)
         # maximum number of tracks to store. Some terrain allows for tracks to
        # be readable even with a large amount of foot traffic.
        self.traits.add(key="trackmax", name="Maximum Readable Tracks", \
                        type="static", base=(round(self.traits.size.actual / 500))) # default of 20
        # boolean info attributes of the room
        self.db.info = {'non-combat room': False, 'outdoor room': True, \
                        'zone': 'The Outdoors'}
        # empty db attribute dictionary for storing tracks
        self.db.tracks = {}

        # add the overhead map symbol we want to use
        self.db.map_symbol = ['|043¡|n', '|143¡|n', '|243¡|n', '|343¡|n', '|443¡|n']

        # add biome info. Biome types should be expressed in a number between 0
        # and 1. The total set of biomes added should add up to 1.
        apply_biomes(self)


    def return_appearance(self, looker):
        """ Returns custom appearance for the room, including overhead map. """
        visible = (con for con in self.contents if con != looker and con.access(looker, "view"))
        exits, users, things = [], [], defaultdict(list)
        for con in visible:
            key = con.get_display_name(looker)
            if con.destination:
                exits.append(key)
            elif con.has_account:
                users.append("|c%s|n" % key)
            else:
                # things can be pluralized
                things[key].append(con)
        # get description, build string
        string = ""
        exits_descs = ""
        thing_strings = []
        desc = self.db.desc
        if desc:
            string += "%s" % desc
        if exits:
            exits_descs += "|cExits:|n " + list_to_string(exits)
        if users or things:
            # handle pluralization of things (never pluralize users)
            for key, itemlist in sorted(things.items()):
                nitem = len(itemlist)
                if nitem == 1:
                    key, _ = itemlist[0].get_numbered_name(nitem, looker, key=key)
                else:
                    key = [item.get_numbered_name(nitem, looker, key=key)[1] for item in itemlist][
                        0
                    ]
                thing_strings.append(key)

        room_contents = "\n|wYou see:|n " + list_to_string(users + thing_strings)
        room_text = string + "\n\n" + room_contents + "\n\n" + exits_descs
        # Putting room description and map in a table format
        coord_string = f" |510Map Coordinates|n ---> |wX: |510{self.traits.xcord.current}|n, |wY: |510{self.traits.ycord.current}|n"
        map = str(Map(looker).show_map())
        desc = str(super().return_appearance(looker))
        table = evtable.EvTable(coord_string, f"|c{self.get_display_name(looker)}|n",
            table=[], border="tablecols")
        table.reformat_column(0, width=46, align="l", valign="c", evenwidth=True)
        table.reformat_column(1, width=54, align="l", valign="c", evenwidth=True)
        table.add_row(Map(looker).show_map(), room_text)
        self.ndb.nearby_rooms = looker.ndb.nearby_rooms
        self.db.room_map = evform.EvForm("world/handlers/mapform.py")
        mobs = "|cMobiles:|n "
        items = "|cItems:|n "
        buildingsntowns = "|cEntrances:|n "
        roads = "|cRoads:|n "
        for obj in self.contents:
            if utils.inherits_from(obj, 'typeclasses.characters.Character'):
                if obj != looker:
                    mobs += obj.get_display_name(looker) + ","
            elif utils.inherits_from(obj, 'typeclasses.items.Item') and \
                not (utils.inherits_from(obj, 'typeclasses.items.Building') or \
                utils.inherits_from(obj, 'typeclasses.items.Town') or \
                utils.inherits_from(obj, 'typeclasses.items.RoadsAndTrail')):
                items += obj.get_display_name(looker)  + ","
            elif utils.inherits_from(obj, 'typeclasses.items.Building') or \
                utils.inherits_from(obj, 'typeclasses.items.Town'):
                buildingsntowns += obj.get_display_name(looker) + ","
            elif utils.inherits_from(obj, 'typeclasses.items.RoadsAndTrail'):
                roads += obj.get_display_name(looker)  + ","
        room_name = f"|c{self.get_display_name(looker)}|n"
        room_desc = str(self.db.desc)
        room_roads = roads.strip(", ")
        room_items = items.strip(", ") + "\n\n" + mobs.strip(", ")
        entr_n_exits = buildingsntowns.strip(", ") + "\n\n" + exits_descs
        map += f"\n|cZone: |440{self.db.info['zone']}|n"
        self.db.room_map.map(cells={1: room_name, \
                        2: coord_string, \
                        3: room_desc, \
                        4: room_items, \
                        5: room_roads, \
                        6: entr_n_exits, \
                        7: map})
        if self.db.room_map:
            return self.db.room_map
        else:
            return table

    def reset_biomes(self):
        """ Resets biomes on this room """
        self.biomes.clear()
        apply_biomes(self)


class IndoorRoom(Room):
    """
    Subtype of room that is indoors
    """
    def at_object_creation(self):
        "Called only at object creation and with update command."
        super(Room, self).at_object_creation()
        self.traits.size.base = 25 # standard of 25 meters square
        self.traits.enc.base = 10000
        self.traits.rot.base = 0
        self.traits.elev.base = 0
        self.traits.trackmax.base =  3
        self.db.info['outdoor room'] = False
        self.db.info['zone'] = None
        self.db.map_symbol = ['|155:|n','|255:|n','|355:|n','|455:|n','|555:|n']


class BuildingEntrance(IndoorRoom):
    """
    Special subtype of Indoor Room that is only created when a building is
    created. This room will be in the inventory of the building and will be
    connected to the room the outdoor building is inside of with an exit
    named 'exit building'.
    """
    def at_object_creation(self):
        "Called only at object creation and with update command."
        super(IndoorRoom, self).at_object_creation()
        self.traits.size.base = 25 # standard of 25 meters square
        self.traits.enc.base = 10000
        self.traits.rot.base = 0
        self.traits.elev.base = 0
        self.traits.trackmax.base =  3
        self.db.info['outdoor room'] = False
        self.db.info['zone'] = None
        self.db.map_symbol = ['|155:|n','|255:|n','|355:|n','|455:|n','|555:|n']
        self.desc = "An entrance room for the building"


class TownEntrance(Room):
    """
    Special subtype of Room that represents the first room inside a town.
    """
    def at_object_creation(self):
        "Called only at object creation and with update command."
        super().at_object_creation()
        self.traits.size.base = 100 # standard of 100 meters square
        self.traits.enc.base = 1000000
        self.traits.rot.base = 0
        self.traits.elev.base = 0
        self.traits.trackmax.base =  10
        self.db.info['outdoor room'] = True
        self.db.info['zone'] = None
        self.db.map_symbol = ['|155©|n','|255©|n','|355©|n','|455©|n','|555©|n']
        self.desc = "An entrance room for the building"
