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
from typeclasses.items import Equippable
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

        if not self.obj.db.eq_slots:
            raise EquipException('`EquipHandler` requires `db.eq_slots` attribute on `{}`.'.format(obj))

        if len(self.obj.contents) > 0:
            self.slots = [slot for body_part in eq_slots for slot in self.obj.db.eq_slots[body_part].items()]
            self.slot_names = [slot for body_part in eq_slots for slot in self.obj.db.eq_slots[body_part].keys()]
            self.empty_slots = [slot[0] for body_part in eq_slots for slot in self.obj.db.eq_slots[body_part].items() if slot[1] == None]
            self.full_slots = [slot[0] for body_part in eq_slots for slot in self.obj.db.eq_slots[body_part].items() if slot[1] != None]
            self.eq = [slot[1] for body_part in eq_slots for slot in self.obj.db.eq_slots[body_part].items() if slot[1] != None]

        else:
            self.body_parts = {}


    def _set(self, body_part, slot, item):
        "Set a slot's contents on a body part"
        # allows None values to pass all checks
        if item is not None:
            # confirm the item is equippable
            if not item.is_typeclass(Equippable, exact=False):
                raise EquipException("Item is not equippable.")
            # confirm the requested slot is valid
            if slot not in self.slots:
                raise EquipException("Slot not available: {}".format(slot))
        # We'll equip the item to the body part and then update the character
        body_part.db.slots[slot] = item
        self.obj.eq_slots_status_update()


    def get(self, slot):
        """Return the item in the named slot."""
        if slot in self.slots:
            return self.slots[slot]
        else:
            return None


    def __len__(self):
        """Returns the number of equipped objects."""
        return len(self.full_slots)


    def __str__(self):
        """Shows the Equipment"""
        return str(self.eq)


    def __iter__(self):
        """Iterate over the equipment in an ordered way."""
        if not self.obj.db.eq_slots:
            return
        for slot in self.slots:
                yield slot, self.get(slot)


    @property
    def slots(self):
        """Returns a list of all equipment slots."""
        return self.slots


    @property
    def empty_slots(self):
        """Returns a list of empty slots."""
        return self.empty_slots


    def add(self, item):
        """Add an object to character's equip.
        Args:
            item (Equippable): the item to be equipped
        """
        if len(self.empty_slots) < 1:
            return False
        if len(self.empty_slots) < len(item.db.slots):
            return False
        for slot in self.empty_slots:
            for item_slot in item.db.slots:
                if slot == item_slot:
                    # now we have to iterate through the body parts and equip
                    # to the right slot on the right body part
                    for body_part in self.obj.db.limbs:
                        for slot_name, eq in body_part.db.eq_slots.items():
                            if eq != None and slot_name == item_slot:
                                # try to ensure we scrub the empty slot list of this slot
                                self.empty_slots.pop(slot)
                                # equip the item
                                self._set(body_part, slot, item)
        return True

    def remove(self,item):
        """Remove an object from character's equip.
        Args:
            item (Equippable): the item to be un-equipped
        """
        removed = False
        for item_slot in item.db.slots:
            for body_part in self.obj.db.limbs:
                for slot_name, eq in body_part.db.eq_slots.items():
                    if slot_name == item_slot:
                        self._set(body_part, slot, None)
                        self.empty_slots.append(slot_name)
                        removed = True
        return removed
