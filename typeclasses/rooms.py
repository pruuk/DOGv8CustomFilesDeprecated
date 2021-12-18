"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """

    # pull in handlers for traits, equipment, mutations, talents
    @lazy_property
    def traits(self):
        """TraitHandler that manages room traits."""
        return TraitHandler(self)

    @lazy_property
    def mutations(self):
        """TraitHandler that manages room mutations."""
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
        return TraitHandler(self)
