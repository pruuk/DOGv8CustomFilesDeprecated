"""
This file will contain all the functions for controlling randomness in
interactions, much as rolling a d20 in D&D would do. There will be a number of
different ways to produce random numbers. Some will be like dice rolls in RPGs
with step-based randomness resolution (ex. Step 8 is 2d6 with any max rolls
being rerolled). Some will be based upon distribution curves (like the famous
Bell Curve).

Regardless of which style of dice roller is chosen, each method will record
critical failures and successes. These will be used to provide progression to
objects in the game (like players); the general idea is that we learn best from
our greatest screwups and best successes.
"""
# import
import numpy as np
import random
from evennia import logger
from evennia.utils.logger import log_file

# Step table for steps up to 21
step_table_dict = {
1 : {'die': [4], 'mod': -2},
2 : {'die': [4], 'mod': -1},
3 : {'die': [4], 'mod': 0},
4 : {'die': [6], 'mod': 0},
5 : {'die': [8], 'mod': 0},
6 : {'die': [10], 'mod': 0},
7 : {'die': [12], 'mod': 0},
8 : {'die': [6, 6], 'mod': 0},
9 : {'die': [8, 6], 'mod': 0},
10 : {'die': [10, 6], 'mod': 0},
11 : {'die': [10, 8], 'mod': 0},
12 : {'die': [10, 10], 'mod': 0},
13 : {'die': [20], 'mod': 1},
14 : {'die': [20, 4], 'mod': 0},
15 : {'die': [20, 6], 'mod': 0},
16 : {'die': [20, 8], 'mod': 0},
17 : {'die': [20, 10], 'mod': 0},
18 : {'die': [20, 6, 6], 'mod': 0},
19 : {'die': [20, 6, 6], 'mod': 2},
20 : {'die': [20, 6, 6], 'mod': 4},
21 : {'die': [20, 6, 6, 6], 'mod': 0}
}

# Step based random check, without criticals
def step_return_a_roll_sans_crits(step_number):
    """
    Takes in a 'Step' number and returns a random number based upon a process
    like dice rolling. This function does not re-roll max rolls.
    """
    # TODO: Make this more compact by converting to list comprehension loops
    # use the table if the step number is 21 or less
    if step_number <= 21:
        for step, method in step_table_dict:
            if step == step_number:
                 roll = 0
                 for die, mod in method:
                     mod_to_roll = mod
                     while len(die) > 1:
                         roll += random.randint(0, die.pop(0))

        return roll + mod_to_roll

    # generate the dice involved based and roll them is step above 21
    elif step_number > 21:
        dice = [20]
        num_of_d6 = int((step_number - 18) / 3) + 2
        mod_to_roll = ((step_number - 18) % 3) * 2
        for i in range(num_of_d6):
            dice.insert(-1, 6)
        while len(die) > 1:
            roll += random.randint(0, die.pop(0))

        return roll + mod_to_roll

    # error catching, we should not get here
    logger.log_trace("We produced an error in the Step roller sans crits. Check \
                     your inputs to ensure properly typecast variables were \
                     passed in.")


# Step based random check, wit criticals
def step_return_a_roll(step_number, *ability_skill_or_powers):
    """
    Takes in a 'Step' number and returns a random number based upon a process
    like dice rolling. This function re-rolls max rolls.
    """
    # convert args to a list so we can loop through it
    abil_list = list(ability_skill_or_powers)

    # use the table if the step number is 21 or less
    if step_number <= 21:
        for step, method in step_table_dict:
            if step == step_number:
                 roll = 0
                 for die, mod in method:
                     mod_to_roll = mod
                     while len(die) > 1:
                         this_roll_dice = die.pop(0)
                         this_roll = random.randint(0, this_roll_dice)
                         roll += this_roll
                         if this_roll == this_roll_dice:
                             die.insert(-1, this_roll_dice)
                             learned_something(abil_list)
                         elif this_roll == 1:
                            # critical failure roll
                            learned_something(abil_list)

        return roll + mod_to_roll

    # generate the dice involved based and roll them is step above 21
    elif step_number > 21:
        dice = [20]
        num_of_d6 = int((step_number - 18) / 3) + 2
        mod_to_roll = ((step_number - 18) % 3) * 2
        for i in range(num_of_d6):
            dice.insert(-1, 6)
        while len(die) > 1:
            this_roll_dice = die.pop(0)
            this_roll = random.randint(0, this_roll_dice)
            roll += this_roll
            if this_roll == this_roll_dice:
                die.insert(-1, this_roll_dice)
                learned_something(abil_list)
            elif this_roll == 1:
               # critical failure roll
               learned_something(abil_list)

        return roll + mod_to_roll

    # error catching, we should not get here
    logger.log_trace("We produced an error in the Step roller sans crits. Check \
                     your inputs to ensure properly typecast variables were \
                     passed in.")


# simpliest distribution curve based check, without criticals
def distro_return_a_roll_sans_crits(number, dist_shape='normal'):
    """
    Takes in a number (integer, float, etc)
    and outputs a random number from a normal distribution
    with the skill rating at the mean.
    Generally, scores should be around 100 for human "normal". They'll be
    higher than 100 for exceptionally skilled or talented individuals. For
    example, someone that powerlifts might have a strength score approaching
    200 or 300.
    Unlike the function below, however, this function will not reroll "crits",
    so the average number returned should be close to the number passed in.
    Ability scores and item durability are a good use for this function.
    A non-normal distribution can be specified, but by default, we'll return
    a random choice from a normal distribution with a mean of the variable
    'number' that was passed in and a standard deviation of 1/10 of the mean.
    dist_shape choices:
        normal
        flat
        very flat
        steep
        very steep
    """
    try:
        if dist_shape =='normal':
            return  int(np.random.default_rng().normal(loc=number, scale=number/10))
        elif dist_shape =='flat':
            return  int(np.random.default_rng().normal(loc=number, scale=number/7.5))
        elif dist_shape =='very flat':
            return  int(np.random.default_rng().normal(loc=number, scale=number/5))
        elif dist_shape =='steep':
            return  int(np.random.default_rng().normal(loc=number, scale=number/15))
        elif dist_shape =='very steep':
            return  int(np.random.default_rng().normal(loc=number, scale=number/20))
    except Exception:
        logger.log_trace("We produced an error with the return_a_roll_sans_crits \
                          function in world.dice_roller. Check your inputs and \
                          make sure the correct vars are passed in.")


def distro_return_a_roll(number, dist_shape='normal', *ability_skill_or_powers):
    """
    Returns a semi-random number from a distribution with a mean of the number
    passed in.
    A non-normal distribution can be specified, but by default, we'll return
    a random choice from a normal distribution with a mean of the variable
    'number' that was passed in and a standard deviation of 1/10 of the mean.
    dist_shape choices:
        normal
        flat
        very flat
        steep
        very steep
    Any individual rolls more than 2 deviations above or below the mean will be
    considered to be critical successes(above) or critical failures (below).
    With the idea that we learn best from our failures and triumphs, these will
    increase the learn properties of any skills, powers, or ability scores
    passed in (as *args) for each critical success or failure. Critical
    sucesses will also trigger an additional roll, but each subsequent critical
    suceess will add less and less to the total output "roll".
    When passing in the *args, make sure to format them like this:
        object_rolling.ability_score_key.learn
        object_rolling.skill_key.learn
        object_rolling.power_key.learn
        For example:
            Meirok.ability_scores.Dex.learn
    """
    # log_file(f"Calling dice roller for {ability_skill_or_powers}, which \
    #                  is type: {type(ability_skill_or_powers)}.", \
    #                  filename='dice_roller.log')
    # define variables we'll need
    total_roll = 0
    num_of_crits = 1
    # determine the scale based upon dist_shape desired
    if dist_shape =='normal':
        scale = number/10
    elif dist_shape =='flat':
        scale = number/7.5
    elif dist_shape =='very flat':
        scale = number/5
    elif dist_shape =='steep':
        scale = number/15
    elif dist_shape =='very steep':
        scale = number/20
    # convert args to a list so we can loop through it
    abil_list = list(ability_skill_or_powers)
    # while loop for rolling until we stop rolling critical successes
    while True:
        this_roll = np.random.default_rng().normal(loc=number, scale=scale)
        total_roll += this_roll/num_of_crits
        # check for rolls that are not critical successes
        if this_roll <= number * 1.2: # TODO: tune this to fire less often
            # check to make sure the roll is at least 1
            if total_roll < 1:
                # less than 1 is definitely a critical failure
                learned_something(abil_list)
                return 1
            elif this_roll < number * .8:
                # critical failure, but over 1
                learned_something(abil_list)
                return int(total_roll)
            else:
                return int(total_roll)
            # break out of the look since we're getting no bonus roll from a
            # critical suceess
            break
        # critical sucess
        elif this_roll > number * 1.2:
            learned_something(abil_list)
            num_of_crits += 1
        else:
            logger.log_trace("We produced an error with the regular roller.")

# TODO: Clean this up so it isn't use try/except
def learned_something(abil_list):
    """
    Takes in a single ability, skill, or power. Adds one to the learn attribute
    for that ability score, skill, or power. This should only be called after
    a critical success on a roll, a critical failure on a roll, or after the
    completion of certain quests.
    """
    try:
        for ability_skill_or_power in abil_list:
            log_file(f"Something was learned about {ability_skill_or_power}",  \
                             filename='dice_roller.log')
            log_file(f"Current learn value: {ability_skill_or_power.learn}",  \
                             filename='dice_roller.log')
            ability_skill_or_power.learn += 1
            log_file(f"New learn value: {ability_skill_or_power.learn}",  \
                             filename='dice_roller.log')

    except Exception:
        logger.log_trace(f"We produced an error trying to increase the learning \
                          value on {ability_skill_or_power_learn_attribute}")
    return
