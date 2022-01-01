# coding=utf-8
"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from evennia.utils import lazy_property
from evennia import utils as utils
from world.handlers.equipment import EquipHandler
from world.handlers.traits import TraitHandler
from world.randomness_controller import distro_return_a_roll as roll
from world.randomness_controller import distro_return_a_roll_sans_crits as rarsc
from world.handlers import talents, mutations, body_parts#, status_effects
from evennia.utils.logger import log_file
from evennia import gametime
from evennia import create_script
from evennia.utils import evform, evtable


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    # pull in handlers for traits, equipment, mutations, talents
    @lazy_property
    def traits(self):
        """TraitHandler that manages room traits."""
        return TraitHandler(self)

    @lazy_property
    def mutations(self):
        """TraitHandler that manages room mutations. We may need to move this to
        the individual body part objects or keep it both here and there. TBD"""
        # note: These will be used rarely for rooms
        return TraitHandler(self, db_attribute='mutations')

    @lazy_property
    def talents(self):
        """TraitHandler that manages room talents."""
        # note: These will be used rarely for rooms
        return TraitHandler(self, db_attribute='talents')

    @lazy_property
    def status_effects(self):
        """TraitHandler that manages room status effects."""
        return TraitHandler(self, db_attribute='status_effects')

    @lazy_property
    def equipment(self):
        """Handler for equipped items. We may need to move this to the
        individual body part objects or keep it both here and there. TBD"""
        return EquipHandler(self)

    def at_object_creation(self):
        "Called only at object creation and with update command."
        # clear traits and trait-like containers
        self.traits.clear()
        self.mutations.clear()
        self.talents.clear()
        #self.status_effects.clear()
        ## Define initial attribute score traits and the secondary traits that
        ## are calculated from the primary attributes

        ## PRIMARY attribute scores
        self.traits.add(key='Dex', name='Dexterity', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.traits.add(key='Str', name='Strength', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.traits.add(key='Vit', name='Vitality', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.traits.add(key='Per', name='Perception', type='static', \
                        base=rarsc(100), extra={'learn' : 0})
        self.traits.add(key='FOP', name='Force of Personality', type='static', \
                        base=rarsc(100), extra={'learn' : 0})

        ## SECONDARY attribute scores
        self.traits.add(key="hp", name="Health Points", type="gauge", \
                        base=((self.traits.Vit.current * 5) + \
                        (self.traits.FOP.current * 2)), extra={'learn' : 0})
        self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                        base=((self.traits.Vit.current * 3) + \
                        (self.traits.Str.current * 2)+ \
                        (self.traits.Dex.current)), extra={'learn' : 0})
        self.traits.add(key="cp", name="Conviction Points", type="gauge", \
                        base=((self.traits.FOP.current * 5) + \
                        (self.traits.Vit.current)), extra={'learn' : 0})
        ## mass and height will need to be rerolled after gender is chosen
        # height is in cm. Weight is in kilograms
        self.traits.add(key="mass", name="Mass", type='static', \
                        base=rarsc(75, dist_shape='normal'), \
                        extra={'learn' : 0})
        self.traits.add(key="height", name="Height", type='static', \
                        base=rarsc(170, dist_shape='normal'), \
                        extra={'learn' : 0})
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=(self.traits.Str.current * .5), \
                        extra={'learn' : 0})

        ## generate initial component parts of the body
        if len(self.contents) == 0:
            body_parts.initialize_body_parts(self)
        ## add list of empty eq slots to character db
        self.eq_slots_status_update()


        # money
        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 0}

        ## info dictionary to contain player preferences. These can be changed
        ## via player commands
        self.db.info = {'target': None, 'mercy': True, 'default attack': \
            'unarmed_strike', 'sneaking' : False, 'wimpy': 150, 'yield': 250}

        # apply the initial mutations and talents. Most talents will be set
        # to zero. Many mutations will only be added if the character gains
        # that mutation
        talents.apply_talents(self)
        mutations.initialize_mutations(self)

    def eq_slots_status_update(self):
        """
        This function pulls all of the equipment slots from the individual
        body parts of the character. This function should be run before doing
        anything with the Equipment Handler found in world.handlers.equipment
        """
        self.db.eq_slots = {}
        self.db.limbs = []

        for item in self.contents:
            if utils.inherits_from(item, 'world.handlers.body_parts.BodyPart'):
                self.db.limbs.append(item)

        if len(self.db.limbs) > 0:
            for part in self.db.limbs:
                self.db.eq_slots[part.name] = part.db.slots

        else:
            log_file("List of Body Parts is Empty.", filename="error.log")


    def at_before_move(self, destination):
        "Called just before trying to move"
        if self.ndb.cantmove: # replace with condition you want to test
            return False
        return True
