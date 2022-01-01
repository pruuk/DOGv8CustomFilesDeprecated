# coding=utf-8
"""
Armor typeclasses

These are the subclasses of equippable items intended to protect from damage
from attacks by other beings.

The code is mostly copied from:
https://github.com/evennia/ainneve/blob/master/typeclasses/armors.py

"""
from typeclasses.items import Equippable
from world.handlers.traits import TraitHandler

class Armor(Equippable):
    """
    Typeclass for armor objects.
    Attributes:
        physical_armor_value (int): primary defensive stat for physical hits
        mental_armor_value (int): primary defensive stat for mental hits

    """
    slots = [] # slot will need to be added at object creation
    mass = 3

    def at_object_creation(self):
        super(Armor, self).at_object_creation()
        # Please note that armor mitigation is a multiplier. A base value of 1
        # provides NO PROTECTION. A Value of 1.1 provides 10% mitigation of
        # damage unless the hit is a critical strike
        self.traits.add(key='pamm', name='Physical Armor Mitigation Multiplier', \
                        type='static', base=1, extra={'learn' : 0})
        self.traits.add(key='samm', name='Stamina Armor Mitigation Multiplier', \
                        type='static', base=1, extra={'learn' : 0})
        self.traits.add(key='mamm', name='Mental Armor Mitigation Multiplier', \
                        type='static', base=1, extra={'learn' : 0})
        self.traits.add(key="hp", name="Health Points", type="gauge", \
                        base=10, extra={'learn' : 0})
        self.traits.add(key="mass", name="Mass", type='static', \
                        base=1, extra={'learn' : 0})
        # encumberance is a measure of how much the item can hold. This will
        # obviously be higher for items like backbacks and quivers than for
        # something like a helmet
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=1, \
                        extra={'learn' : 0})


    def at_equip(self, character):
        pass

    def at_remove(self, character):
        pass

class Shield(Armor):
    """Typeclass for shield prototypes."""
    slots = ['hand'] # note that some shields may be multi-slot
    multi_slot = False
    mass = 8


class Hat(Armor):
    "subtype to be worn on head"
    slots = ['head']
    multi_slot = False


class Helmet(Armor):
    "subtype to be worn on head, close-faced"
    slots = ['head', 'face', 'ears', 'nose', 'mouth']
    multi_slot = True
    mass = 5


class Mask(Armor):
    "subtype to be worn on face"
    slots = ['face']
    multi_slot = False


class Earrings(Armor):
    "subtype to be worn on ears"
    slots = ['ear']
    multi_slot = False


class Neck(Armor):
    """subtype to be worn on neck. Includes necklaces, torques, etc."""
    slots = ['neck']
    multi_slot = False


class Vest(Armor):
    """subtype to be worn on chest."""
    slots = ['chest']
    multi_slot = False
    mass = 5


class Chestplate(Armor):
    """subtype to be worn on chest, shoulders, and arms. Lighter armor"""
    slots = ['chest', 'back', 'shoulders']
    multi_slot = True
    mass = 10


class Robes(Armor):
    """ Subtype to cover most of body, but not the head"""
    slots = ['chest', 'back', 'shoulders', 'waist', 'upper_arms', \
             'thighs']
    multi_slot = True
    mass = 3


class FullBodyArmor(Armor):
    """subtype that is a full suit of armor. Usually heavy armor"""
    slots = ['head', 'face', 'ears', 'neck', 'chest', 'waist', 'shoulders', \
             'upper_arms', 'forearms', 'hands', 'thighs', 'lower_legs', 'feet']
    multi_slot = True
    mass = 35


class Back(Armor):
    "subtype to be worn on back. Includes capes, backpacks, and cloaks"
    slots = ['back']
    multi_slot = False


class Quiver(Armor):
    """subtype to be worn as quiver to hold ammo"""
    slots = ['quiver']
    multi_slot = False
    mass = 2


class Belt(Armor):
    """subtype to be worn around the waist."""
    slots = ['waist']
    multi_slot = False
    mass = 2


class Glove(Armor):
    """subtype to be worn on hands."""
    slots = ['hands']
    multi_slot = False
    mass = 1


class Gauntlets(Armor):
    """subtype to be worn on hands. prevents wearing rings"""
    slots = ['hands', 'fingers']
    multi_slot = True
    mass = 3


class Ring(Armor):
    """subtype to be worn on fingers."""
    slots = ['fingers']
    multi_slot = False


class Legs(Armor):
    """subtype to be worn on legs. Includes pants."""
    slots = ['thighs', 'lower_legs']
    multi_slot = True
    mass = 3


class Feet(Armor):
    """subtype to be worn on feet. Includes boots, shoes, etc"""
    slots = ['feet', 'toes'] # might just be feet if these are open-toed sandals
    multi_slot = True
    mass = 2


class Greaves(Armor):
    """subtype to be worn on legs and feet."""
    slots = ['lower_legs', 'feet', 'toes']
    multi_slot = True
    mass = 5
