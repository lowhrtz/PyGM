import re
# import DbQuery
import Dice
from Common import Range, RollTable

base_pattern = r'(\d+d\d+[+-x×]?[\d,]*|\d+) ?'
percent_pattern = r' ?(?:\((\d+)%.*\))?'
cp_pattern = re.compile(base_pattern + 'cp' + percent_pattern)
sp_pattern = re.compile(base_pattern + 'sp' + percent_pattern)
ep_pattern = re.compile(base_pattern + 'ep' + percent_pattern)
gp_pattern = re.compile(base_pattern + 'gp' + percent_pattern)
pp_pattern = re.compile(base_pattern + 'pp' + percent_pattern)
gems_pattern = re.compile(base_pattern + 'gems' + percent_pattern)
jewellery_pattern = re.compile(base_pattern + 'jewellery' + percent_pattern)
magic_items_pattern = re.compile(base_pattern + 'magic items?' + percent_pattern)
scrolls_pattern = re.compile(base_pattern + 'scrolls?' + percent_pattern)
potions_pattern = re.compile(base_pattern + 'potions?' + percent_pattern)
rings_pattern = re.compile(base_pattern + 'rings?' + percent_pattern)

gemstone_desc_levels = [
        'Ornamental', 'Semi-Precious', 'Fancy',
        'Precious', 'Gem', 'Jewel'
    ]

gemstone_value_levels = [
        '4d4', '2d4x10', '4d4x10',
        '2d4x100', '4d4x100', '2d4x1000'
]

alter_roll_dice_string = '1d10'


def get_treasure_list(match):
    return [int(m[0]) if m[0].isdigit() else Dice.rollString(m[0])
            for m in match if not m[1] or int(m[1]) >= Dice.randomInt(1, 100)]


def parse_treasure_text(treasure_text, wandering=True):
    treasure_split = treasure_text.split(';')
    if len(treasure_split) == 1:
        individual = treasure_split[0]
        lair = ''
    else:
        if 'individual' in treasure_split[0].lower():
            individual = treasure_split[0]
            lair = treasure_split[1]
        else:
            lair = treasure_split[0]
            individual = treasure_split[1]
    if wandering:
        t = individual
    else:
        t = lair
    cp_match = cp_pattern.findall(t)
    sp_match = sp_pattern.findall(t)
    ep_match = ep_pattern.findall(t)
    gp_match = gp_pattern.findall(t)
    pp_match = pp_pattern.findall(t)
    gems_match = gems_pattern.findall(t)
    gems = [gemstone_table() for _ in range(1, sum(get_treasure_list(gems_match)) + 1)]
    jewellery_match = jewellery_pattern.findall(t)
    jewellery = [jewellery_table() for _ in range(1, sum(get_treasure_list(jewellery_match)) + 1)]

    magic_items_match = magic_items_pattern.findall(t)
    magic_items = [magic_items_table() for _ in range(1, sum(get_treasure_list(magic_items_match)) + 1)]
    scrolls_match = scrolls_pattern.findall(t)
    scrolls = [scrolls_table() for _ in range(1, sum(get_treasure_list(scrolls_match)) + 1)]
    potions_match = potions_pattern.findall(t)
    potions = [potions_table() for _ in range(1, sum(get_treasure_list(potions_match)) + 1)]
    rings_match = rings_pattern.findall(t)
    rings = [rings_table() for _ in range(1, sum(get_treasure_list(rings_match)) + 1)]

    return {
        'cp': sum(get_treasure_list(cp_match)),
        'sp': sum(get_treasure_list(sp_match)),
        'ep': sum(get_treasure_list(ep_match)),
        'gp': sum(get_treasure_list(gp_match)),
        'pp': sum(get_treasure_list(pp_match)),
        'gems': gems,
        'jewellery': jewellery,

        'magic_items': magic_items + scrolls + potions + rings,
        # 'potions': potions,
        # 'rings': rings,
    }


def gemstone_table(description=None):
    if description:
        return alter_gemstone(description)
    # else:
    #     percent_roll = Dice.randomInt(1, 100)
    #     if 1 <= percent_roll <= 30:
    #         return alter_gemstone('Ornamental')
    #     elif 31 <= percent_roll <= 55:
    #         return alter_gemstone('Semi-Precious')
    #     elif 56 <= percent_roll <= 75:
    #         return alter_gemstone('Fancy')
    #     elif 76 <= percent_roll <= 90:
    #         return alter_gemstone('Precious')
    #     elif 91 <= percent_roll <= 99:
    #         return alter_gemstone('Gem')
    #     else:
    #         return alter_gemstone('Jewel')

    gt = RollTable('d100', {
        Range(1, 30): lambda: alter_gemstone('Ornamental'),
        Range(31, 55): lambda: alter_gemstone('Semi-Precious'),
        Range(56, 75): lambda: alter_gemstone('Fancy'),
        Range(76, 90): lambda: alter_gemstone('Precious'),
        Range(91, 99): lambda: alter_gemstone('Gem'),
        Range(100, 100): lambda: alter_gemstone('Jewel'),
    })

    return gt.roll()


def alter_gemstone(description):
    alter_roll = Dice.rollString(alter_roll_dice_string)
    return alter_table(alter_roll, gemstone_desc_levels.index(description))


def alter_table(alter_roll, desc_level, ignore_list=()):
    if alter_roll in ignore_list:
        return alter_table(Dice.rollString(alter_roll_dice_string), desc_level, ignore_list)
    # gemstones = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Gemstone']
    if alter_roll == 1:
        return alter_table(Dice.rollString(alter_roll_dice_string), desc_level + 1, [9, 10])
    elif alter_roll == 10:
        return alter_table(Dice.rollString(alter_roll_dice_string), desc_level - 1, [1])
    else:
        value = None
        if desc_level == -1:
            value = 10
        elif desc_level == -2:
            value = 5
        elif desc_level == -3:
            value = 1
        elif desc_level == -4:
            value = .5
        elif desc_level == -5:
            value = .1
        elif desc_level == len(gemstone_desc_levels):
            value = 5000
        elif desc_level == len(gemstone_desc_levels) + 1:
            value = 10000
        elif desc_level == len(gemstone_desc_levels) + 2:
            value = 25000
        elif desc_level == len(gemstone_desc_levels) + 3:
            value = 50000
        elif desc_level == len(gemstone_desc_levels) + 4:
            value = 100000
        elif desc_level == len(gemstone_desc_levels) + 5:
            value = 250000
        elif desc_level == len(gemstone_desc_levels) + 6:
            value = 500000
        elif desc_level >= len(gemstone_desc_levels) + 7:
            value = 1000000
        if desc_level < 0:
            desc_level = 0
        elif desc_level >= len(gemstone_desc_levels):
            desc_level = len(gemstone_desc_levels) - 1
        # gemstone_candidates = [g for g in gemstones if g['Subcategory'] == gemstone_desc_levels[desc_level]]
        # gemstone = gemstone_candidates[Dice.randomInt(0, len(gemstone_candidates) - 1)]
        # if value is None:
        #     value = Dice.rollString(gemstone['Value'])
        if value is None:
            value = Dice.rollString(gemstone_value_levels[desc_level])
        if alter_roll == 2 or alter_roll == 3:
            value *= alter_roll
        elif alter_roll == 9:
            value -= value*Dice.rollString('1d4x10')/100
        # gemstone['Actual Value'] = value
        # return gemstone
        return gemstone_desc_levels[desc_level], value


def jewellery_table():
    # jewellery = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Jewellery']
    # jewellery_indexed = {j['unique_id']: j for j in jewellery}
    percent_roll = Dice.randomInt(1, 100)
    d10_roll = Dice.rollString('d10')
    for key in jewellery_matrix.keys():
        lower, upper = treasure_matrix_key_pattern.match(key).groups()
        if upper is None:
            upper = lower
        if percent_roll in range(int(lower), int(upper) + 1):
            row = jewellery_matrix[key]
            jewellery_item = row[0]
            for i in range(1, len(row)):
                l, u = treasure_matrix_key_pattern.match(row[i]).groups()
                if u is None:
                    u = l
                if d10_roll in range(int(l), int(u) + 1):
                    jewellery_quality = jewellery_quality_levels[i]
                    item_id = f'jewellery_{jewellery_item}_{jewellery_quality}'
                    # j = jewellery_indexed[item_id]
                    # j['Actual Value'] = Dice.rollString(j['Value'])
                    # return j
                    return item_id


treasure_matrix_key_pattern = re.compile(r'^(\d+)[-]?(\d+)?$')
jewellery_quality_levels = ['', 'silver', 'silver_gold', 'gold', 'silver_gems', 'gold_gems', 'exceptional']
jewellery_matrix = {
    '1-3': ('amulet', '1-4', '5-7', '8-9', '10'),
    '4': ('anklet', '1-3', '4-6', '7-8', '9', '10'),
    '5-7': ('arm_ring', '1-4', '5-6', '7-8', '9', '10'),
    '8-10': ('belt', '1-4', '5-6', '7-8', '9-10'),
    '11-12': ('box', '1-4', '5-7', '8-9', '10'),
    '13-17': ('bracelet', '1-3', '4-6', '7-8', '9', '10'),
    '18-20': ('brooch', '1-3', '4-6', '7-8', '9', '10'),
    '21-23': ('buckle', '1-4', '5-7', '8-9', '10'),
    '24-25': ('chain', '1-4', '5-7', '8-9', '10'),
    '26-27': ('chalice', '1-3', '4-6', '7-8', '9', '10'),
    '28-30': ('choker', '1-4', '5-7', '8-9', '10'),
    '31-32': ('clasp', '1-4', '5-6', '7-8', '9-10'),
    '33-35': ('comb', '1-3', '4-6', '7-8', '9', '10'),
    '36-37': ('coronet', '1', '2', '3-4', '5-8', '9', '10'),
    '38': ('crown', '1', '2', '3', '4', '5-7', '8-10'),
    '39-40': ('diadem', '1-3', '4-6', '7-8', '9', '10'),
    '41-46': ('earring', '1-3', '4-6', '7-8', '9', '10'),
    '47-49': ('goblet', '1-3', '4-6', '7-8', '9', '10'),
    '50-51': ('idol', '1-2', '3-4', '5-7', '8-9', '10'),
    '52-54': ('knife', '1-4', '5-7', '8-9', '10'),
    '55-58': ('locket', '1-3', '4-5', '6-7', '8-9', '10'),
    '59-60': ('medal', '1-4', '5-7', '8-10'),
    '61-64': ('medallion', '1-3', '4-6', '7-9', '10'),
    '65-69': ('necklace', '1-3', '4-6', '7-8', '9', '10'),
    '70-73': ('pendant', '1-3', '4-6', '7-8', '9', '10'),
    '74-77': ('pin', '1-3', '4-6', '7-8', '9', '10'),
    '78': ('orb', '1', '2', '3', '4-5', '6-8', '9-10'),
    '79-87': ('ring', '1-3', '4-6', '7-8', '9', '10'),
    '88': ('sceptre', '1', '2', '3', '4-5', '6-8', '9-10'),
    '89-92': ('seal', '1-4', '5-7', '8-9', '10'),
    '93-94': ('statuette', '1-3', '4-6', '7-8', '9', '10'),
    '95': ('tiara', '1-3', '4-6', '7-8', '9', '10'),
    '96-97': ('toe_ring', '1-3', '4-6', '7-8', '9', '10'),
    '98-100': ('weapon_hilt', '1-3', '4-6', '7-8', '9', '10'),
}


def magic_items_table():
    # magic_items_roll = Dice.rollString('d20')
    # if 1 <= magic_items_roll <= 3:
    #     return armour_shield_table()
    # elif 4 <= magic_items_roll <= 6:
    #     return miscellaneous_magic_table()
    # elif 7 <= magic_items_roll <= 9:
    #     return miscellaneous_weapons_table()
    # elif 10 <= magic_items_roll <= 13:
    #     return potions_table()
    # elif magic_items_roll == 14:
    #     return rings_table()
    # elif magic_items_roll == 15:
    #     return rods_staves_wands_table()
    # elif 16 <= magic_items_roll <= 18:
    #     return scrolls_table()
    # else:
    #     return swords_table()

    mit = RollTable('d20', {
        Range(1, 3): armour_shield_table,
        Range(4, 6): miscellaneous_magic_table,
        Range(7, 9): miscellaneous_weapons_table,
        Range(10, 13): potions_table,
        Range(14, 14): rings_table,
        Range(15, 15): rods_staves_wands_table,
        Range(16, 18): scrolls_table,
        Range(19, 20): swords_table,

    })

    return mit.roll()


def armour_shield_table():
    # armour = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Armour']
    # armour_indexed = {a['unique_id']: a for a in armour}
    # first_roll = Dice.rollString('d20')
    # second_roll = Dice.randomInt(1, 100)
    # if first_roll == 1:
    #     armour_type = 'banded'
    # elif 2 <= first_roll <= 4:
    #     if 1 <= second_roll <= 90:
    #         armour_type = 'chain'
    #     else:
    #         armour_type = 'elfin_chain'
    # elif 5 <= first_roll <= 6:
    #     armour_type = 'leather'
    # elif 7 <= first_roll <= 9:
    #     armour_type = 'plate'
    # elif first_roll == 10:
    #     armour_type = 'ring'
    # elif 11 <= first_roll <= 12:
    #     armour_type = 'splint'
    # elif 13 <= first_roll <= 14:
    #     armour_type = 'scale'
    # elif first_roll == 15:
    #     armour_type = 'studded'
    # else:
    #     armour_type = 'medium'

    armour_type_table = RollTable('d20', {
        Range(1, 1): 'banded',
        Range(2, 4): RollTable('d100', {
            Range(1, 90): 'chain',
            Range(91, 100): 'elfin_chain',
        }),
        Range(5, 6): 'leather',
        Range(7, 9): 'plate',
        Range(10, 10): 'ring',
        Range(11, 12): 'splint',
        Range(13, 14): 'scale',
        Range(15, 15): 'studded',
        Range(16, 20): 'medium',
    })
    armour_type = armour_type_table.roll()

    # power_roll = Dice.rollString('d20')
    # second_power_roll = Dice.randomInt(1, 100)
    # if 1 <= power_roll <= 10:
    #     power = '+1'
    # elif 11 <= power_roll <= 15:
    #     power = '+2'
    # elif power_roll == 16:
    #     power = '+3'
    # elif power_roll == 17:
    #     if 1 <= second_power_roll <= 65:
    #         power = '+4'
    #     else:
    #         power = '+5'
    # elif power_roll == 18:
    #     power = 'cursed'
    # else:
    #     return special_armour_table(armour_indexed)

    power_table = RollTable('d20', {
        Range(1, 10): '+1',
        Range(11, 15): '+2',
        Range(16, 16): '+3',
        Range(17, 17): RollTable('d100', {
            Range(1, 65): '+4',
            Range(66, 100): '+5',
        }),
        Range(18, 18): 'cursed',
        Range(19, 20): 0,
    })
    power = power_table.roll()
    if power == 0:
        return special_armour_table()

    if armour_type == 'medium':
        id_prefix = 'shield'
    else:
        id_prefix = 'armour'
    # armour_id = f'{id_prefix}_{armour_type}_{power}'
    # return armour_indexed[armour_id]
    return f'{id_prefix}_{armour_type}_{power}'


# def special_armour_table(armour_indexed=None):
def special_armour_table():
    # if armour_indexed is None:
    #     armour = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Armour']
    #     armour_indexed = {a['unique_id']: a for a in armour}
    # roll = Dice.rollString('1d2')
    # if roll == 1:
    #     return armour_indexed['shield_large_+1_missile_deflector']
    # else:
    #     return armour_indexed['armor_plate_mail_of_aethereality_16_20_charges_remaining']
    return RollTable('1d2', {
        Range(1, 1): 'shield_large_+1_missile_deflector',
        Range(2, 2): 'armor_plate_mail_of_aethereality_16_20_charges_remaining',
    }).roll()


def miscellaneous_weapons_table():
    # weapons = [w for w in DbQuery.getTable('Items') if w['Category'] == 'Weapon']
    # weapons_indexed = {w['unique_id']: w for w in weapons}
    first_roll = Dice.rollString('d20')
    second_roll = Dice.rollString('d100')
    third_roll = Dice.rollString('d4')

    if 1 <= first_roll <= 3:
        weapon_type = 'arrow'
    elif 4 <= first_roll <= 5:
        if 1 <= second_roll <= 50:
            weapon_type = 'axe_battle'
        else:
            weapon_type = 'axe_hand'
    elif first_roll == 6:
        if 1 <= second_roll <= 50:
            weapon_type = 'bolt_heavy_xbow'
        else:
            weapon_type = 'bolt_light_xbow'
    elif first_roll == 7:
        if 1 <= second_roll <= 50:
            if third_roll == 1:
                weapon_type = 'bow_long'
            elif third_roll == 2:
                weapon_type = 'bow_short'
            elif third_roll == 3:
                weapon_type = 'composite_bow_long'
            else:
                weapon_type = 'composite_bow_short'
        else:
            if 1 <= third_roll <= 2:
                weapon_type = 'crossbow_heavy'
            else:
                weapon_type = 'crossbow_light'
    elif 8 <= first_roll <= 11:
        weapon_type = 'dagger'
    elif first_roll == 12:
        if 1 <= second_roll <= 50:
            weapon_type = 'flail_heavy'
        else:
            weapon_type = 'flail_light'
    elif first_roll == 13:
        if 1 <= second_roll <= 50:
            weapon_type = 'hammer_war_heavy'
        else:
            weapon_type = 'hammer_war_light'
    elif first_roll == 14:
        weapon_type = 'javelin'
    elif 15 <= first_roll <= 16:
        if 1 <= second_roll <= 50:
            weapon_type = 'mace_heavy'
        else:
            weapon_type = 'mace_light'
    elif first_roll == 17:
        if 1 <= second_roll <= 33:
            if 1 <= third_roll <= 2:
                weapon_type = 'pick_heavy'
            else:
                weapon_type = 'pick_light'
        elif 34 <= second_roll <= 66:
            weapon_type = 'morning_star'
        else:
            weapon_type = 'pole_arm'
    elif first_roll == 18:
        weapon_type = 'sword_scimitar'
    elif first_roll == 19:
        weapon_type = 'spear'
    else:
        if 1 <= second_roll <= 50:
            weapon_type = 'trident'
        else:
            weapon_type = 'sling'

    power_roll = Dice.rollString('d20')
    second_power_roll = Dice.rollString('d100')
    if 1 <= power_roll <= 10:
        power = '+1'
    elif 11 <= power_roll <= 15:
        power = '+2'
    elif power_roll == 16:
        power = '+3'
    elif power_roll == 17:
        if 1 <= second_power_roll <= 65:
            power = '+4'
        else:
            power = '+5'
    elif power_roll == 18:
        power = 'cursed'
    else:
        # return special_miscellaneous_weapons_table(weapons_indexed)
        return special_miscellaneous_weapons_table()

    weapon_id = f'{weapon_type}_{power}'
    # return weapons_indexed[weapon_id]
    return weapon_id


# def special_miscellaneous_weapons_table(weapons_indexed=None):
def special_miscellaneous_weapons_table():
    # if weapons_indexed is None:
    #     weapons = [w for w in DbQuery.getTable('Items') if w['Category'] == 'Weapon']
    #     weapons_indexed = {w['unique_id']: w for w in weapons}
    # first_roll = Dice.rollString('d100')
    # second_roll = Dice.rollString('d2')
    # if 1 <= first_roll <= 5:
    #     return weapons_indexed['arrow_of_slaying']
    # elif 6 <= first_roll <= 15:
    #     return weapons_indexed['axe_of_hurling']
    # elif 16 <= first_roll <= 30:
    #     if second_roll == 1:
    #         return weapons_indexed['crossbow_of_accuracy_heavy']
    #     else:
    #         return weapons_indexed['crossbow_of_accuracy_light']
    # elif 31 <= first_roll <= 40:
    #     if second_roll == 1:
    #         return weapons_indexed['crossbow_of_range_heavy']
    #     else:
    #         return weapons_indexed['crossbow_of_range_light']
    # elif 41 <= first_roll <= 50:
    #     if second_roll == 1:
    #         return weapons_indexed['crossbow_of_speed_heavy']
    #     else:
    #         return weapons_indexed['crossbow_of_speed_light']
    # elif 51 <= first_roll <= 60:
    #     return weapons_indexed['dagger_of_venom']
    # elif 61 <= first_roll <= 70:
    #     if second_roll == 1:
    #         return weapons_indexed['hammer_of_the_dwarfs_war_heavy']
    #     else:
    #         return weapons_indexed['hammer_of_the_dwarfs_war_light']
    # elif 71 <= first_roll <= 75:
    #     if second_roll == 1:
    #         return weapons_indexed['mace_holy_heavy']
    #     else:
    #         return weapons_indexed['mace_holy_light']
    # elif 76 <= first_roll <= 85:
    #     return weapons_indexed['sling_of_the_halfling']
    # else:
    #     return weapons_indexed['trident_fork']

    smwt = RollTable('d100', {
        Range(1, 5): 'arrow_of_slaying',
        Range(6, 15): 'axe_of_hurling',
        Range(16, 30): RollTable('d2', {
            Range(1, 1): 'crossbow_of_accuracy_heavy',
            Range(2, 2): 'crossbow_of_accuracy_light',
        }),
        Range(31, 40): RollTable('d2', {
            Range(1, 1): 'crossbow_of_range_heavy',
            Range(2, 2): 'crossbow_of_range_light',
        }),
        Range(41, 50): RollTable('d2', {
            Range(1, 1): 'crossbow_of_speed_heavy',
            Range(2, 2): 'crossbow_of_speed_light',
        }),
        Range(51, 60): 'dagger_of_venom',
        Range(61, 70): RollTable('d2', {
            Range(1, 1): 'hammer_of_the_dwarfs_war_heavy',
            Range(2, 2): 'hammer_of_the_dwarfs_war_light',
        }),
        Range(71, 75): RollTable('d2', {
            Range(1, 1): 'mace_holy_heavy',
            Range(2, 2): 'mace_holy_light',
        }),
        Range(76, 85): 'sling_of_the_halfling',
        Range(86, 100): 'trident_fork',
    })

    return smwt.roll()


def potions_table():
    # potions = [p for p in DbQuery.getTable('Items') if p['Category'] == 'Potion']
    # potions_indexed = {p['unique_id']: p for p in potions}
    #
    # first_roll = Dice.rollString('d20')
    # second_roll = Dice.rollString('d100')
    #
    # if first_roll == 1:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_animal_control']
    #     else:
    #         return potions_indexed['potion_clairaudience']
    # elif first_roll == 2:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_clairvoyance']
    #     else:
    #         return potions_indexed['potion_climbing']
    # elif first_roll == 3:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_cursed']
    #     else:
    #         return potions_indexed['potion_delusion']
    # elif first_roll == 4:
    #     if 1 <= second_roll <= 65:
    #         return potions_indexed['potion_diminution']
    #     else:
    #         dragon_roll = Dice.rollString('d20')
    #         if 1 <= dragon_roll <= 2:
    #             return potions_indexed['potion_black_dragon_control']
    #         elif 3 <= dragon_roll <= 4:
    #             return potions_indexed['potion_blue_dragon_control']
    #         elif 5 <= dragon_roll <= 6:
    #             return potions_indexed['potion_brass_dragon_control']
    #         elif dragon_roll == 7:
    #             return potions_indexed['potion_bronze_dragon_control']
    #         elif 8 <= dragon_roll <= 9:
    #             return potions_indexed['potion_copper_dragon_control']
    #         elif dragon_roll == 10:
    #             return potions_indexed['potion_gold_dragon_control']
    #         elif 11 <= dragon_roll <= 13:
    #             return potions_indexed['potion_green_dragon_control']
    #         elif dragon_roll == 14:
    #             return potions_indexed['potion_red_dragon_control']
    #         elif dragon_roll == 15:
    #             return potions_indexed['potion_silver_dragon_control']
    #         elif 16 <= dragon_roll <= 17:
    #             return potions_indexed['potion_white_dragon_control']
    #         elif 18 <= dragon_roll <= 19:
    #             return potions_indexed['potion_evil_dragon_control']
    #         else:
    #             return potions_indexed['potion_good_dragon_control']
    # elif first_roll == 5:
    #     return potions_indexed['potion_esp']
    # elif first_roll == 6:
    #     if 1 <= second_roll <= 35:
    #         return potions_indexed['potion_extra_healing']
    #     else:
    #         return potions_indexed['potion_fire_resistance']
    # elif first_roll == 7:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_flying']
    #     else:
    #         return potions_indexed['potion_gaseous_form']
    # elif first_roll == 8:
    #     giant_roll = Dice.rollString('d20')
    #     if 1 <= second_roll <= 50:
    #         if 1 <= giant_roll <= 2:
    #             return potions_indexed['potion_cloud_giant_control']
    #         elif 3 <= giant_roll <= 6:
    #             return potions_indexed['potion_fire_giant_control']
    #         elif 7 <= giant_roll <= 10:
    #             return potions_indexed['potion_frost_giant_control']
    #         elif 11 <= giant_roll <= 15:
    #             return potions_indexed['potion_hill_giant_control']
    #         elif 16 <= giant_roll <= 19:
    #             return potions_indexed['potion_stone_giant_control']
    #         else:
    #             return potions_indexed['potion_storm_giant_control']
    #     else:
    #         if 1 <= giant_roll <= 6:
    #             return potions_indexed['potion_hill_giant_strength']
    #         elif 7 <= giant_roll <= 10:
    #             return potions_indexed['potion_stone_giant_strength']
    #         elif 11 <= giant_roll <= 14:
    #             return potions_indexed['potion_frost_giant_strength']
    #         elif 15 <= giant_roll <= 17:
    #             return potions_indexed['potion_fire_giant_strength']
    #         elif 18 <= giant_roll <= 19:
    #             return potions_indexed['potion_cloud_giant_strength']
    #         else:
    #             return potions_indexed['potion_storm_giant_strength']
    # elif first_roll == 9:
    #     return potions_indexed['potion_growth']
    # elif first_roll == 10:
    #     return potions_indexed['potion_healing']
    # elif first_roll == 11:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_heroism']
    #     else:
    #         human_roll = Dice.rollString('d20')
    #         if 1 <= human_roll <= 2:
    #             return potions_indexed['potion_human_control_dwarfs']
    #         elif 3 <= human_roll <= 4:
    #             return potions_indexed['potion_human_control_elves']
    #         elif human_roll == 5:
    #             return potions_indexed['potion_human_control_elves_humans']
    #         elif 6 <= human_roll <= 7:
    #             return potions_indexed['potion_human_control_gnomes']
    #         elif 8 <= human_roll <= 9:
    #             return potions_indexed['potion_human_control_halflings']
    #         elif 10 <= human_roll <= 11:
    #             return potions_indexed['potion_human_control_half_orcs']
    #         elif 12 <= human_roll <= 17:
    #             return potions_indexed['potion_human_control_humans']
    #         else:
    #             return potions_indexed['potion_human_control_other']
    # elif first_roll == 12:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_invisibility']
    #     else:
    #         return potions_indexed['potion_invulnerability']
    # elif first_roll == 13:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_levitation']
    #     else:
    #         return potions_indexed['potion_longevity']
    # elif first_roll == 14:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_oil_aetherealness']
    #     else:
    #         return potions_indexed['potion_oil_slipperiness']
    # elif first_roll == 15:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_philtre_love']
    #     else:
    #         return potions_indexed['potion_philtre_persuasiveness']
    # elif first_roll == 16:
    #     if 1 <= second_roll <= 65:
    #         return potions_indexed['potion_plant_control']
    #     else:
    #         return potions_indexed['potion_polymorph']
    # elif first_roll == 17:
    #     if 1 <= second_roll <= 50:
    #         return potions_indexed['potion_speed']
    #     else:
    #         return potions_indexed['potion_super_heroism']
    # elif first_roll == 18:
    #     return potions_indexed['potion_sweet_water']
    # elif first_roll == 19:
    #     if 1 <= second_roll <= 75:
    #         return potions_indexed['potion_treasure_finding']
    #     else:
    #         undead_roll = Dice.rollString('d10')
    #         if undead_roll == 1:
    #             return potions_indexed['potion_undead_control_ghasts']
    #         elif undead_roll == 2:
    #             return potions_indexed['potion_undead_control_ghosts']
    #         elif undead_roll == 3:
    #             return potions_indexed['potion_undead_control_ghouls']
    #         elif undead_roll == 4:
    #             return potions_indexed['potion_undead_control_shadows']
    #         elif undead_roll == 5:
    #             return potions_indexed['potion_undead_control_skeletons']
    #         elif undead_roll == 6:
    #             return potions_indexed['potion_undead_control_spectres']
    #         elif undead_roll == 7:
    #             return potions_indexed['potion_undead_control_vampires']
    #         elif undead_roll == 8:
    #             return potions_indexed['potion_undead_control_wights']
    #         elif undead_roll == 9:
    #             return potions_indexed['potion_undead_control_wraiths']
    #         elif undead_roll == 10:
    #             return potions_indexed['potion_undead_control_zombies']
    # else:
    #     return potions_indexed['potion_water_breathing']

    pt = RollTable('d20', {
        Range(1, 1): RollTable('d100', {
            Range(1, 50): 'potion_animal_control',
            Range(51, 100): 'potion_clairaudience',
        }),
        Range(2, 2): RollTable('d100', {
            Range(1, 50): 'potion_clairvoyance',
            Range(51, 100): 'potion_climbing',
        }),
        Range(3, 3): RollTable('d100', {
            Range(1, 50): 'potion_cursed',
            Range(51, 100): 'potion_delusion',
        }),
        Range(4, 4): RollTable('d100', {
            Range(1, 65): 'potion_diminution',
            Range(66, 100): RollTable('d20', {
                Range(1, 2): 'potion_black_dragon_control',
                Range(3, 4): 'potion_blue_dragon_control',
                Range(5, 6): 'potion_brass_dragon_control',
                Range(7, 7): 'potion_bronze_dragon_control',
                Range(8, 9): 'potion_copper_dragon_control',
                Range(10, 10): 'potion_gold_dragon_control',
                Range(11, 13): 'potion_green_dragon_control',
                Range(14, 14): 'potion_red_dragon_control',
                Range(15, 15): 'potion_silver_dragon_control',
                Range(16, 17): 'potion_white_dragon_control',
                Range(18, 19): 'potion_evil_dragon_control',
                Range(20, 20): 'potion_good_dragon_control',
            }),
        }),
        Range(5, 5): 'potion_esp',
        Range(6, 6): RollTable('d100', {
            Range(1, 35): 'potion_extra_healing',
            Range(36, 100): 'potion_fire_resistance',
        }),
        Range(7, 7): RollTable('d100', {
            Range(1, 50): 'potion_flying',
            Range(51, 100): 'potion_gaseous_form',
        }),
        Range(8, 8): RollTable('d100', {
            Range(1, 50): RollTable('d20', {
                Range(1, 2): 'potion_cloud_giant_control',
                Range(3, 6): 'potion_fire_giant_control',
                Range(7, 10): 'potion_frost_giant_control',
                Range(11, 15): 'potion_hill_giant_control',
                Range(16, 19): 'potion_stone_giant_control',
                Range(20, 20): 'potion_storm_giant_control',
            }),
            Range(51, 100): RollTable('d20', {
                Range(1, 6): 'potion_hill_giant_strength',
                Range(7, 10): 'potion_stone_giant_strength',
                Range(11, 14): 'potion_frost_giant_strength',
                Range(15, 17): 'potion_fire_giant_strength',
                Range(18, 19): 'potion_cloud_giant_strength',
                Range(20, 20): 'potion_storm_giant_strength',
            }),
        }),
        Range(9, 9): 'potion_growth',
        Range(10, 10): 'potion_healing',
        Range(11, 11): RollTable('d100', {
            Range(1, 50): 'potion_heroism',
            Range(51, 100): RollTable('d20', {
                Range(1, 2): 'potion_human_control_dwarfs',
                Range(3, 4): 'potion_human_control_elves',
                Range(5, 5): 'potion_human_control_elves_humans',
                Range(6, 7): 'potion_human_control_gnomes',
                Range(8, 9): 'potion_human_control_halflings',
                Range(10, 11): 'potion_human_control_half_orcs',
                Range(12, 17): 'potion_human_control_humans',
                Range(18, 20): 'potion_human_control_other',
            }),
        }),
        Range(12, 12): RollTable('d100', {
            Range(1, 50): 'potion_invisibility',
            Range(51, 100): 'potion_invulnerability',
        }),
        Range(13, 13): RollTable('d100', {
            Range(1, 50): 'potion_levitation',
            Range(51, 100): 'potion_longevity',
        }),
        Range(14, 14): RollTable('d100', {
            Range(1, 50): 'potion_oil_aetherealness',
            Range(51, 100): 'potion_oil_slipperiness',
        }),
        Range(15, 15): RollTable('d100', {
            Range(1, 50): 'potion_philtre_love',
            Range(51, 100): 'potion_philtre_persuasiveness',
        }),
        Range(16, 16): RollTable('d100', {
            Range(1, 65): 'potion_plant_control',
            Range(66, 100): 'potion_polymorph',
        }),
        Range(17, 17): RollTable('d100', {
            Range(1, 50): 'potion_speed',
            Range(51, 100): 'potion_super_heroism',
        }),
        Range(18, 18): 'potion_sweet_water',
        Range(19, 19): RollTable('d100', {
            Range(1, 75): 'potion_treasure_finding',
            Range(76, 100): RollTable('d10', {
                Range(1, 1): 'potion_undead_control_ghasts',
                Range(2, 2): 'potion_undead_control_ghosts',
                Range(3, 3): 'potion_undead_control_ghouls',
                Range(4, 4): 'potion_undead_control_shadows',
                Range(5, 5): 'potion_undead_control_skeletons',
                Range(6, 6): 'potion_undead_control_spectres',
                Range(7, 7): 'potion_undead_control_vampires',
                Range(8, 8): 'potion_undead_control_wights',
                Range(9, 9): 'potion_undead_control_wraiths',
                Range(10, 10): 'potion_undead_control_zombies',
            }),
        }),
        Range(20, 20): 'potion_water_breathing',
    })

    return pt.roll()


def rings_table():
    rt = RollTable('d20', {
        Range(1, 1): 'ring_charisma',
        Range(2, 3): 'ring_feather_falling',
        Range(4, 4): 'ring_fire_resistance',
        Range(5, 5): 'ring_free_action',
        Range(6, 6): 'ring_genie_summoning',
        Range(7, 7): 'ring_invisibility',
        Range(8, 12): RollTable('d100', {
            Range(1, 68): 'ring_protection_+1',
            Range(69, 70): 'ring_protection_+1_5_ft_radius',
            Range(71, 92): 'ring_protection_+2',
            Range(93, 93): 'ring_protection_+2_5_ft_radius',
            Range(94, 97): 'ring_protection_+3',
            Range(98, 98): 'ring_protection_+3_5_ft_radius',
            Range(99, 99): 'ring_protection_+4ac_+1_saving_throw',
            Range(100, 100): 'ring_protection_+5ac_+1_saving_throw',
        }),
        Range(13, 13): RollTable('d100', {
            Range(1, 25): RollTable('d100', {
                Range(1, 90): 'ring_regeneration',
                Range(91, 100): 'ring_vampiric_regeneration'
            }),
            Range(26, 100): 'ring_spell_storing',
        }),
        Range(14, 14): 'ring_spell_turning',
        Range(15, 15): 'ring_swimming',
        Range(16, 16): RollTable('d100', {
           Range(1, 50): RollTable('d100', {
               Range(1, 25): 'ring_telekinesis_25',
               Range(26, 50): 'ring_telekinesis_50',
               Range(51, 89): 'ring_telekinesis_100',
               Range(90, 99): 'ring_telekinesis_200',
               Range(100, 100): 'ring_telekinesis_400',
           }),
           Range(51, 100): RollTable('d100', {
                Range(1, 25): 'ring_three_wishes_limited',
                Range(26, 100): 'ring_three_wishes',
           }),
        }),
        Range(17, 17): 'ring_warmth',
        Range(18, 19): 'ring_water_walking',
        Range(20, 20): RollTable('d100', {
            Range(1, 45): 'ring_wizardry_1st',
            Range(46, 75): 'ring_wizardry_2nd',
            Range(76, 82): 'ring_wizardry_3rd',
            Range(83, 88): 'ring_wizardry_1st_2nd',
            Range(89, 92): 'ring_wizardry_4th',
            Range(93, 95): 'ring_wizardry_5th',
            Range(96, 99): 'ring_wizardry_1st_2nd_3rd',
            Range(100, 100): 'ring_wizardry_4th_5th',
        }),
    })

    # rings = [r for r in DbQuery.getTable('Items') if r['Category'] == 'Ring']
    # rings_indexed = {r['unique_id']: r for r in rings}
    # return rings_indexed[rt.roll()]
    return rt.roll()


def rods_staves_wands_table():
    rswt = RollTable('d20', {
        Range(1, 1): 'rod_absorption',
        Range(2, 3): 'rod_cancellation',
        Range(4, 4): RollTable('d100', {
            Range(1, 25): 'rod_captivation',
            Range(26, 75): 'rod_lordly_might',
            Range(76, 100): 'rod_resurrection',
        }),
        Range(5, 5): RollTable('d100', {
            Range(1, 50): 'rod_rulership',
            Range(51, 100): 'rod_striking',
        }),
        Range(6, 6): RollTable('d100', {
            Range(1, 50): 'staff_compulsion',
            Range(51, 100): 'staff_healing',
        }),
        Range(7, 7): RollTable('d100', {
            Range(1, 25): 'staff_power',
            Range(26, 100): RollTable('d100', {
                Range(1, 60): 'staff_serpent_python',
                Range(61, 100): 'staff_serpent_viper',
            }),
        }),
        Range(8, 8): RollTable('d100', {
            Range(1, 75): 'staff_withering',
            Range(76, 100): 'staff_wizardry',
        }),
        Range(9, 9): 'wand_detecting_magic',
        Range(10, 10): 'wand_detecting_minerals_metals',
        Range(11, 11): 'wand_detecting_traps_secret_doors',
        Range(12, 12): 'wand_enemy_detection',
        Range(13, 13): RollTable('d100', {
            Range(1, 50): 'wand_fear',
            Range(51, 100): 'wand_fire',
        }),
        Range(14, 14): RollTable('d100', {
            Range(1, 50): 'wand_ice',
            Range(51, 100): 'wand_light',
        }),
        Range(15, 15): RollTable('d100', {
            Range(1, 50): 'wand_illusion',
            Range(51, 100): 'wand_lightning',
        }),
        Range(16, 16): 'wand_magic_missiles',
        Range(17, 17): 'wand_negation',
        Range(18, 18): 'wand_paralysation',
        Range(19, 19): 'wand_polymorphing',
        Range(20, 20): RollTable('d100', {
            Range(1, 50): 'wand_summoning',
            Range(51, 100): 'wand_wonder',
        }),
    })

    # rswl = ['Rod', 'Staff', 'Wand']
    # rsw = [s for s in DbQuery.getTable('Items') if s['Category'] in rswl]
    # rsw_indexed = {s['unique_id']: s for s in rsw}
    # return rsw_indexed[rswt.roll()]
    return rswt.roll()


def scrolls_table():
    st = RollTable('d20', {
        Range(1, 12): RollTable('d20', {
            Range(1, 3): 'scroll_cleric',
            Range(4, 5): 'scroll_druid',
            Range(6, 7): 'scroll_illusionist',
            Range(8, 20): 'scroll_magic_user',
        }),
        Range(13, 19): RollTable('d20', {
            Range(1, 2): 'scroll_warding_acid',
            Range(3, 4): 'scroll_warding_demons',
            Range(5, 6): 'scroll_warding_devils',
            Range(7, 9): RollTable('d20', {
                Range(1, 3): 'scroll_warding_elemental_air',
                Range(4, 6): 'scroll_warding_elemental_earth',
                Range(7, 9): 'scroll_warding_elemental_fire',
                Range(10, 12): 'scroll_warding_elemental_water',
                Range(13, 20): 'scroll_warding_elemental_all',
            }),
            Range(10, 11): RollTable('d20', {
                Range(1, 1): 'scroll_warding_lycanthropes_werebears',
                Range(2, 2): 'scroll_warding_lycanthropes_wereboars',
                Range(3, 4): 'scroll_warding_lycanthropes_wererats',
                Range(5, 5): 'scroll_warding_lycanthropes_weretigers',
                Range(6, 8): 'scroll_warding_lycanthropes_werewolves',
                Range(9, 19): 'scroll_warding_lycanthropes_all_lycanthropes',
                Range(20, 20): 'scroll_warding_lycanthropes_all_shape_changers',
            }),
            Range(12, 14): 'scroll_warding_magic',
            Range(15, 16): 'scroll_warding_petrification',
            Range(17, 18): RollTable('d2', {
                Range(1, 1): 'scroll_warding_possession',
                Range(2, 2): 'scroll_warding_polymorph',
            }),
            Range(19, 20): 'scroll_warding_undead',
        }),
        Range(20, 20): 'scroll_cursed',
    })

    # scrolls = [s for s in DbQuery.getTable('Items') if s['Category'] == 'Scroll']
    # scrolls_indexed = {s['unique_id']: s for s in scrolls}
    # return scrolls_indexed[st.roll()]
    return st.roll()


def swords_table():
    sf = RollTable('d20', {
        Range(1, 1): RollTable('d100', {
            Range(1, 20): 'claymore',
            Range(21, 100): 'bastard',
        }),
        Range(2, 5): 'broad',
        Range(6, 19): 'long',
        Range(20, 20): RollTable('d100', {
            Range(1, 20): 'scimitar',
            Range(21, 100): 'short',
        }),
    })

    sp = RollTable('d20', {
        Range(1, 10): '+1',
        Range(11, 15): '+2',
        Range(16, 16): '+3',
        Range(17, 17): RollTable('d100', {
            Range(1, 65): '+4',
            Range(66, 100): '+5',
        }),
        Range(18, 18): 'cursed',
        Range(19, 20): RollTable('d100', {
            Range(1, 1): 'bleeding_sword',
            Range(2, 6): 'dancing_sword',
            Range(7, 16): 'defender',
            Range(17, 21): 'dragonbane',
            Range(32, 36): 'flaming_blade',
            Range(37, 46): 'giantbane',
            Range(47, 51): 'holy_sword',
            Range(52, 53): 'keenblade',
            Range(54, 69): 'luck_blade',
            Range(70, 74): 'magebane',
            Range(75, 79): 'nine_lives_stealer',
            Range(80, 84): 'trollbane',
            Range(85, 89): 'vampire_blade',
            Range(90, 90): 'vorpal_blade',
            Range(91, 95): 'werebane',
            Range(96, 99): 'wyrmbane',
            Range(100, 100): 'unusual',
        }),
    })

    # swords = [s for s in DbQuery.getTable('Items') if s['Category'] == 'Sword']
    # swords_indexed = {s['unique_id']: s for s in swords}
    # return swords_indexed[f'sword_{sf.roll()}_{sp.roll()}']
    return f'sword_{sf.roll()}_{sp.roll()}'


def miscellaneous_magic_table(ignore_100=False):
    mmt = RollTable('d100', {
        Range(1, 50): mm_table_i(),
        Range(51, 70): mm_table_ii(),
        Range(71, 90): mm_table_iii(),
        Range(91, 99): mm_table_iv(),
        Range(100, 100): 0,
    })

    if ignore_100:
        temp = mmt.roll()
        while temp == 0:
            temp = mmt.roll()
        mmtr = temp
    else:
        mmtr = mmt.roll()

    if mmtr == 0:
        return [miscellaneous_magic_table(ignore_100=True), miscellaneous_magic_table(ignore_100=True)]

    return mmtr


def mm_table_i():
    mmti = RollTable('d100', {
        Range(1, 1): 'incense_meditation',
        Range(2, 2): 'javelin_raptor',
        Range(3, 3): 'thunder_spear',
        Range(4, 4): 'boots_elvenkind',
        Range(5, 5): RollTable('1d9', {
            Range(1, 1): 'candle_invocation_lawful_good',
            Range(2, 2): 'candle_invocation_neutral_good',
            Range(3, 3): 'candle_invocation_chaotic_good',
            Range(4, 4): 'candle_invocation_lawful_neutral',
            Range(5, 5): 'candle_invocation_true_neutral',
            Range(6, 6): 'candle_invocation_chaotic_neutral',
            Range(7, 7): 'candle_invocation_lawful_evil',
            Range(8, 8): 'candle_invocation_neutral_evil',
            Range(9, 9): 'candle_invocation_chaotic_evil',
        }),
        Range(6, 6): 'dust_appearance',
        Range(7, 7): 'dust_disappearance',
        Range(8, 8): 'rope_climbing',
        Range(9, 9): 'scarab_protection',
        Range(10, 10): 'slippers_spider_climbing',
        Range(11, 11): RollTable('d6', {
            Range(1, 4): 'strand_prayer_beads',
            Range(5, 5): 'strand_prayer_beads_lesser',
            Range(6, 6): 'strand_prayer_beads_greater',
        }),
        Range(12, 13): RollTable('d4', {
            Range(1, 1): 'amulet_natural_armour_+1',
            Range(2, 2): 'amulet_natural_armour_+2',
            Range(3, 3): 'amulet_natural_armour_+3',
            Range(4, 4): 'amulet_natural_armour_+4',
        }),
        Range(14, 15): 'blessed_book',
        Range(16, 17): 'brooch_shielding',
        Range(18, 19): 'hat_disguise',
        Range(20, 21): RollTable('d4', {
            Range(1, 1): 'horn_valhalla_silver',
            Range(2, 2): 'horn_valhalla_brass',
            Range(3, 3): 'horn_valhalla_bronze',
            Range(4, 4): 'horn_valhalla_iron',
        }),
        Range(22, 23): 'periapt_proof_against_poison',
        Range(24, 25): 'phylactery_faithfulness',
        Range(26, 27): 'robe_blending',
        Range(28, 30): 'pipes_sewers',
        Range(31, 33): 'restorative_ointment',
        Range(34, 36): 'robe_useful_items',
        Range(37, 39): 'vest_escape',
        Range(40, 42): 'cloak_elvenkind',
        Range(43, 46): 'wings_flying',
        Range(47, 55): RollTable('d100', {
            Range(1, 50): 'cloak_resistance_+1',
            Range(51, 75): 'cloak_resistance_+2',
            Range(76, 90): 'cloak_resistance_+3',
            Range(91, 99): 'cloak_resistance_+4',
            Range(100, 100): 'cloak_resistance_+5',
        }),
        Range(56, 65): RollTable('d6', {
            Range(1, 1): 'feather_token_anchor',
            Range(2, 2): 'feather_token_bird',
            Range(3, 3): 'feather_token_fan',
            Range(4, 4): 'feather_token_swan_boat',
            Range(5, 5): 'feather_token_tree',
            Range(6, 6): 'feather_token_whip',
        }),
        Range(66, 75): RollTable('d9', {
            Range(1, 1): 'figurines_wondrous_power_bronze_griffon',
            Range(2, 2): 'figurines_wondrous_power_ebony_fly',
            Range(3, 3): 'figurines_wondrous_power_golden_lions',
            Range(4, 4): 'figurines_wondrous_power_ivory_goats',
            Range(5, 5): 'figurines_wondrous_power_marble_elephant',
            Range(6, 6): 'figurines_wondrous_power_obsidian_steed',
            Range(7, 7): 'figurines_wondrous_power_onyx_dog',
            Range(8, 8): 'figurines_wondrous_power_serpentine_owl',
            Range(9, 9): 'figurines_wondrous_power_silver_raven',
        }),
        Range(76, 100): RollTable('d100', {
            Range(1, 35): 'bracers_armour_ac_9',
            Range(36, 60): 'bracers_armour_ac_8',
            Range(61, 75): 'bracers_armour_ac_7',
            Range(76, 85): 'bracers_armour_ac_6',
            Range(86, 91): 'bracers_armour_ac_5',
            Range(92, 96): 'bracers_armour_ac_4',
            Range(97, 99): 'bracers_armour_ac_3',
            Range(100, 100): 'bracers_armour_ac_2',
        }),
    })

    # mms = [mi for mi in DbQuery.getTable('Items') if mi['Category'] == 'Misc Magic']
    # mms_indexed = {mm['unique_id']: mm for mm in mms}
    #
    # return mms_indexed[mmti.roll()]
    return mmti.roll()


def mm_table_ii(ignore_over_98=False):
    mmtii = RollTable('d100', {
        Range(1, 1): 'arrow_direction',
        Range(2, 2): 'brazier_commanding_fire_elementals',
        Range(3, 3): 'cape_mountebank',
        Range(4, 4): 'cloak_manta_ray',
        Range(5, 5): 'decanter_endless_water',
        Range(6, 6): 'dust_dryness',
        Range(7, 7): 'elixir_swimming',
        Range(8, 8): 'gloves_arrow_snaring',
        Range(9, 9): 'gloves_swimming_climbing',
        Range(10, 10): 'goggles_night',
        Range(11, 11): 'horseshoes_speed',
        Range(12, 12): 'necklace_adaptation',
        Range(13, 13): 'orb_storms',
        Range(14, 14): 'periapt_health',
        Range(15, 15): 'pipes_haunting',
        Range(16, 16): 'ring_gates',
        Range(17, 17): 'robe_bones',
        Range(18, 18): 'unguent_timelessness',
        Range(19, 20): 'universal_solvent',
        Range(21, 22): 'amulet_proof_against_detection_location',
        Range(23, 24): 'boots_speed',
        Range(25, 26): 'boots_striding_springing',
        Range(27, 28): 'bracers_archery_lesser',
        Range(29, 30): 'candle_truth',
        Range(31, 32): 'cloak_displacement_minor',
        Range(33, 34): 'cloak_bat',
        Range(35, 36): 'dark_skull',
        Range(37, 38): 'dust_tracelessness',
        Range(39, 40): 'elixir_truth',
        Range(41, 42): 'elixir_vision',
        Range(43, 44): 'glove_storing',
        Range(45, 46): 'horn_tritons',
        Range(47, 48): RollTable('d7', {
            Range(1, 1): 'necklace_fireballs_type_i',
            Range(2, 2): 'necklace_fireballs_type_ii',
            Range(3, 3): 'necklace_fireballs_type_iii',
            Range(4, 4): 'necklace_fireballs_type_iv',
            Range(5, 5): 'necklace_fireballs_type_v',
            Range(6, 6): 'necklace_fireballs_type_vi',
            Range(7, 7): 'necklace_fireballs_type_vii',
        }),
        Range(49, 50): 'periapt_wound_closure',
        Range(51, 52): 'phylactery_undead_turning',
        Range(53, 54): 'rope_entanglement',
        Range(55, 56): RollTable('d2', {
            Range(1, 1): 'stone_horse_draft',
            Range(2, 2): 'stone_horse_heavy_war'
        }),
        Range(57, 58): 'stone_alarm',
        Range(59, 60): 'sustaining_spoon',
        Range(61, 62): 'wind_fan',
        Range(63, 65): RollTable('d4', {
            Range(1, 1): 'bag_holding_type_i',
            Range(2, 2): 'bag_holding_type_ii',
            Range(3, 3): 'bag_holding_type_iii',
            Range(4, 4): 'bag_holding_type_iv',
        }),
        Range(66, 68): 'boots_levitation',
        Range(69, 71): 'bottle_air',
        Range(72, 74): 'broom_flying',
        Range(75, 77): RollTable('d100', {
            Range(1, 75): 'crystal_ball',
            Range(75, 85): 'crystal_ball_clairaudience',
            Range(86, 90): 'crystal_ball_see_invisibility',
            Range(91, 95): 'crystal_ball_esp',
            Range(96, 100): 'crystal_ball_true_seeing',
        }),
        Range(78, 80): 'elixir_fire_breath',
        Range(81, 83): 'elixir_hiding',
        Range(84, 86): 'handy_haversack',
        Range(87, 89): 'harp_charming',
        Range(90, 92): 'helm_comprehend_languages_read_magic',
        Range(93, 95): 'helm_underwater_action',
        Range(96, 98): 'horn_fog',
        Range(99, 99): 0,
        Range(100, 100): 1,
    })

    if ignore_over_98:
        tmp = mmtii.roll()
        while type(tmp).__name__ == 'int':
            tmp = mmtii.roll()
        roll = mmtii.roll()
    else:
        roll = mmtii.roll()

    if roll == 0:
        return [mm_table_i(), mm_table_i()]
    elif roll == 1:
        return [mm_table_ii(ignore_over_98=True), mm_table_ii(ignore_over_98=True)]

    # mms = [mi for mi in DbQuery.getTable('Items') if mi['Category'] == 'Misc Magic']
    # mms_indexed = {mm['unique_id']: mm for mm in mms}
    #
    # return mms_indexed[roll]
    return roll


def mm_table_iii(ignore_over_65=False):
    mmtiii = RollTable('d100', {
        Range(1, 1): 'ahmeks_copious_coin_purse',
        Range(2, 2): 'alchemy_jug',
        Range(3, 3): 'amulet_health',
        Range(4, 4): 'amulet_planes',
        Range(5, 5): 'apparatus_lobster',
        Range(6, 6): RollTable('d6', {
            Range(1, 2): 'bag_tricks_grey',
            Range(3, 4): 'bag_tricks_rust',
            Range(5, 6): 'bag_tricks_tan',
        }),
        Range(7, 7): 'bead_force',
        Range(8, 8): 'blemish_blotter',
        Range(9, 9): 'boots_winterlands',
        Range(10, 10): 'bowl_commanding_water_elementals',
        Range(11, 11): 'bracelet_friends',
        Range(12, 12): 'bracers_archery_greater',
        Range(13, 13): RollTable('d6', {
            Range(1, 2): 'carpet_flying_5_5',
            Range(3, 4): 'carpet_flying_5_10',
            Range(5, 6): 'carpet_flying_10_10',
        }),
        Range(14, 14): 'censer_controlling_air_elementals',
        Range(15, 15): 'chime_interruption',
        Range(16, 16): 'chime_opening',
        Range(17, 17): 'circlet_blasting_minor',
        Range(18, 18): 'circlet_persuasion',
        Range(19, 19): 'cloak_aetherealness',
        Range(20, 20): 'cloak_arachnida',
        Range(21, 21): 'cloak_charisma',
        Range(22, 22): 'cloak_displacement_major',
        Range(23, 23): 'cube_force',
        Range(24, 24): 'cube_frost_resistance',
        Range(25, 25): 'cubic_gate',
        Range(26, 26): 'deck_illusions',
        Range(27, 27): 'dimensional_shackles',
        Range(28, 28): 'drums_panic',
        Range(29, 29): 'dust_illusion',
        Range(30, 30): 'efficient_quiver',
        Range(31, 31): RollTable('d4', {
            Range(1, 1): 'elemental_gem_air',
            Range(2, 2): 'elemental_gem_earth',
            Range(3, 3): 'elemental_gem_fire',
            Range(4, 4): 'elemental_gem_water',
        }),
        Range(32, 32): 'eyes_eagle',
        Range(33, 33): RollTable('d18', {
            Range(1, 1): 'gauntlets_ogre_power_+1_to_hit_+1_damage',
            Range(2, 2): 'gauntlets_ogre_power_+1_to_hit_+2_damage',
            Range(3, 3): 'gauntlets_ogre_power_+1_to_hit_+3_damage',
            Range(4, 4): 'gauntlets_ogre_power_+1_to_hit_+4_damage',
            Range(5, 5): 'gauntlets_ogre_power_+1_to_hit_+5_damage',
            Range(6, 6): 'gauntlets_ogre_power_+1_to_hit_+6_damage',
            Range(7, 7): 'gauntlets_ogre_power_+2_to_hit_+1_damage',
            Range(8, 8): 'gauntlets_ogre_power_+2_to_hit_+2_damage',
            Range(9, 9): 'gauntlets_ogre_power_+2_to_hit_+3_damage',
            Range(10, 10): 'gauntlets_ogre_power_+2_to_hit_+4_damage',
            Range(11, 11): 'gauntlets_ogre_power_+2_to_hit_+5_damage',
            Range(12, 12): 'gauntlets_ogre_power_+2_to_hit_+6_damage',
            Range(13, 13): 'gauntlets_ogre_power_+3_to_hit_+1_damage',
            Range(14, 14): 'gauntlets_ogre_power_+3_to_hit_+2_damage',
            Range(15, 15): 'gauntlets_ogre_power_+3_to_hit_+3_damage',
            Range(16, 16): 'gauntlets_ogre_power_+3_to_hit_+4_damage',
            Range(17, 17): 'gauntlets_ogre_power_+3_to_hit_+5_damage',
            Range(18, 18): 'gauntlets_ogre_power_+3_to_hit_+6_damage',
        }),
        Range(34, 34): 'gauntlet_rust',
        Range(35, 35): 'gloves_dexterity',
        Range(36, 36): 'goggles_minute_seeing',
        Range(37, 37): 'headband_intellect',
        Range(38, 38): 'helm_telepathy',
        Range(39, 39): 'horn_goodness_evil',
        Range(40, 40): 'horseshoes_zephyr',
        Range(41, 41): 'instant_fortress',
        Range(42, 42): 'iron_bands_binding',
        Range(43, 43): 'iron_flask',
        Range(44, 44): 'lantern_revealing',
        Range(45, 45): 'mantle_faith',
        Range(46, 46): 'mantle_magic_resistance',
        Range(47, 47): 'marvellous_pigments',
        Range(48, 48): 'mask_skull',
        Range(49, 49): 'medallion_thoughts',
        Range(50, 50): pearl_power_roll,
        Range(51, 51): 'pearl_sirines',
        Range(52, 52): 'periapt_wisdom',
        Range(53, 53): 'pipes_pain',
        Range(54, 54): 'pipes_sounding',
        Range(55, 55): 'plentiful_vessel',
        Range(56, 56): 'robe_stars',
        Range(57, 57): 'scabbard_keen_edges',
        Range(58, 58): 'scarab_golem_bane',
        Range(59, 59): 'silversheen',
        Range(60, 60): 'sovereign_glue',
        Range(61, 61): 'stone_controlling_earth_elementals',
        Range(62, 62): 'stone_good_luck',
        Range(63, 63): 'stone_salve',
        Range(64, 64): 'vestment_druids',
        Range(65, 65): 'well_many_worlds',
        Range(66, 75): 0,
        Range(76, 85): 1,
        Range(86, 95): 2,
        Range(96, 99): 3,
        Range(100, 100): 4,
    })

    if ignore_over_65:
        tmp = mmtiii.roll()
        while type(tmp).__name__ == 'int':
            tmp = mmtiii.roll()
        roll = tmp
    else:
        roll = mmtiii.roll()

    if roll == 0:
        return [mm_table_i(), mm_table_i()]
    elif roll == 1:
        return [mm_table_i(), mm_table_ii()]
    elif roll == 2:
        return [mm_table_ii(), mm_table_ii()]
    elif roll == 3:
        return [mm_table_ii(), mm_table_iii(ignore_over_65=True)]
    elif roll == 4:
        return [mm_table_iii(ignore_over_65=True), mm_table_iii(ignore_over_65=True)]

    # mms = [mi for mi in DbQuery.getTable('Items') if mi['Category'] == 'Misc Magic']
    # mms_indexed = {mm['unique_id']: mm for mm in mms}
    #
    # return mms_indexed[roll]
    return roll


def pearl_power_roll():

    def roll_two_levels():
        roll1 = Dice.rollString('d6')
        roll2 = Dice.rollString('d6')
        while roll1 == roll2:
            roll2 = Dice.rollString('d6')

        suffix = ['th', 'st', 'nd', 'rd'] + ['th'] * 3

        ord1 = str(roll1) + suffix[roll1]
        ord2 = str(roll2) + suffix[roll2]

        if roll1 < roll2:
            first_level = ord1
            second_level = ord2
        else:
            first_level = ord2
            second_level = ord1

        return f'pearl_power_{first_level}_{second_level}'

    ppr = RollTable('d6', {
        Range(1, 1): 'pearl_power_1st',
        Range(2, 2): 'pearl_power_2nd',
        Range(3, 3): 'pearl_power_3rd',
        Range(4, 4): 'pearl_power_4th',
        Range(5, 5): 'pearl_power_5th',
        Range(6, 6): RollTable('d8', {
            Range(1, 1): 'pearl_power_1st',
            Range(2, 2): 'pearl_power_2nd',
            Range(3, 3): 'pearl_power_3rd',
            Range(4, 4): 'pearl_power_4th',
            Range(5, 5): 'pearl_power_5th',
            Range(6, 6): 'pearl_power_6th',
            Range(7, 7): 'pearl_power_7th',
            Range(8, 8): RollTable('d10', {
                Range(1, 1): 'pearl_power_1st',
                Range(2, 2): 'pearl_power_2nd',
                Range(3, 3): 'pearl_power_3rd',
                Range(4, 4): 'pearl_power_4th',
                Range(5, 5): 'pearl_power_5th',
                Range(6, 6): 'pearl_power_6th',
                Range(7, 7): 'pearl_power_7th',
                Range(8, 8): 'pearl_power_8th',
                Range(9, 9): 'pearl_power_9th',
                Range(10, 10): roll_two_levels,
            }),
        }),
    })

    return ppr.roll()


def belt_giant_strength_roll():
    to_hit_bonus = Dice.rollString('1d4+2')
    damage_bonus = Dice.rollString('1d6+6')

    return f'belt_giant_strength_+{to_hit_bonus}_+{damage_bonus}'


def mm_table_iv():
    mmtiv = RollTable('d100', {
        Range(1, 2): 'afreeti_bottle',
        Range(3, 4): 'amulet_life_protection',
        Range(5, 5): 'amulet_mighty_fists',
        Range(6, 7): 'belt_dwarfkind',
        Range(8, 9): belt_giant_strength_roll,
        Range(10, 11): 'boat_folding',
        Range(12, 13): 'boots_teleportation',
        Range(14, 14): 'boots_winged',
        Range(15, 16): 'brooch_instigation',
        Range(17, 18): 'circlet_blasting_major',
        Range(19, 20): 'eversmoking_bottle',
        Range(21, 22): 'eyes_charming',
        Range(23, 24): 'eyes_doom',
        Range(25, 26): 'eyes_petrifaction',
        Range(27, 28): 'gem_brightness',
        Range(29, 30): 'gem_seeing',
        Range(31, 32): RollTable('d8', {
            Range(1, 1): 'golem_manual_clay_cleric',
            Range(2, 2): 'golem_manual_flesh_cleric',
            Range(3, 3): 'golem_manual_iron_cleric',
            Range(4, 4): 'golem_manual_stone_cleric',
            Range(5, 5): 'golem_manual_clay_magic_user',
            Range(6, 6): 'golem_manual_flesh_magic_user',
            Range(7, 7): 'golem_manual_iron_magic_user',
            Range(8, 8): 'golem_manual_stone_magic_user',
        }),
        Range(33, 34): 'helm_brilliance',
        Range(35, 36): 'helm_teleportation',
        Range(37, 38): 'horn_blasting',
        Range(39, 40): 'horn_blasting_greater',
        Range(41, 42): ioun_stones_table,
        Range(43, 44): 'lyre_building',
        Range(45, 46): 'manual_bodily_health',
        Range(47, 48): 'manual_gainful_exercise',
        Range(49, 50): 'manual_quickness_action',
        Range(51, 52): 'mattock_titans',
        Range(53, 54): 'maul_titans',
        Range(55, 56): 'mirror_life_trapping',
        Range(57, 58): 'mirror_mental_prowess',
        Range(59, 60): 'mirror_opposition',
        Range(61, 62): 'oil_famishing',
        Range(63, 64): 'portable_hole',
        Range(65, 66): 'robe_eyes',
        Range(67, 68): 'robe_scintillating_colours',
        Range(69, 70): RollTable('d100', {
            Range(1, 45): 'robe_archmagi_white',
            Range(46, 75): 'robe_archmagi_grey',
            Range(76, 100): 'robe_archmagi_black',
        }),
        Range(71, 72): RollTable('d9', {
            Range(1, 1): 'sagacious_volume_assassin',
            Range(2, 2): 'sagacious_volume_cleric',
            Range(3, 3): 'sagacious_volume_druid',
            Range(4, 4): 'sagacious_volume_fighter',
            Range(5, 5): 'sagacious_volume_illusionist',
            Range(6, 6): 'sagacious_volume_magic_user',
            Range(7, 7): 'sagacious_volume_paladin',
            Range(8, 8): 'sagacious_volume_ranger',
            Range(9, 9): 'sagacious_volume_thief',
        }),
        Range(73, 74): 'shrouds_disintegration',
        Range(75, 76): 'tome_clear_thought',
        Range(77, 78): 'tome_leadership_influence',
        Range(79, 80): 'tome_understanding',
        Range(81, 85): lambda: [mm_table_iii(), mm_table_iii()],
        Range(86, 90): lambda: [mm_table_iv(), miscellaneous_weapons_table()],
        Range(91, 95): lambda: [mm_table_iv(), swords_table()],
        Range(96, 100): cursed_items_table,
    })

    return mmtiv.roll()


def ioun_stones_table(ignore_over_96=False):
    ist = RollTable('d100', {
        Range(1, 6): 'ioun_stones_clear',
        Range(7, 12): 'ioun_stones_dusty_rose',
        Range(13, 18): 'ioun_stones_deep_red',
        Range(19, 24): 'ioun_stones_incandescent_blue',
        Range(25, 30): 'ioun_stones_pale_blue',
        Range(31, 36): 'ioun_stones_pink',
        Range(37, 42): 'ioun_stones_pink_green',
        Range(43, 48): 'ioun_stones_scarlet_blue',
        Range(49, 54): 'ioun_stones_dark_blue',
        Range(55, 60): 'ioun_stones_vibrant_purple',
        Range(61, 66): 'ioun_stones_iridescent',
        Range(67, 72): 'ioun_stones_pale_lavender',
        Range(73, 77): 'ioun_stones_pearly_white',
        Range(78, 83): 'ioun_stones_pale_green',
        Range(84, 89): 'ioun_stones_orange',
        Range(90, 96): 'ioun_stones_lavender_green',
        Range(97, 99): 0,
        Range(100, 100): 1,
    })

    if ignore_over_96:
        tmp = ist.roll()
        while type(tmp).__name__ == 'int':
            tmp = ist.roll()
        roll = tmp
    else:
        roll = ist.roll()

    if roll == 0:
        return [ioun_stones_table(ignore_over_96=True), ioun_stones_table(ignore_over_96=True)]
    elif roll == 1:
        return [ioun_stones_table(ignore_over_96=True),
                ioun_stones_table(ignore_over_96=True),
                ioun_stones_table(ignore_over_96=True)]

    return roll


def cursed_items_table():
    cit = RollTable('d100', {
        Range(1, 5): 'amulet_inescapable_location',
        Range(6, 7): 'armour_arrow_attraction',
        Range(8, 10): 'armour_rage',
        Range(11, 13): 'bag_devouring',
        Range(14, 17): 'boots_dancing',
        Range(18, 22): 'bracers_defencelessness',
        Range(23, 23): 'broom_animated_attack',
        Range(24, 24): 'cloak_poisonousness',
        Range(25, 25): 'crystal_hypnosis_ball',
        Range(26, 27): 'dust_sneezing_choking',
        Range(28, 33): 'flask_curses',
        Range(34, 38): RollTable('d2', {
            Range(1, 1): 'gauntlets_fumbling_heavy',
            Range(2, 2): 'gauntlets_fumbling_light',
        }),
        Range(39, 39): 'helm_opposite_alignment',
        Range(40, 44): 'incense_obsession',
        Range(45, 49): 'mace_blood',
        Range(50, 52): 'medallion_thought_projection',
        Range(53, 53): 'necklace_strangulation',
        Range(54, 55): 'net_snaring',
        Range(56, 58): 'periapt_foul_rotting',
        Range(59, 63): 'potion_poison',
        Range(64, 73): 'ring_clumsiness',
        Range(74, 75): 'robe_powerlessness',
        Range(76, 80): 'robe_vermin',
        Range(81, 81): 'scarab_death',
        Range(82, 86): 'spear_cursed_backbiter',
        Range(87, 91): 'stone_weight_loadstone',
        Range(92, 96): 'sword_-2_cursed',
        Range(97, 99): 'sword_berserker_+2',
        Range(100, 100): 'vacuous_grimoire',
    })

    return cit.roll()
