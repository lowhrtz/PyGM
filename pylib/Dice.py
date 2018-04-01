import random
import re


random.seed()
DIVIDER = 'd'


def randomInt(lower, upper):
    return random.randint(lower, upper)


def rollString(dice_string):
    single_dice_format = re.compile('^d?[0-9]+$')
    dice_format = re.compile('^[0-9]+[d][0-9]+$')
    complex_format = re.compile('^\\(?[0-9]+[d][0-9]+(\\s*\\+[0-9]+\\s*)?\\)?(\\s*[x|×]\\s*[0-9]+)?$')

    if single_dice_format.match(dice_string):
        sides = int(dice_string.replace('d', ''))
        return randomInt(1, sides)

    elif dice_format.match(dice_string):
        dice_string_list = dice_string.split(DIVIDER)
        number = int(dice_string_list[0])
        sides = int(dice_string_list[1])
        result = 0
        for _ in range(number):
            result += randomInt(1, sides)
        return result 

    elif complex_format.match(dice_string):
        dice_match = re.compile('[0-9]*[d][0-9]+')
        match = dice_match.search(dice_string)
        start, end = match.span()
        simple_dice = dice_string[start:end]
        simple_roll = rollString(simple_dice)
        eval_string = dice_string.replace(simple_dice, str(simple_roll))
        return eval(eval_string.replace('×', '*').replace('x', '*'))
    return -1


def dice_tuple(dice_string):
    dice_split = [d.strip() for d in dice_string.split('×')]
    dice_and_add = dice_split[0]
    dice_and_add = dice_and_add.replace('(', '').replace(')', '')
    dice_multiplier = None
    if len(dice_split) > 1:
        dice_multiplier = int(dice_split[1])
    dice_and_add_split = [daa.strip() for daa in dice_and_add.split('+')]
    base_dice = dice_and_add_split[0]
    add = None
    if len(dice_and_add_split) > 1:
        add = int(dice_and_add_split[1])
    base_dice_split = base_dice.split('d')
    dice_number = int(base_dice_split[0])
    dice_value = int(base_dice_split[1])
    return dice_number, dice_value, add, dice_multiplier


def dice_rating(dice_string):
    dice_number, dice_value, add, dice_multiplier = dice_tuple(dice_string)
    rating = dice_number * dice_value
    if add:
        rating += add
    if dice_multiplier:
        rating *= dice_multiplier
    return rating


def get_best_dice(dice_string_list):
    best = None
    for dice_string in dice_string_list:
        if best:
            dice_string_rating = dice_rating(dice_string)
            best_rating = dice_rating(best)
            if dice_string_rating > best_rating:
                best = dice_string
        else:
            best = dice_string

    return best
