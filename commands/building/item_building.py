# coding=utf-8
"""
Menus for editing item objects. Every item created with the make menu will
be dropped in the current room the builder is standing in.
"""
from evennia.contrib.building_menu import BuildingMenu
from evennia.utils import lazy_property
from world.handlers.traits import TraitHandler
from evennia.utils.logger import log_file
from evennia import create_object
from typeclasses.objects import Object

class ItemMakingMenu(BuildingMenu):

    """
    Building menu to create an item of a specific type. This menu will create
    a single copy or a specific number of items of a specific type. The
    object(s) created can then be edited individually with a different menu.
    Editing of the objects in this menu will be somewhat limited.
    """

    @lazy_property
    def traits(self):
        """TraitHandler that manages room traits."""
        return TraitHandler(self)

    def init(self, room):
        ## Flavor Item, general stuff in the room
        self.add_choice("|=zCreate an Item|n", "1", glance = """
        Create an item of a specific type. This will open a submenu of item type
        choices.
        """, text=text_item_creation,
        on_nomatch=nomatch_item_creation)


# Menu functions
def text_item_creation(caller, room):
    """Show the item creation choices in the choice itself."""
    text = "-" * 79
    text += """
|w1|n. |yFlavor Items|n are ordinary objects that add flavor to the room, but
are not normally intended to be equipped by players or NPCs. For
example, a road object, a rock, a column.

|w2|n. |yFurnishings|n are items that fill a room and can be used for things
like sitting or lying on them, or hanging them on a wall, or hanging
coats on, etc.

|w3|n. |yLight Sources|n are hand held or worn light sources that can be carried
by a player or NPC. Most light sources require fuel, which is generally
a consumable item.

|w4|n. |yRoads and Trails|n are objects that can be traveled upon. They generally
degrade in condition over time due to wear and weather.

|w5|n. |yComponents and Gatherables|n are objects that can be refined and/or
combined in order to craft or power other objects. These items are
generally found as raw materials.

|w6|n. |yConsumables|n are materials that are exhausted within a small, limited
number of uses. Fuel, first aid kits, firewood, etc.

|w7|n. |yBuildings are structures that can be entered. By default, creating a
a building will also create 3 other objects: an entry room inside the
building with coordinates 0,0 amd exits to and from the entry room.

|w8|n. |yArmor & Clothing, Jewelry|n are wearable items that may or may not provide
some passive benefit to the wearer.

|w9|n. |yWeapons|n are wieldable items that may or may not provide some passive
benefit to the wearer. They can generally be used to do damage of some
kind to others (or other items), but some weapons have other affects
like ensnaring the opponent.

|wA|n. |yTools|n are wieldable items that serve a specific function such as
digging, crafting, construction, etc. Most Tools can be used as
improvised weapons, but they generally won't be great weapons.

|wB|n. |yVehicles|n are items that can be used to move a lot of cargo from one
place to another. They generally can only travel in limited areas and
must have an appropriate power source to function (such as a draft
animal to pull a cart or a player to row a boat). Taking a vehicle to
a place it is not designed to go can damage or get the vehicle stuck.

|wC|n. |yKeys|n are items that can be used to open a specific item, exit, or set of
items and exits. This lock can sometimes be circumvented by skill or
force.
"""
    text += "\nType in |w<menu number or letter>|n. |510<Name of Item>|n to create the item"
    text += "\nExample: |w8|n. |510Boiled Leather Vest|n"
    text += "\n    - would create an item of subtype Armor named 'Boiled Leather Vest'."
    text += "\nType |w@|n to go back to the main menu."
    return text

def nomatch_item_creation(menu, caller, room, string):
    """
    The user types something into the submenu for item creation
    """
    option_num = string[:1]
    name_str = string[3:]
    if len(string) > 0:
        if option_num == '1':
            item = create_object('typeclasses.items.Item',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '2':
            item = create_object('typeclasses.items.Furnishing',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '3':
            item = create_object('typeclasses.items.LightSource',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '4':
            item = create_object('typeclasses.items.RoadsAndTrail',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '5':
            item = create_object('typeclasses.items.Component',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '6':
            item = create_object('typeclasses.items.Consumnable',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '7':
            item = create_object('typeclasses.items.Building',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '8':
            item = create_object('typeclasses.armors.Armor',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == '9':
            item = create_object('typeclasses.weapons.Weapon',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == 'A':
            item = create_object('typeclasses.items.Tool',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == 'B':
            item = create_object('typeclasses.items.Vehicle',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        elif option_num == 'C':
            item = create_object('typeclasses.items.Key',
                    key=name_str,
                    location=caller.location,
                    home=caller.location)
        if item:
            caller.msg(f"You create an item named {name_str}.")
    return
