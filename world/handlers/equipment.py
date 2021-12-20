# -*- coding: UTF-8 -*-
"""
This file is inspired by the Ainneve mud code at:
https://github.com/evennia/ainneve/blob/master/world/equip.py
and then modified to fit Delusion of Grandeur's twitch style combat.

Equipment handler module.

Config Properties:
    TODO

Setup:
    To use the EquipHandler, add it to a character typeclass as follows:
    ```python
    from world.equip import EquipHandler
      ...
    @property
    def equip(self):
        return EquipHandler(self)
    ```
Use:
    Equippable items are equipped and unequipped using the `add` and `remove`
    methods, respectively.
    The EquipHandler can be iterated over to access the contents of its slots
    in an ordered fashion. It also supports `obj in character.equip` syntax
    to check whether an item is equipped
"""
# from typeclasses.items import Equippable
from functools import reduce

class EquipException(Exception):
    """Base exception class for EquipHandler."""
    def __init__(self, msg):
        self.msg = msg

class EquipHandler(object):
    """Handler for a character's "equipped" items.
    Args:
        obj (character): character object
    Properties
        slots (tuple): returns a tuple of all slots in order
        empty_slots (list): returns a list of empty slots
    Note:
        Individual slots' items can be accessed as attributes
    Methods:
        add (Equippable): "equip" an item from the character's inventory.
        remove (Equippable): "un-equip" an item and move it to inventory.
    """
    def __init__(self, obj):
        # save the parent typeclass
        self.obj = obj
