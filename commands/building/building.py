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

        if obj.typename == "Room":
            Menu = RoomSculptingMenu
        else:
            self.msg("|rThe object {} cannot be edited.|n".format(obj.get_display_name(self.caller)))
            return

        menu = Menu(self.caller, obj)
        menu.open()
