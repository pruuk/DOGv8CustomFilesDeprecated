# -*- coding: utf-8 -*-
"""
Mutations module.
This module is modeled after the skills module for the Ainneve mud based upon
Evennia. I've borrowed heavily from the code and style at:
https://github.com/evennia/ainneve/blob/master/world/skills.py
This module contains the data and functions related to object Mutations.

Please see:
https://docs.google.com/document/d/1YoCURidXUJab1nQy1L5_66MF5n8D1QwQlojroV4XuGw/edit
and:
https://docs.google.com/document/d/1ATy_q5RCEiCPj043pZbpJKFWbaruv5Vb2iP8yKWGv1c/edit
for more information about the world of DOG and the plan for implementing the
first sets of mutations and talents.
Classes:
    'mutation': convenience object for mutation display data
Module Functions:
    - initialize_mutations(character, body_part)
        Initializes a character's or NPC's starting mutations. These are limited
        in number and mostly represent the types of mutations measured around
        the base of 100 (human normal). If body_part is 'full', the mutation
        is stored on the character object
    - 'load_mutation(mutation)'
        Loads an instance of the Skill class by name for display of skill name
        and description.
    - 'add_new_mutation(character, body_part)'
        Adds a newly developed mutation to a character or body part of a
        character. If body_part is 'full', the mutation is stored on the
        character object.
"""
# imports
from world.randomness_controller import distro_return_a_roll as roll
from world.randomness_controller import distro_return_a_roll_sans_crits as rarsc
from evennia.utils import logger, lazy_property


class MutationException(Exception):
    def __init__(self, msg):
        self.msg = msg

# Dictionary of Possible Mutations
_MUTATION_DATA = {
    # WHOLE BODY MUTATIONS
    'extreme_flexibility': {
        'name': 'Extreme Flexibility',
        'base': 'Dex',
        'body_part': ['all'],
        'desc': ("|mExtreme Flexibility|n is a mutation that improves the "
                 "ability to dodge and block in combat, reduces damage from "
                 "some grappling attacks, and allows the character to fit in "
                 "tight locations. This is a prerequisite to the rubber body "
                 "power."),
        'prerequisites': None,
        'starting_score': 'Dex',
        'extra': {'learn' : 0, 'min': 25, 'max': 500}
    },
    'rubber_body': {
        'name': 'Rubber Body',
        'base': 'Dex',
        'body_part': ['all'],
        'desc': ("|mRubber Body|n is a mutation that makes the body soft and "
                 "extremely flexible. Characters with this mutation are "
                 "resistant to bludgeoning damage and some grappling attacks. "
                 "Rubber body allows the character to fit in tight locations "
                 "and in some cases  "
                 "power."),
        'prerequisites': {'mutations.extreme_flexibility.actual': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'bone_density': {
        'name': 'Bone Density',
        'base': 'Str',
        'body_part': ['all'],
        'desc': ("|mBone Density|n is a measure of the density of the "
                 "density of the character's bones. This mutation can raise or "
                 "lower the density of the character's bones, which can affect "
                 "a number of other mutations, the maximum Strength of the "
                 "character, the mass of the character, how expensive (in "
                 "Stamina cost) it is to move between rooms. The minimum for"
                 "this score is 25 and the maximum is 1000. 100 is human normal."),
        'prerequisites': None,
        'starting_score': 'Str',
        'extra': {'learn' : 0, 'min': 25, 'max': 1000}
    },
    'increased_regeneration': {
        'name': 'Increased Regeneration',
        'base': 'Vit',
        'body_part': ['all'],
        'desc': ("|mIncreased Regeneration|n is a mutation that increases the "
                 "rate that a character heals health and stamina."),
        'prerequisites': None,
        'starting_score': 'Vit',
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'extra_limbs': {
        'name': 'Extra Limbs',
        'base': 'Vit',
        'body_part': ['all'],
        'desc': ("|mExtra Limbs|n is a mutation that increases the number of "
                 "limbs that a character has. The extra limbs can be extra arms,"
                 "tail, legs, wings, tentacles, etc. "),
        'prerequisites': {'mutations.regrow_limbs.actual': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 600}
    },
     'chromatic_flesh': {
        'name': 'Chromatic Flesh',
        'base': 'Per',
        'body_part': ['all'],
        'desc': ("|mChromatic Flesh|n is a mutation that gives the character "
                 "the ability to alter the surface apperance of their flesh. "
                 "This mutation unlocks talents like natural camo."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'malleable_flesh': {
        'name': 'Malleable Flesh',
        'base': 'Cha',
        'body_part': ['all'],
        'desc': ("|mMalleable Flesh|n is a mutation that gives the character "
                 "the ability to alter the shape and texture of their own"
                 "flesh with the force of their will. This mutation unlocks"
                 "certain talents such as disguise and aids natural camo."),
        'prerequisites': {'mutations.rubber_body.actual': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    # MULTIPLE PART MUTATIONS
    'regrow_limbs': {
        'name': 'Regrow Limbs',
        'base': 'Vit',
        'body_part': ['arm', 'leg'],
        'desc': ("|mRegrow Limbs|n is a mutation that allows the character to "
                 "heal egregious wounds, such as losing a limb."),
        'prerequisites': {'mutations.increased_regeneration.actual': 300},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'armored_hide': {
        'name': 'Armored Hide',
        'base': 'Vit',
        'body_part': ['arm', 'leg', 'torso', 'head'],
        'desc': ("|mArmored Hide|n is a mutation that allows a character to grow "
                 "armored hide, scales, or plates which mitigate damage from "
                 "many types of damage. This mutation changes the appearance "
                 "of the character and increases their mass."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 300}
    },
    'bladed_body': {
        'name': 'Bladed Body Ridges',
        'base': 'Vit',
        'body_part': ['arm', 'leg', 'torso', 'head'],
        'desc': ("|mBladed Body Ridges|n is a mutation that allows a character "
                 "to grow sharp body ridges which can do damage to attackers or "
                 "cause many grappling attacks to do damage."),
        'prerequisites': {'mutations.armored_hide': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 300}
    },
    'sharp_claws': {
        'name': 'Sharp Claws',
        'base': 'Vit',
        'body_part': ['arm', 'leg'],
        'desc': ("|mSharp Claws|n is a mutation that allows a character to grow "
                 "sharp claws on their hands and feet, which can increase the "
                 "damage of unarmed strikes, but make equipping shoes and gloves "
                 "difficult unless the equipment is custom crafted."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'long_limbs': {
        'name': 'Long Limbs',
        'base': 'Vit',
        'body_part': ['arm', 'leg'],
        'desc': ("|mLong Limbs|n is a mutation that allows a character to grow "
                 "longer limbs. It can make using non-custom armor and clothing"
                 "difficult in some cases."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 300}
    },
    'short_limbs': {
        'name': 'Short Limbs',
        'base': 'Vit',
        'body_part': ['arm', 'leg'],
        'desc': ("|mShort Limbs|n is a mutation that allows a character to grow "
                 "shorter limbs. It can make using non-custom armor and clothing"
                 "difficult in some cases."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 200}
    },
    'sharp_teeth': {
        'name': 'Sharp Claws',
        'base': 'Vit',
        'body_part': ['head', 'arms'],
        'desc': ("|mSharp Teeth|n is a mutation that allows a character to grow "
                 "sharp teeth in their mouth or on tentacles, which can increase the "
                 "damage of unarmed strikes, but make equipping some face items "
                 "or armor difficult unless the equipment is custom crafted."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    # HEAD MUTATIONS
    'visual_sensitivity': {
        'name': 'Visual Sensitivity',
        'base': 'Per',
        'body_part': ['head'],
        'desc': ("|mVisual Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of vision. At high enough levels "
                 "the character wil gain access to low light vision, infrared "
                 "vision, and x-ray vision. This mutation comes at the cost of "
                 "being vulnerable to certain attack types involving energy."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'sonic_sensitivity': {
        'name': 'Sonic Sensitivity',
        'base': 'Per',
        'body_part': ['head'],
        'desc': ("|mSonic Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of hearing. At high enough levels "
                 "the character can develop talents like echo location, sonic "
                 "attacks, etc. This mutation comes at the cost of being "
                 "vulnerable to certain attack types involving sound."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'tactile_sensitivity': {
        'name': 'Tactile Sensitivity',
        'base': 'Per',
        'body_part': ['head'],
        'desc': ("|mTactile Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of touch. This mutation comes "
                 "at the cost of being vulnerable to certain attack types."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
     'olefactory_sensitivity': {
        'name': 'Olefactory Sensitivity',
        'base': 'Per',
        'body_part': ['head'],
        'desc': ("|mOlefactory Sensitivity|n is a mutation that gives the character "
                 "a unnaturally sensitive sense of taste and smell. This "
                 "mutation comes at the cost of being vulnerable to certain "
                 "attack types."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'magnetic_sensitivity': {
        'name': 'Magnetic Sensitivty',
        'base': 'Per',
        'body_part': ['head'],
        'desc': ("|mMagnetic Sensitivty|n is a mutation that gives the character "
                 "the ability to sense magnetic fields. Characters with this"
                 "power rarely get lost."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'extrasensory_perception': {
        'name': 'Extrasensory Perception',
        'base': 'Per',
        'body_part': ['head'],
        'desc': ("|mExtrasensory Perception|n is a mutation that gives the "
                 "character the ability to perceive outside the normal set of "
                 "senses. It is related to psychokinesis and pychoprojection "
                 "in that all three of these mutations are psionic type powers. "
                 "This mutation unlocks a number of talents, but comes at the "
                 "cost of making the character more vulnerable to certain "
                 "environments and attack types."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'psychokinesis': {
        'name': 'Psychokinesis',
        'base': 'Cha',
        'body_part': ['head'],
        'desc': ("|mPsychokinesis|n is a mutation that gives the character "
                 "the ability to interact with physical systems with their will. "
                 "At higher levels, they can attack by throwing small objects, "
                 "unlock doors, or even fly (if their mass is low enough). "
                 "This mutation unlocks a number of talents."),
        'prerequisites': {'mutations.extrasensory_perception': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 1000}
    },
    'psychoprojection': {
        'name': 'Psychoprojection',
        'base': 'Cha',
        'body_part': ['head'],
        'desc': ("|mPsychoprojection|n is a mutation that gives the character "
                 "the ability to interact with non-physical systems with their "
                 "will. At higher levels, they can unlock a number of talents, "
                 "such as astral projection, atomic phasing, invisibility, etc."),
        'prerequisites': {'mutations.extrasensory_perception': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 1000}
    },
    # TORSO MUTATIONS
    'gut_biome': {
        'name': 'Interesting Gut Biome',
        'base': 'Vit',
        'body_part': ['torso'],
        'desc': ("|mInteresting Gut Biome|n is a mutation that allows a "
                 "character's to eat many things a normal character couldn't. "
                 "At advanced levels, some characters may be able to control "
                 "their gut biome well enough to synthesize compounds within "
                 "their own gut."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'poison_bite': {
        'name': 'Poison Bite',
        'base': 'Vit',
        'body_part': ['torso'],
        'desc': ("|mPoison Bite|n is a mutation that allows a character to"
                 "inflict a poisonous or bacterially damaging bite upon a "
                 "victim. Please note that effective use of this mutation "
                 "requires using a combat talent that involves biting."),
        'prerequisites': {'mutations.gut_biome': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'poison_spit': {
        'name': 'Poison Spit',
        'base': 'Vit',
        'body_part': ['torso'],
        'desc': ("|mPoison Spit|n is a mutation that allows a character to"
                 "inflict a poisonous or bacterially damaging extrad attack "
                 "upon a victim. Please note that effective use of this mutation "
                 "requires using a combat talent that involves spitting."),
        'prerequisites': {'mutations.poison_bite': 200},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'sticky_spit': {
        'name': 'Sticky Spit',
        'base': 'Vit',
        'body_part': ['torso'],
        'desc': ("|mSticky Spit|n is a mutation that allows a character to"
                 "produce very sticky spit that can be used an a debilitating "
                 "attack or as an adhesive. Please note that effective use of "
                 "this mutation requires using a combat talent that involves "
                 "spitting."),
        'prerequisites': {'mutations.gut_biome': 300},
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    'gills': {
        'name': 'Gills',
        'base': 'Vit',
        'body_part': ['torso'],
        'desc': ("|mGills|n is a mutation that allows a character to breathe"
                 "underwater. It makes wearing certain body armors harder, "
                 "possibly requiring custom armor."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 500}
    },
    # LEG MUTATIONS
    'webbed_feet': {
        'name': 'Webbed Feet',
        'base': 'Vit',
        'body_part': ['legs'],
        'desc': ("|mWebbed Feet|n is a mutation that allows a character to grow"
                 "webbed feet. It makes wearing certain foot armors harder, "
                 "possibly requiring custom armor. Travel ubnderwater will be "
                 "easier for the character, but they will be slower on land."),
        'prerequisites': None,
        'starting_score': 0,
        'extra': {'learn' : 0, 'min': 0, 'max': 300}
    },
    # ARM MUTATIONS

}

# all mutations
ALL_MUTATIONS = {
  'extreme_flexibility', 'rubber_body',
  'bone_density', 'increased_regeneration',
  'regrow_limbs', 'extra_limbs', 'armored_hide',
  'bladed_body', 'sharp_claws', 'long_limbs', 'short_limbs', 'gut_biome',
  'poison_bite', 'poison_spit', 'sticky_spit',
  'gills', 'webbed_feet',
  'visual_sensitivity', 'sonic_sensitivity',
  'tactile_sensitivity', 'olefactory_sensitivity',
  'magnetic_sensitivity', 'chromatic_flesh',
  'extrasensory_perception', 'psychokinesis', 'psychoprojection',
  'malleable_flesh'
}
# mutations, grouped by body part
WHOLE_BODY_MUTATIONS = [m for m in ALL_MUTATIONS if 'all' in _MUTATION_DATA[m]['body_part']]
MULTIPLE_PART_MUTATIONS = [m for m in ALL_MUTATIONS if len(_MUTATION_DATA[m]['body_part']) > 1]
HEAD_MUTATIONS = [m for m in ALL_MUTATIONS if 'head' in _MUTATION_DATA[m]['body_part']]
TORSO_MUTATIONS = [m for m in ALL_MUTATIONS if 'torso' in _MUTATION_DATA[m]['body_part']]
ARM_MUTATIONS = [m for m in ALL_MUTATIONS if 'arm' in _MUTATION_DATA[m]['body_part']]
LEG_MUTATIONS = [m for m in ALL_MUTATIONS if 'leg' in _MUTATION_DATA[m]['body_part']]
# mutations, grouped by ability score
DEX_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Dex']
STR_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Str']
VIT_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Vit']
PER_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'Per']
FOP_MUTATIONS = [m for m in ALL_MUTATIONS if _MUTATION_DATA[m]['base'] == 'FOP']

# initialize character with starting mutations
def initialize_mutations(character):
    """
    Sets up a character or NPC's initial mutations. Many of these will start at 0
    and require prerequisites to be met, quests to be completed, and/or events
    to happen to or near the character or NPC to trigger the mutation that leads
    to the discovery of that mutation.
    Args:
        character (Character): the character being initialized
        list_of_body_parts (body_part, body_part, etc): Each body part on the character
    """
    # convert args to a list so we can loop through it

    for mutation, data in _MUTATION_DATA.items():
        if data['starting_score'] != 0:
            # initialize full body mutations first
            if data['body_part'] == 'all':
                if data['starting_score'] in ('Dex', 'Str', 'Vit', 'Per', 'Cha'):
                    character.mutations.add(
                        key=mutation,
                        type='static',
                        base=character.traits[data['base']].actual,
                        body_part=data['body_part'],
                        mod=0,
                        name=data['name'],
                        extra=data['extra']
                    )
                elif data['starting_score'] == {'rarsc': 100}:
                    character.mutations.add(
                        key=mutation,
                        type='static',
                        base=rarsc(100),
                        mod=0,
                        name=data['name'],
                        extra=data['extra']
                    )
                else:
                    logger.log_trace("Initialization of one of the full body mutations failed")
            else:
                logger.log_trace("Initialization of one of the mutations failed")


# function to load a mutation
def load_mutation(mutation):
    """
    Retrieves an instance of a 'mutation' class.
    Args:
        mutation (string): case sensitive mutation name
    Returns:
        (mutation): instance of a named mutation
    """
    mutation = mutation.lower()
    if mutation in ALL_MUTATIONS:
        return Mutation(**_MUTATION_DATA[mutation])
    else:
        raise MutationException('Invalid mutation name.')


def get_ability_score_base_for_mutation(mutation):
    """
    Retrieves the ability score that is the base for that mutation. Used by
    the progression functions to only progress the mutations related to an
    ability score that has recently been 'learned'.
    """
    for item in DEX_MUTATIONS:
        if item.name == mutation.name:
            return 'Dexterity'
    for item in STR_MUTATIONS:
        if item.name == mutation.name:
            return 'Strength'
    for item in VIT_MUTATIONS:
        if item.name == mutation.name:
            return 'Vitality'
    for item in PER_MUTATIONS:
        if item.name == mutation.name:
            return 'Perception'
    for item in FOP_MUTATIONS:
        if item.name == mutation.name:
            return 'Force of Personality'

def add_new_mutation(mutation, body_part):
    """
    Add a new mutation to a specific body part or to the whole body by passing
    in 'all' for the body_part variable. The initial score for any given new
    mutation is 1, with the exception of growing an extra limb(s).
    """
    if mutation == 'extra_limb':
        # deal with this case
        # TODO: Deal with this once the body_parts module is built
        pass

    elif mutation in ALL_MUTATIONS:
        # add any other mutation to the character or body part
        if body_part == 'all':
            character.mutations.add(
                key=mutation,
                type='static',
                base=1,
                body_part=data['body_part'],
                mod=0,
                name=data['name'],
                extra=data['extra']
            )
        else:
            part.mutations.add(
                key=mutation,
                type='static',
                base=1,
                body_part=data['body_part'],
                mod=0,
                name=data['name'],
                extra=data['extra']
            )
    else:
        raise MutationException('Invalid mutation name.')


class Mutation(object):
    """Represents a mutation's display attributes for use in help files.
    Args:
        name (str): display name for mutation
        desc (str): description of mutation
    """
    def __init__(self, name, desc, base):
        self.name = name
        self.desc = desc
        self.base = base
