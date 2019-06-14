import re
import DbQuery
import Dice

base_pattern = r'(\d+d\d+[+-x×]?[\d,]*|\d+) ?'
percent_pattern = r' ?(?:\((\d+)%.*\))?'
cp_pattern = re.compile(base_pattern + 'cp' + percent_pattern)
sp_pattern = re.compile(base_pattern + 'sp' + percent_pattern)
ep_pattern = re.compile(base_pattern + 'ep' + percent_pattern)
gp_pattern = re.compile(base_pattern + 'gp' + percent_pattern)
pp_pattern = re.compile(base_pattern + 'pp' + percent_pattern)
gems_pattern = re.compile(base_pattern + 'gems' + percent_pattern)
jewellery_pattern = re.compile(base_pattern + 'jewellery' + percent_pattern)
potions_pattern = re.compile(base_pattern + 'potions' + percent_pattern)

gemstone_desc_levels = [
        'Ornamental', 'Semi-Precious', 'Fancy',
        'Precious', 'Gem', 'Jewel'
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

    potions_match = potions_pattern.findall(t)
    potions = [potions_table() for _ in range(1, sum(get_treasure_list(potions_match)) + 1)]

    return {
        'cp': sum(get_treasure_list(cp_match)),
        'sp': sum(get_treasure_list(sp_match)),
        'ep': sum(get_treasure_list(ep_match)),
        'gp': sum(get_treasure_list(gp_match)),
        'pp': sum(get_treasure_list(pp_match)),
        'gems': gems,
        'jewellery': jewellery,

        'potions': potions,
    }


def gemstone_table(description=None):
    if description:
        return alter_gemstone(description)
    else:
        percent_roll = Dice.randomInt(1, 100)
        if 1 <= percent_roll <= 30:
            return alter_gemstone('Ornamental')
        elif 31 <= percent_roll <= 55:
            return alter_gemstone('Semi-Precious')
        elif 56 <= percent_roll <= 75:
            return alter_gemstone('Fancy')
        elif 76 <= percent_roll <= 90:
            return alter_gemstone('Precious')
        elif 91 <= percent_roll <= 99:
            return alter_gemstone('Gem')
        else:
            return alter_gemstone('Jewel')


def alter_gemstone(description):
    alter_roll = Dice.rollString(alter_roll_dice_string)
    return alter_table(alter_roll, gemstone_desc_levels.index(description))


def alter_table(alter_roll, desc_level, ignore_list=()):
    if alter_roll in ignore_list:
        return alter_table(Dice.rollString(alter_roll_dice_string), desc_level, ignore_list)
    gemstones = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Gemstone']
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
        gemstone_candidates = [g for g in gemstones if g['Subcategory'] == gemstone_desc_levels[desc_level]]
        gemstone = gemstone_candidates[Dice.randomInt(0, len(gemstone_candidates) - 1)]
        if value is None:
            value = Dice.rollString(gemstone['Value'])
        if alter_roll == 2 or alter_roll == 3:
            value *= alter_roll
        elif alter_roll == 9:
            value -= value*Dice.rollString('1d4x10')/100
        gemstone['Actual Value'] = value
        return gemstone


def jewellery_table():
    jewellery = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Jewellery']
    jewellery_indexed = {j['unique_id']: j for j in jewellery}
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
                    j = jewellery_indexed[item_id]
                    j['Actual Value'] = Dice.rollString(j['Value'])
                    return j


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
    magic_items_roll = Dice.rollString('d20')
    if 1 <= magic_items_roll <= 3:
        return armour_shield_table()
    elif 4 <= magic_items_roll <= 6:
        return miscellaneous_magic_table()
    elif 7 <= magic_items_roll <= 9:
        return miscellaneous_weapons_table()
    elif 10 <= magic_items_roll <= 13:
        return potions_table()
    elif magic_items_roll == 14:
        return rings_table()
    elif magic_items_roll == 15:
        return rods_staves_wands_table()
    elif 16 <= magic_items_roll <= 18:
        return scrolls_table()
    else:
        return swords_table()


def armour_shield_table():
    armour = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Armour']
    armour_indexed = {a['unique_id']: a for a in armour}
    first_roll = Dice.rollString('d20')
    second_roll = Dice.randomInt(1, 100)
    if first_roll == 1:
        armour_type = 'banded'
    elif 2 <= first_roll <= 4:
        if 1 <= second_roll <= 90:
            armour_type = 'chain'
        else:
            armour_type = 'elfin_chain'
    elif 5 <= first_roll <= 6:
        armour_type = 'leather'
    elif 7 <= first_roll <= 9:
        armour_type = 'plate'
    elif first_roll == 10:
        armour_type = 'ring'
    elif 11 <= first_roll <= 12:
        armour_type = 'splint'
    elif 13 <= first_roll <= 14:
        armour_type = 'scale'
    elif first_roll == 15:
        armour_type = 'studded'
    else:
        armour_type = 'medium'

    power_roll = Dice.rollString('d20')
    second_power_roll = Dice.randomInt(1, 100)
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
        return special_armour_table(armour_indexed)

    if armour_type == 'medium':
        id_prefix = 'shield'
    else:
        id_prefix = 'armour'
    armour_id = f'{id_prefix}_{armour_type}_{power}'
    return armour_indexed[armour_id]


def special_armour_table(armour_indexed=None):
    if armour_indexed is None:
        armour = [i for i in DbQuery.getTable('Items') if i['Category'] == 'Armour']
        armour_indexed = {a['unique_id']: a for a in armour}
    roll = Dice.rollString('1d2')
    if roll == 1:
        return armour_indexed['shield_large_+1_missile_deflector']
    else:
        return armour_indexed['armor_plate_mail_of_aethereality_16_20_charges_remaining']


def miscellaneous_magic_table():
    pass


def miscellaneous_weapons_table():
    weapons = [w for w in DbQuery.getTable('Items') if w['Category'] == 'Weapon']
    weapons_indexed = {w['unique_id']: w for w in weapons}
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
        return special_miscellaneous_weapons_table(weapons_indexed)

    weapon_id = f'{weapon_type}_{power}'
    return weapons_indexed[weapon_id]


def special_miscellaneous_weapons_table(weapons_indexed=None):
    if weapons_indexed is None:
        weapons = [w for w in DbQuery.getTable('Items') if w['Category'] == 'Weapon']
        weapons_indexed = {w['unique_id']: w for w in weapons}
    first_roll = Dice.rollString('d100')
    second_roll = Dice.rollString('d2')
    if 1 <= first_roll <= 5:
        return weapons_indexed['arrow_of_slaying']
    elif 6 <= first_roll <= 15:
        return weapons_indexed['axe_of_hurling']
    elif 16 <= first_roll <= 30:
        if second_roll == 1:
            return weapons_indexed['crossbow_of_accuracy_heavy']
        else:
            return weapons_indexed['crossbow_of_accuracy_light']
    elif 31 <= first_roll <= 40:
        if second_roll == 1:
            return weapons_indexed['crossbow_of_range_heavy']
        else:
            return weapons_indexed['crossbow_of_range_light']
    elif 41 <= first_roll <= 50:
        if second_roll == 1:
            return weapons_indexed['crossbow_of_speed_heavy']
        else:
            return weapons_indexed['crossbow_of_speed_light']
    elif 51 <= first_roll <= 60:
        return weapons_indexed['dagger_of_venom']
    elif 61 <= first_roll <= 70:
        if second_roll == 1:
            return weapons_indexed['hammer_of_the_dwarfs_war_heavy']
        else:
            return weapons_indexed['hammer_of_the_dwarfs_war_light']
    elif 71 <= first_roll <= 75:
        if second_roll == 1:
            return weapons_indexed['mace_holy_heavy']
        else:
            return weapons_indexed['mace_holy_light']
    elif 76 <= first_roll <= 85:
        return weapons_indexed['sling_of_the_halfling']
    else:
        return weapons_indexed['trident_fork']


def potions_table():
    potions = [p for p in DbQuery.getTable('Items') if p['Category'] == 'Potion']
    potions_indexed = {p['unique_id']: p for p in potions}

    first_roll = Dice.rollString('d20')
    second_roll = Dice.rollString('d100')

    if first_roll == 1:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_animal_control']
        else:
            return potions_indexed['potion_clairaudience']
    elif first_roll == 2:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_clairvoyance']
        else:
            return potions_indexed['potion_climbing']
    elif first_roll == 3:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_cursed']
        else:
            return potions_indexed['potion_delusion']
    elif first_roll == 4:
        if 1 <= second_roll <= 65:
            return potions_indexed['potion_diminution']
        else:
            dragon_roll = Dice.rollString('d20')
            if 1 <= dragon_roll <= 2:
                return potions_indexed['potion_black_dragon_control']
            elif 3 <= dragon_roll <= 4:
                return potions_indexed['potion_blue_dragon_control']
            elif 5 <= dragon_roll <= 6:
                return potions_indexed['potion_brass_dragon_control']
            elif dragon_roll == 7:
                return potions_indexed['potion_bronze_dragon_control']
            elif 8 <= dragon_roll <= 9:
                return potions_indexed['potion_copper_dragon_control']
            elif dragon_roll == 10:
                return potions_indexed['potion_gold_dragon_control']
            elif 11 <= dragon_roll <= 13:
                return potions_indexed['potion_green_dragon_control']
            elif dragon_roll == 14:
                return potions_indexed['potion_red_dragon_control']
            elif dragon_roll == 15:
                return potions_indexed['potion_silver_dragon_control']
            elif 16 <= dragon_roll <= 17:
                return potions_indexed['potion_white_dragon_control']
            elif 18 <= dragon_roll <= 19:
                return potions_indexed['potion_evil_dragon_control']
            else:
                return potions_indexed['potion_good_dragon_control']
    elif first_roll == 5:
        return potions_indexed['potion_esp']
    elif first_roll == 6:
        if 1 <= second_roll <= 35:
            return potions_indexed['potion_extra_healing']
        else:
            return potions_indexed['potion_fire_resistance']
    elif first_roll == 7:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_flying']
        else:
            return potions_indexed['potion_gaseous_form']
    elif first_roll == 8:
        giant_roll = Dice.rollString('d20')
        if 1 <= second_roll <= 50:
            if 1 <= giant_roll <= 2:
                return potions_indexed['potion_cloud_giant_control']
            elif 3 <= giant_roll <= 6:
                return potions_indexed['potion_fire_giant_control']
            elif 7 <= giant_roll <= 10:
                return potions_indexed['potion_frost_giant_control']
            elif 11 <= giant_roll <= 15:
                return potions_indexed['potion_hill_giant_control']
            elif 16 <= giant_roll <= 19:
                return potions_indexed['potion_stone_giant_control']
            else:
                return potions_indexed['potion_storm_giant_control']
        else:
            if 1 <= giant_roll <= 6:
                return potions_indexed['potion_hill_giant_strength']
            elif 7 <= giant_roll <= 10:
                return potions_indexed['potion_stone_giant_strength']
            elif 11 <= giant_roll <= 14:
                return potions_indexed['potion_frost_giant_strength']
            elif 15 <= giant_roll <= 17:
                return potions_indexed['potion_fire_giant_strength']
            elif 18 <= giant_roll <= 19:
                return potions_indexed['potion_cloud_giant_strength']
            else:
                return potions_indexed['potion_storm_giant_strength']
    elif first_roll == 9:
        return potions_indexed['potion_growth']
    elif first_roll == 10:
        return potions_indexed['potion_healing']
    elif first_roll == 11:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_heroism']
        else:
            human_roll = Dice.rollString('d20')
            if 1 <= human_roll <= 2:
                return potions_indexed['potion_human_control_dwarfs']
            elif 3 <= human_roll <= 4:
                return potions_indexed['potion_human_control_elves']
            elif human_roll == 5:
                return potions_indexed['potion_human_control_elves_humans']
            elif 6 <= human_roll <= 7:
                return potions_indexed['potion_human_control_gnomes']
            elif 8 <= human_roll <= 9:
                return potions_indexed['potion_human_control_halflings']
            elif 10 <= human_roll <= 11:
                return potions_indexed['potion_human_control_half_orcs']
            elif 12 <= human_roll <= 17:
                return potions_indexed['potion_human_control_humans']
            else:
                return potions_indexed['potion_human_control_other']
    elif first_roll == 12:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_invisibility']
        else:
            return potions_indexed['potion_invulnerability']
    elif first_roll == 13:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_levitation']
        else:
            return potions_indexed['potion_longevity']
    elif first_roll == 14:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_oil_aetherealness']
        else:
            return potions_indexed['potion_oil_slipperiness']
    elif first_roll == 15:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_philtre_love']
        else:
            return potions_indexed['potion_philtre_persuasiveness']
    elif first_roll == 16:
        if 1 <= second_roll <= 65:
            return potions_indexed['potion_plant_control']
        else:
            return potions_indexed['potion_polymorph']
    elif first_roll == 17:
        if 1 <= second_roll <= 50:
            return potions_indexed['potion_speed']
        else:
            return potions_indexed['potion_super_heroism']
    elif first_roll == 18:
        return potions_indexed['potion_sweet_water']
    elif first_roll == 19:
        if 1 <= second_roll <= 75:
            return potions_indexed['potion_treasure_finding']
        else:
            undead_roll = Dice.rollString('d10')
            if undead_roll == 1:
                return potions_indexed['potion_undead_control_ghasts']
            elif undead_roll == 2:
                return potions_indexed['potion_undead_control_ghosts']
            elif undead_roll == 3:
                return potions_indexed['potion_undead_control_ghouls']
            elif undead_roll == 4:
                return potions_indexed['potion_undead_control_shadows']
            elif undead_roll == 5:
                return potions_indexed['potion_undead_control_skeletons']
            elif undead_roll == 6:
                return potions_indexed['potion_undead_control_spectres']
            elif undead_roll == 7:
                return potions_indexed['potion_undead_control_vampires']
            elif undead_roll == 8:
                return potions_indexed['potion_undead_control_wights']
            elif undead_roll == 9:
                return potions_indexed['potion_undead_control_wraiths']
            elif undead_roll == 10:
                return potions_indexed['potion_undead_control_zombies']
    else:
        return potions_indexed['potion_water_breathing']


def rings_table():
    pass


def rods_staves_wands_table():
    pass


def scrolls_table():
    pass


def swords_table():
    pass
