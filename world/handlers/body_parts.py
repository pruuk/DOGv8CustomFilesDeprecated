# -*- coding: utf-8 -*-
"""
    Body Parts Module.

    This file will contain the necessary functions to instantiate the body
    parts of a creature or plant. These body parts will essentially serve
    as a container for associated equipment and for part specific mutations.

    On humanoid characters or NPC, if the health of the head or torso falls
    to zero, the whole character dies. If the stamina or health of any others
    part falls to zero, that part becomes unuseable until it recovers.

    Classes:
        'body_part': generalize body part object

    Sub-Classes:
        'head': The location of the mind of a creature
        'torso': The primary body of the creature
        'leg': An appendage that primarily serves the purpose of carrying the
               weight of the character/NPC and provides locomotion on land
        'arm': An appendage that can make use of tools and weapons
        'wings': A set of appendages that can enable flight if many other
                conditions are met
        'tentacle': An appendage that provides locomotion in water environments,
                can be used (somewhat poorly) for tool or weapon use, and often
                has teeth or suckers that enhance combat abilities
        'tail': An appendage that provides additional balance and can be used
                in combat. In some cases, a tail can have spikes or a club at
                the end.

    Module Functions:

        - initialize_body_parts(character)
            Initializes a set of body parts for a new character.

        - add_new_body_part(body_part, character)
            Adds a new instance of a body_part to a character object's set of
            body parts

"""
# imports
from world.randomness_controller import distro_return_a_roll as roll
from world.randomness_controller import distro_return_a_roll_sans_crits as rarsc
from evennia import DefaultObject
from evennia.utils import lazy_property
from world.handlers.equipment import EquipHandler
from world.handlers.traits import TraitHandler
from world.handlers import mutations #, status_effects
from evennia import create_object
from evennia import utils as utils

class BPException(Exception):
    def __init__(self, msg):
        self.msg = msg

# classes for body part objects
class BodyPart(DefaultObject):
    """
    Base class for any body parts. This class should not be used.
    Please use an appropriate subclass.
    """

    @lazy_property
    def traits(self):
        """TraitHandler that manages character traits."""
        return TraitHandler(self)

    @lazy_property
    def mutations(self):
        """TraitHandler that manages character mutations."""
        return TraitHandler(self, db_attribute='mutations')

    @lazy_property
    def equip(self):
        """Handler for equipped items."""
        return EquipHandler(self)

    @lazy_property
    def status_effects(self):
        """TraitHandler that manages room status effects."""
        return TraitHandler(self, db_attribute='status_effects')

    def at_object_creation(self):
        "Called only at object creation and with update command."
        # size is relative to normal for the given creature's baseline of 100
        # 150 is 1.5 times normal size in proportion to the overall body size
        self.traits.add(key="size", name='Size', type='static', base=100)
        self.db.type = 'undefined'


class Head(BodyPart):
    """
    Subclass for a head on a character or NPC's body
    """

    def at_object_creation(self):
        "Called only at object creation and with update command."
        self.traits.add(key="size", name='Size', type='static', base=100)
        self.db.type = 'head'
        self.db.allowable_eq_slots = ['head', 'face', 'right_ear', 'left_ear',
                                      'right_eye', 'left_eye', 'nose', 'mouth',
                                      'neck']
        self.db.slots = {
            'head': None,
            'face': None,
            'right_ear': None,
            'left_ear': None,
            'right_eye': None,
            'left_eye': None,
            'nose': None,
            'mouth': None,
            'neck': None
        }

    def at_after_move(self):
        """
        Called after a move of the object has been completed.
        """
        if utils.inherits_from(self.location, 'typeclases.characters.Character'):
            character = self.location
            self.traits.add(key="hp", name="Health Points", type="gauge", \
                            base=character.traits.hp.current * .1, extra={'learn' : 0})
            self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                            base=character.traits.sp.current * .1, extra={'learn' : 0})


class Torso(BodyPart):
    """
    Subclass for a torso on a character or NPC's body
    """

    def at_object_creation(self):
        "Called only at object creation and with update command."
        self.traits.add(key="size", name='Size', type='static', base=100)
        self.db.type = 'torso'
        self.db.allowable_eq_slots = ['chest', 'back', 'waist', 'quiver']
        self.db.slots = {
            'chest': None,
            'back': None,
            'waist': None,
            'quiver': None
        }

    def at_after_move(self):
        """
        Called after a move of the object has been completed.
        """
        if utils.inherits_from(self.location, 'typeclases.characters.Character'):
            character = self.location
            self.traits.add(key="hp", name="Health Points", type="gauge", \
                            base=character.traits.hp.current * .4, extra={'learn' : 0})
            self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                            base=character.traits.sp.current * .4, extra={'learn' : 0})


class Leg(BodyPart):
    """
    Subclass for a leg on a character or NPC's body
    """

    def at_object_creation(self):
        "Called only at object creation and with update command."
        self.traits.add(key="size", name='Size', type='static', base=100)
        self.db.type = 'leg'
        self.db.allowable_eq_slots = ['thigh', 'lower_leg', 'foot', 'toes',
                                      'hoof']
        self.db.slots = {
            'thigh': None,
            'lower_leg': None,
            'foot': None,
            'toes': None
        }

    def at_after_move(self):
        """
        Called after a move of the object has been completed.
        """
        if utils.inherits_from(self.location, 'typeclases.characters.Character'):
            character = self.location
            self.traits.add(key="hp", name="Health Points", type="gauge", \
                            base=character.traits.hp.current * .15, extra={'learn' : 0})
            self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                            base=character.traits.sp.current * .15, extra={'learn' : 0})


class Arm(BodyPart):
    """
    Subclass for a arm on a character or NPC's body
    """

    def at_object_creation(self):
        "Called only at object creation and with update command."
        self.traits.add(key="size", name='Size', type='static', base=100)
        self.db.type = 'arm'
        self.db.allowable_eq_slots = ['shoulder', 'upper_arm', 'forearm',
                                      'hands', 'fingers']
        self.db.slots = {
            'shoulder': None,
            'upper_arm': None,
            'forearm': None,
            'hands': None,
            'fingers': None
        }

    def at_after_move(self):
        """
        Called after a move of the object has been completed.
        """
        if utils.inherits_from(self.location, 'typeclases.characters.Character'):
            character = self.location
            self.traits.add(key="hp", name="Health Points", type="gauge", \
                            base=character.traits.hp.current * .1, extra={'learn' : 0})
            self.traits.add(key="sp", name="Stamina Points", type="gauge", \
                            base=character.traits.sp.current * .1, extra={'learn' : 0})

# TODO: Add body part classes for the non-standard types
# TODO: Add function to add new body parts (due to mutation)

## Functions
# initialize a new humanoid character
def initialize_body_parts(character):
    """
    Load new character with their body part Objects
    """
    # Create body part objects
    head = create_object("world.handlers.body_parts.Head", key='head')
    torso = create_object("world.handlers.body_parts.Torso", key='torso')
    right_arm = create_object("world.handlers.body_parts.Arm", key='right_arm')
    left_arm = create_object("world.handlers.body_parts.Arm", key='left_arm')
    right_leg = create_object("world.handlers.body_parts.Leg", key='right_leg')
    left_leg = create_object("world.handlers.body_parts.Leg", key='left_leg')

    # Add objects to character
    head.move_to(character)
    torso.move_to(character)
    right_arm.move_to(character)
    left_arm.move_to(character)
    right_leg.move_to(character)
    left_leg.move_to(character)
