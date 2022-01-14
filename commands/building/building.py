# coding=utf-8
"""
Building commands

This will be the set of commands that will open menus for those with permission
to edit in-game objects to do so. The menus will be a series of nested numbered
options that a builder can select until they get to a point where they are
editing a specific value on an object.

"""
from evennia.contrib.building_menu import BuildingMenu
from commands.command import Command
from commands.building.room_building import RoomSculptingMenu
from commands.building.item_building import ItemMakingMenu
from evennia import create_object
from typeclasses.objects import Object
from typeclasses.items import Building
from evennia.utils.logger import log_file
from evennia import utils as utils
from world.handlers.biomes import apply_biomes

class SculptCmd(Command):
    """
    Sculpting command.

    Usage:
        @sculpt [object]

    Opens a building menu to edit the specified object. This menu allows
    a builder to edit specific information about this object.

    Examples:
        @sculpt here
        @sculpt <character name>
        @sculpt #142

    NOTE: Please be careful editing your own character object. You can cause
          issues with your character or the game. With great powers...

    """
    key = '@sculpt'
    locks = 'cmd:id(1) or perm(Builders)'
    help_category = 'Building'

    def func(self):
        if not self.args.strip():
            self.msg("|rYou should provide an argument to this function: the object to edit.|n")
            return

        obj = self.caller.search(self.args.strip(), global_search=True)
        if not obj:
            return
        if utils.inherits_from(obj, 'typeclasses.rooms.Room'):
            Menu = RoomSculptingMenu
        else:
            self.msg("|rThe object {} cannot be edited.|n".format(obj.get_display_name(self.caller)))
            return


        menu = Menu(self.caller, obj)
        menu.open()


class FormItemCmd(Command):
    """
    Forming Command.

    Usage:
        @form

    Opens a building menu to create item objects of various types. This menu
    will only allow you to create a base item of a given type with a name you
    have chosen. To edit that item, exit the forming menu and use the sculpt
    command on the item.
    """
    key = '@form'
    locks = 'cmd:id(1) or perm(Builders)'
    help_category = 'Building'

    def func(self):
        Menu = ItemMakingMenu
        menu = Menu(self.caller, self.caller.location)
        menu.open()



class CoordinatesWormCmd(Command):
    """
    Command to update room coordinates.

    NOTE: This command is dangerous! It will update the coordinates of every
          room that is connected to this one by cardinal directions, and will
          do so based upon the coordinates in the room you are standing! Do not
          run this command unless you are sure you want to do so! This will also
          cause all sorts of havoc if your zone is not self-consistent from a
          cardinal direction standpoint.

    Usage:
        coordworm [room]

    Examples:
        coordworm here
        coordworm #2

    """
    key='@coordworm'
    locks = 'cmd:id(1) or perm(Admins)'
    help_category = 'Building'

    def func(self):
        if not self.args.strip():
            self.msg("|rYou should provide an argument to this function: the object to edit.|n")
            return
        room = self.caller.search(self.args.strip(), global_search=True)
        if room and utils.inherits_from(room, 'typeclasses.rooms.Room'):
            worm = create_object('commands.building.building.CoordinateWorm',
                                 key='worm',
                                 location=room)
            coords_reset = len(worm.has_mapped_room_ids)
            self.msg(f"{coords_reset} rooms have been updated with fresh coordinates.")
            worm.delete()
        else:
            self.msg("Searched room not found. provide a valid room for the worm to map")


class CoordinateWorm(Object):
    """
    A worm that travels through a zone and sets the coordinates of the rooms.
    Called by the 'coordworm' command.
    """

    def at_object_creation(self):
        self.zone = self.location.db.info['zone']
        self.outdoors = self.location.db.info['outdoor room']
        self.has_mapped = {}
        self.has_mapped_room_ids = []
        self.curX = self.location.traits.xcord.current
        self.curY = self.location.traits.ycord.current
        self.explore_map(self.location)


    def explore_map(self, room):
        """
        Explores the map via exits.
        """
        self.set_room_coordinates(room)
        for exit in room.exits:
            if exit.name not in ("north", "east", "west", "south", "northeast", \
                                 "northwest", "southeast", "southwest"):
                # we only map in the cardinal directions. Mapping up/down would be
                # an interesting learning project for someone who wanted to try it.
                continue
            if exit.destination.id in self.has_mapped_room_ids:
                # we've been to the destination already, skip ahead.
                continue

            self.update_pos(room, exit.name.lower())
            self.explore_map(exit.destination)


    def set_room_coordinates(self, room):
        """
        Sets the X and Y Coordinate traits for the room to match CurX and CurY
        """
        if room == self.location:
            self.has_mapped[room] = [self.curX, self.curY]
            self.has_mapped_room_ids.append(room.id)
        else:
            self.has_mapped[room] = [self.curX, self.curY]
            self.has_mapped_room_ids.append(room.id)
            room.traits.xcord.base = self.curX
            room.traits.ycord.base = self.curY
            room.db.info['zone'] = self.zone
            room.db.info['outdoor room'] = self.outdoors


    def update_pos(self, room, exit_name):
        # this ensures the pointer variables always
        # stays up to date to where the worm is currently at.
        self.curX, self.curY = \
           self.has_mapped[room][0], self.has_mapped[room][1]

        # now we have to actually move the pointer
        # variables depending on which 'exit' it found
        if exit_name == 'east':
            self.curX += 1
        elif exit_name == 'west':
            self.curX -= 1
        elif exit_name == 'north':
            self.curY += 1
        elif exit_name == 'south':
            self.curY -= 1
        elif exit_name == 'northeast':
            self.curX += 1
            self.curY += 1
        elif exit_name == 'southeast':
            self.curX += 1
            self.curY -= 1
        elif exit_name == 'northwest':
            self.curX += 1
            self.curY += 1
        elif exit_name == 'southwest':
            self.curX -= 1
            self.curY -= 1


class CreateBuildingCmd(Command):
    """
    This command creates a Building Item. When the building is created, this
    should in turn create and entry room inside the building object (which is
    in turn inside the caller's current location) and the exits between the
    new entryway room and the caller's current location.

    Usage:
        @createbuilding <building's name>

    Examples:
        @createbuilding A Large Stone Inn

    """
    key = '@createbuilding'
    locks = 'cmd:id(1) or perm(Builders)'
    help_category = 'Building'

    def func(self):
        if not self.args.strip():
            self.msg("|rYou should provide a name for the building!|n")
            return
        outdoor_room = self.caller.location.id
        building = create_object('typeclasses.items.Building',
                key=self.args.strip(),
                location=self.caller.location,
                home=self.caller.location)
        self.caller.execute_cmd(f"open enter building;enter,exit building;exit = #{building.db.entryway.id}")
        self.caller.msg("You create a building")
