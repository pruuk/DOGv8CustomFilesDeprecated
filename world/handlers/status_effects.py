# -*- coding: utf-8 -*-
"""
Status Effects module

This is a module that contains all the status effects for objects in the game.
Status Effects can have real game effects, flavor/description effects, or both.
Status Effects are generally temporary.
Status Effects can be on almost any game object.
Status Effects can be positive, negative, or both.

The standard Traithandler will record the status effect and its application.

Catergories by object type:
    - Characters & NPCs
    - Items and Equipment
    - Rooms/Zones/World
    - All

Categories by status type:
    - Damage Over Time
        - Bleeding
        - Rust
        - Rot
        - Poisoned
        - Diseased/Sick
        - Asphyxiated (damages stamina)

    - Immobilizing
        - Paralyzed
        - Exhausted
        - Locked/Jammed
        - Stunned
        - Sleep/Knocked Out
        - Broken

    - Slowing
        - Grappled
        - Entangled
        - Hindered

    - Mostly Cosmetic
        - Wet
        - Scuffed
        - Scarred
        - Polished
        - Dirty
        - Muddy

    - Impairing
        - High
        - Drunk
        - Blinded
        - Fatigued
        - Wounded
        - Deafened

    - Mentally Impairing / Altering
        - Concussed
        - Confused
        - Enamored
        - Charmed
        - Inspired
        - Feared
        - Depressed
        - Enraged
        - Mind Controlled

    - Misc
        - Hasted
        - Fast Regen

"""

## TODO: Decide how to implement status effects
