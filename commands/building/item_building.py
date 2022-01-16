# coding=utf-8
"""
Menus for editing item objects. Every item created with the make menu will
be dropped in the current room the builder is standing in.
"""
from evennia.contrib.building_menu import BuildingMenu
from evennia.utils import lazy_property
from evennia import utils as utils
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
        on_nomatch=nomatch_item_creation),
        self.add_choice("|=zDelete an Item|n", "2",
        text=text_delete,
        on_nomatch=nomatch_item_deletion)


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

|w7|n. |yTraps|n are items that can apply some kind of status effect to players
or NPCs. For example, a spiked pit trap might apply the bleeding status effect.

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

def text_delete(caller, room):
    """ Shows text with a list of items to delete."""
    text = "-" * 79
    text += "\nItems in room:"
    index = 0
    for item in room.contents:
        if utils.inherits_from(item, 'typeclasses.items.Item'):
            index += 1
            text += f"\n    {index}. {item.key}"
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
            item = create_object('typeclasses.items.Trap',
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


def nomatch_item_deletion(menu, caller, room, string):
    """
    The user types something into the submenu for item deletion
    """
    option_num = string[:1]
    index = 0
    for item in room.contents:
        if utils.inherits_from(item, 'typeclasses.items.Item'):
            index += 1
            if int(option_num) == index:
                caller.msg(f"Deleting {item.key}")
                item.delete()

class ItemSculptingMenu(BuildingMenu):
    """
    Menu and submenus for making edits to items and the subtypes of items.
    """
    @lazy_property
    def traits(self):
        """TraitHandler that manages item traits."""
        return TraitHandler(self)

    def init(self, item):
        self.item = item
        self.add_choice("|=zTitle|n", key="1", attr="key", glance="|y{obj.key}|n", text="""
                -------------------------------------------------------------------------------
                Editing the title of {{obj.key}}(#{{obj.id}})

                You can change the title simply by entering it.
                Use |y{back}|n to go back to the main menu.

                Current title: |c{{obj.key}}|n
        """.format(back="|n or |y".join(self.keys_go_back)))
        self.add_choice_edit("|=zDescription|n", "2")
        self.add_choice("|=zTraits|n", "3", glance=glance_traits,
            text=text_traits, on_nomatch=nomatch_traits)

#menu functions
def glance_traits(item):
    """Show the Room's Traits"""
    glance = ""
    if item.traits:
        glance += f"\n  |yValue: |Y{item.traits.val.current}|n"
        glance += f"\n  |yMass: |Y{item.traits.mass.current}|n"
        glance += f"\n  |yHPs: |Y{item.traits.hp.current}|n"
        glance += f"\n  |yQuality: |Y{item.traits.qual.current}|n"
        glance += f"\n  |yCondition: |Y{item.traits.cond.current}|n"
        glance += f"\n  |yCapacity: |Y{item.traits.cap.current}|n"
        if item.traits.comfort:
            glance += f"\n  |yComfort: |Y{item.traits.comfort.current}|n"
        if item.traits.light:
            glance += f"\n  |yLight: |Y{item.traits.light.current}|n"
        if item.traits.charge:
            glance += f"\n  |yCharges: |Y{item.traits.charge.current}|n"
    else:
        glance += "No traits defined."
    return glance


def text_traits(caller, item):
    """ Show the traits info as a textual submenu"""
    text = "-" * 79
    text += "\n\nEditable Item Traits:"
    text += f"\n  1. |yItem Value (in coppers): |Y{item.traits.val.current}|n"
    text += f"\n  2. |yItem Mass (in kilograms): |Y{item.traits.mass.current}|n"
    text += f"\n  3. |yItem Health: |Y{item.traits.hp.current}|n"
    text += f"\n  4. |yItem Quality: |Y{item.traits.qual.current}|n"
    text += f"\n  5. |yItem Condition: |Y{item.traits.cond.current}|n"
    text += f"\n  6. |yItem Capacity (in kilgrams): |Y{item.traits.cap.current}|n"
    if item.traits.comfort:
        text += f"\n  7. |yComfort: |Y{item.traits.comfort.current}|n"
    if item.traits.light:
        text += f"\n  8. |yItem Light Intensity: |Y{item.traits.light.current}|n"
    if item.traits.charge:
        text += f"\n  9. |yNumber of Charges: |Y{item.traits.charge.current}|n"
    text += "\n  Type |y@|n to return to the main menu."
    return text

def nomatch_traits(menu, caller, item, string):
    """
    The user types in something.

    """
    cmd_str = string[3:]
    if len(string) > 2:
        if string[:1] == '1':
            item.traits.val.base = int(cmd_str)
            caller.msg(f"Set Value to: {item.traits.val.current}")
        elif string[:1] == '2':
            item.traits.mass.base = float(cmd_str)
            caller.msg(f"Set Mass to: {item.traits.mass.current}")
        elif string[:1] == '3':
            item.traits.hp.base = int(cmd_str)
            caller.msg(f"Set HPs to: {item.traits.hp.current}")
        elif string[:1] == '4':
            if 0 <= float(cmd_str) <= 1:
                item.traits.qual.base = float(cmd_str)
                caller.msg(f"Set Quality to: {item.traits.qual.current}")
            else:
                caller.msg("Choose a value between 0 and 1")
        elif string[:1] == '5':
            if 0 <= float(cmd_str) <= 1:
                item.traits.cond.base = float(cmd_str)
                caller.msg(f"Set Condition to: {item.traits.cond.current}")
            else:
                caller.msg("Choose a value between 0 and 1")
        elif string[:1] == '6':
            item.traits.cap.base = float(cmd_str)
            caller.msg(f"Set Capacity to: {item.traits.cap.current}")
        elif string[:1] == '7':
            if 0 <= float(cmd_str) <= 1:
                item.traits.comfort.base = float(cmd_str)
                caller.msg(f"Set Comfort to: {item.traits.comfort.current}")
            else:
                caller.msg("Choose a value between 0 and 1")
        elif string[:1] == '8':
            if 0 <= float(cmd_str) <= 1:
                item.traits.light.base = float(cmd_str)
                caller.msg(f"Set Light Intensity to: {item.traits.light.current}")
            else:
                caller.msg("Choose a value between 0 and 1")
        elif string[:1] == '9':
            item.traits.charge.base = int(cmd_str)
            caller.msg(f"Set # of Charges to: {item.traits.charge.current}")

        else:
            caller.msg("Unknown Command")
            return False
    return
