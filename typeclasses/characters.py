"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter


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
        return TraitHandler(self)

    @lazy_property
    def body_parts(self):
        """Handler for parts of the body. For a normal human, this would be
        head, torso, right arm, left arm, right leg, left leg. Note that
        equipment is associated with individual parts of the body."""
        return BodyPartHandler(self)

    @lazy_property
    def equipment(self):
        """Handler for equipped items. We may need to move this to the
        individual body part objects or keep it both here and there. TBD"""
        return EquipHandler(self)

    def at_object_creation(self):
        "Called only at object creation and with update command."
        # clear traits, ability_scores, talents, and mutations
        self.traits.clear()
        self.mutations.clear()
        self.talents.clear()
        self.status_effects.clear()
        self.body_parts.clear()
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
        ## mass will need to be rerolled after gender is chosen
        self.traits.add(key="mass", name="Mass", type='static', \
                        base=rarsc(180, dist_shape='very flat'), \
                        extra={'learn' : 0})
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=(self.traits.Str.current * .5), \
                        extra={'learn' : 0})

        ## generate initial component parts of the body
        self.body_parts.add(key='head', name='Head', type='head')
        self.body_parts.add(key='tor', name='Torso', type='torso')
        self.body_parts.add(key='rarm', name='Right Arm', type='arm')
        self.body_parts.add(key='larm', name='Left Arm', type='arm')
        self.body_parts.add(key='rleg', name='Right Leg', type='leg')
        self.body_parts.add(key='lleg', name='Left Leg', type='leg')

        ## info dictionary to contain player preferences. These can be changed
        ## via player commands
        self.db.info = {'Target': None, 'Mercy': True, 'Default Attack': \
            'unarmed_strike', 'Sneaking' : False, 'Wimpy': 150, 'Yield': 250}

        return TraitHandler(self)
