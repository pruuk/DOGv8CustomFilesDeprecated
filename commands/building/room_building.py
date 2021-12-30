"""
Menus for editing room objects.
"""
from evennia.contrib.building_menu import BuildingMenu
from evennia.utils import lazy_property
from world.handlers.traits import TraitHandler

class RoomSculptingMenu(BuildingMenu):

    """
    Building menu to edit a room.
    """

    @lazy_property
    def traits(self):
        """TraitHandler that manages room traits."""
        return TraitHandler(self)

    def init(self, room):
        self.add_choice("|=zTitle|n", key="1", attr="key", glance="|y{obj.key}|n", text="""
                -------------------------------------------------------------------------------
                Editing the title of {{obj.key}}(#{{obj.id}})

                You can change the title simply by entering it.
                Use |y{back}|n to go back to the main menu.

                Current title: |c{{obj.key}}|n
        """.format(back="|n or |y".join(self.keys_go_back)))
        self.add_choice_edit("|=zDescription|n", "2")
        self.add_choice("|=zExits|n", "3", glance=glance_exits, text=text_exits,
            on_nomatch=nomatch_exits)
        self.add_choice("|=zInfo Attributes|n", "4", glance=glance_info_attrs,
            text=text_info, on_nomatch=nomatch_info)
        self.add_choice("|=zTraits|n", "5", glance=glance_traits,
            text=text_traits, on_nomatch=nomatch_traits)
        self.add_choice("|=zUpdate the Room to Current Spec|n", "6",
            glance=glance_update, on_enter=update_on_enter)


# Menu functions
def glance_exits(room):
    """Show the room exits."""
    if room.exits:
        glance = ""
        for exit in room.exits:
            glance += "\n  |y{exit}|n".format(exit=exit.key)

        return glance

    return "\n  |gNo exit yet|n"


def glance_info_attrs(room):
    """Show the info Attributes"""
    if room.db.info:
        glance = ""
        for info_attr, info_value in room.db.info.items():
            glance += f"\n  |y{info_attr}: |Y{info_value}|n"
        return glance
    return "\n No valid info attributes. Please update room to current base spec."


def glance_traits(room):
    """Show the Room's Traits"""
    glance = ""
    if room.traits:
        glance += f"\n  |yRoom Size (in Square Meters): |Y{room.traits.size.current}|n"
        glance += f"\n  |yRoom Elevation (in Meters Above Sea Level): |Y{room.traits.elev.current}|n"
        glance += f"\n  |yX Coordinate: |Y{room.traits.xcord.current}|n"
        glance += f"\n  |yY Coordinate: |Y{room.traits.ycord.current}|n"
        glance += f"\n  |yY Ruggedness of Terrain (Slope from 0 = flat to 1 = vertical): |Y{room.traits.rot.current}|n"
    else:
        glance += "No traits defined."
    return glance


def glance_update(room):
    """ Show the glance warning text for updating """
    glance = ""
    glance += "|y\n  Updating the object will overwrite all of the room's current values"
    glance += "\n  and update the room to have the standard set of properties that any"
    glance += "\n  brand new room will have.|n"
    glance += "\n  |YNOTE: Updating the room will execute the command and exit you from"
    glance += "\n  the sculpting menu.|n"
    return glance


def text_exits(caller, room):
    """Show the room exits in the choice itself."""
    text = "-" * 79
    text += "\n\nRoom exits:"
    text += "\n Use tunnel or dig commands (outside these menus) to create new rooms and exits."
    text += "\n Use @ to return to the previous menu."
    text += "\n To edit a specific exit use something like '@3 east'"
    text += "\n\nExisting exits:"
    if room.exits:
        for exit in room.exits:
            text += "\n  |y@3 {exit}|n".format(exit=exit.key)
            if exit.aliases.all():
                text += " (|y{aliases}|n)".format(aliases="|n, |y".join(
                        alias for alias in exit.aliases.all()))
            if exit.destination:
                text += " toward {destination}".format(destination=exit.get_display_name(caller))
    else:
        text += "\n\n |gNo exit has yet been defined.|n"

    return text


def text_info(caller,room):
    """ Show the room info attrs in the main menu """
    text = "-" * 79
    text += "\n\nRoom Attributes:"
    index_num = 0
    if room.db.info:
        for info_attr, info_value in room.db.info.items():
            index_num += 1
            text += f"\n {index_num}. |y{info_attr}: |Y{info_value}|n"
        text += "\n\n To edit an item, type in something like:"
        text += "\n 1. True"
        text += "\n This example will set the Non-Combat boolean to True"
    else:
        text += "\n\n |gNo room attributes have been defined.|n"
    return text


def text_traits(caller, room):
    """ Show the traits info as a textual submenu"""
    text = "-" * 79
    text += "\n\nEditable Room Traits:"
    text += f"\n  1. |yRoom Size (in Square Meters): |Y{room.traits.size.current}|n"
    text += f"\n  2. |yRoom Elevation (in Meters Above Sea Level): |Y{room.traits.elev.current}|n"
    text += f"\n  3. |yX Coordinate: |Y{room.traits.xcord.current}|n"
    text += f"\n  4. |yY Coordinate: |Y{room.traits.ycord.current}|n"
    text += f"\n  5. |yY Ruggedness of Terrain (Slope from 0 = flat to 1 = vertical): |Y{room.traits.rot.current}|n"
    text += "\n\n  Note: Changing the size of a room will also change its carrying capacity."
    text += "\n\n  Example: 3. 1 will change the X Coordinate to 1"
    text += "\n  Type |y@|n to return to the main menu."
    return text


def nomatch_traits(menu, caller, room, string):
    """
    The user types in something.

    """
    cmd_str = string[3:]
    if len(string) > 2:
        if string[:1] == '1':
            room.traits.size.base = int(cmd_str)
            room.traits.enc.base = room.traits.size.current ** 2
            caller.msg(f"Set Size to: {room.traits.size.current}")
        elif string[:1] == '2':
            room.traits.elev.base = int(cmd_str)
            caller.msg(f"Set Elevation to: {room.traits.elev.current}")
        elif string[:1] == '3':
            room.traits.xcord.base = int(cmd_str)
            caller.msg(f"Set X Coordinate to: {room.traits.xcord.current}")
        elif string[:1] == '4':
            room.traits.ycord.base = int(cmd_str)
            caller.msg(f"Set Y Coordinate to: {room.traits.ycord.current}")
        elif string[:1] == '5':
            room.traits.rot.base = float(cmd_str)
            caller.msg(f"Set Ruggedness of Terrain to: {room.traits.rot.current}")
        else:
            caller.msg("Unknown Command")
            return False
    return


def nomatch_info(menu, caller, room, string):
    """
    The user types in something.

    """
    cmd_str = string[3:]
    if len(string) > 0:
        if string[:1] == '1':
            caller.execute_cmd(f"set here/info['Non-Combat Room'] = {cmd_str}")
        elif string[:1] == '2':
            caller.execute_cmd(f"set here/info['Outdoor Room'] = {cmd_str}")
        elif string[:1] == '3':
            caller.execute_cmd(f"set here/info['Zone'] = {cmd_str}")
        else:
            caller.msg("Unknown Command")
            return False
    return


def nomatch_exits(menu, caller, room, string):
    """
    The user typed something in the list of exits.  Maybe an exit name?
    """
    string = string[3:]
    exit = caller.search(string, candidates=room.exits)
    if exit is None:
        return

    # Open a sub-menu, using nested keys
    caller.msg("Editing: {}".format(exit.key))
    menu.open_submenu("commands.building.room_building.ExitBuildingMenu", exit, parent_keys=["3"])
    return False


def update_on_enter(caller):
    """
    The user can update the room to current base spec.
    """
    caller.execute_cmd("update here")
    return



class ExitBuildingMenu(BuildingMenu):
    """
    Building submenu to edit an exit.
    """

    def init(self, exit):
        self.add_choice("key", key="1", attr="key", glance="{obj.key}")
        self.add_choice_edit("description", "2")
