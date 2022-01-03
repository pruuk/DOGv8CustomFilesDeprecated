# coding=utf-8
"""
Menus for editing item objects. Every item created with the make menu will
be dropped in the current room the builder is standing in.
"""
from evennia.contrib.building_menu import BuildingMenu
from evennia.utils import lazy_property
from world.handlers.traits import TraitHandler
from evennia.utils.logger import log_file

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
        self.room = room
        self.add_choice_edit("|=zFlavor Item|n", "2", glance = """
        Flavor items are ordinary objects that add flavor to the room, but
        are not normally intended to be equipped by players or NPCs. For
        example, a road object, a rock, a column, a chair. These items can
        be used (poorly) as improvised weapons if the wielder is strong
        enough, but they will be poor weapons.""", text=text_flavitem,
        onnomatch=nomatch_flavitem)


# Menu functions
def text_flavitem(caller, room):
    """Show the room exits in the choice itself."""
    text = "-" * 79

    return text


def nomatch_flavitem(menu, caller, room, string):
    """
    The user types something into the submenu for flavor objects
    """

    return


        # self.add_choice("|=zTitle|n", key="1", attr="key", glance="|y{obj.key}|n", text="""
        #         -------------------------------------------------------------------------------
        #         Editing the title of {{obj.key}}(#{{obj.id}})
        #
        #         You can change the title simply by entering it.
        #         Use |y{back}|n to go back to the main menu.
        #
        #         Current title: |c{{obj.key}}|n
        # """.format(back="|n or |y".join(self.keys_go_back)))
        # self.add_choice_edit("|=zDescription|n", "2")
        # self.add_choice("|=zExits|n", "3", glance=glance_exits, text=text_exits,
        #     on_nomatch=nomatch_exits)
        # self.add_choice("|=zInfo Attributes|n", "4", glance=glance_info_attrs,
        #     text=text_info, on_nomatch=nomatch_info)
        # self.add_choice("|=zTraits|n", "5", glance=glance_traits,
        #     text=text_traits, on_nomatch=nomatch_traits)
        # self.add_choice("|=zBiomes|n", "6", glance=glance_biomes,
        #     text=text_biomes, on_nomatch=nomatch_biomes)
        # self.add_choice("|=zChoose Map Symbol (from a list)|n", "7",
        #     glance="\n  {obj.db.map_symbol}",
        #     text=text_map_symbol, on_nomatch=nomatch_map_symbol)
        # self.add_choice("|=zUpdate the Room to Current Spec|n", "8",
        #     glance=glance_update, on_enter=update_on_enter)
