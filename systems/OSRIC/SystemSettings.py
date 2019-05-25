# -*- coding: utf-8 -*-
from decimal import Decimal
from string import Template
import DbQuery

systemName = 'Osric'
subSystemName = 'OSRIC'
hasSeparateRacesAndClasses = True
attributes = [('STR', 'Strength', '3d6'),
              ('INT', 'Intelligence', '3d6'),
              ('WIS', 'Wisdom', '3d6'),
              ('DEX', 'Dexderity', '3d6'),
              ('CON', 'Constitution', '3d6'),
              ('CHA', 'Charisma', '3d6'),
              # ('COM','Comliness', '3d6'),
]
life = ['HP', ]
alignment = ['Lawful Good', 'Neutral Good', 'Chaotic Good', 'Lawful Neutral', 'True Neutral', 'Chaotic Neutral', 'Lawful Evil', 'Neutral Evil', 'Chaotic Evil']
gender = ['Male', 'Female', 'NA']
economy = {
    'gp': 1,
    'pp': 5,
    'ep': .5,
    'sp': .1,
    'cp': .01
}
restrictive_races = ['dwarf', 'half_orc']

bonuses = {
    'STR': [(3, '-3', '-1', '-35', '1', '0'),
            (5, '-2', '-1', '-25', '1', '0'),
            (7, '-1', '0', '-15', '1', '0'),
            (9, '0', '0', '0', '1-2', '1'),
            (11, '0', '0', '0', '1-2', '2'),
            (13, '0', '0', '+10', '1-2', '4'),
            (15, '0', '0', '+20', '1-2', '7'),
            (16, '0', '+1', '+35', '1-3', '10'),
            (17, '+1', '+1', '+50', '1-3', '13'),
            (18, '+1', '+2', '+75', '1-3', '16'),
            (18.5, '+1', '+3', '+100', '1-3', '20'),
            (18.75, '+2', '+3', '+125', '1-4', '25'),
            (18.9, '+2', '+4', '+150', '1-4', '30'),
            (18.99, '+2', '+5', '+200', '1-4(1 in 6)', '35'),
            (19, '+3', '+6', '+300', '1-5(1 in 6)', '40'), ],
    'INT': [(3, '0', '-', '-'),
            (4, '0', '-', '-'),
            (5, '0', '-', '-'),
            (6, '0', '-', '-'),
            (7, '0', '-', '-'),
            (8, '1', '-', '-'),
            (9, '1', '35', '4/6'),
            (10, '2', '45', '5/7'),
            (11, '2', '45', '5/7'),
            (12, '3', '45', '5/7'),
            (13, '3', '55', '6/9'),
            (14, '4', '55', '6/9'),
            (15, '4', '65', '7/11'),
            (16, '5', '65', '7/11'),
            (17, '6', '75', '8/14'),
            (18, '7', '85', '9/18'),
            (19, '8', '90', '10/22'), ],
    'WIS': [(3, '-3', '0', '45'),
            (4, '-2', '0', '40'),
            (5, '-1', '0', '35'),
            (6, '-1', '0', '30'),
            (7, '-1', '0', '25'),
            (8, '0', '0', '20'),
            (9, '0', '0', '15'),
            (10, '0', '0', '10'),
            (11, '0', '0', '5'),
            (12, '0', '0', '1'),
            (13, '0', '1', '0'),
            (14, '0', '2', '0'),
            (15, '+1', '2/1', '0'),
            (16, '+2', '2/2', '0'),
            (17, '+3', '2/2/1', '0'),
            (18, '+4', '2/2/1/1', '0'),
            (19, '+5', '3/2/1/1', '0'), ],
    'DEX': [(3, '-3', '-3', '+4'),
            (4, '-2', '-2', '+3'),
            (5, '-1', '-1', '+2'),
            (6, '0', '0', '+1'),
            (7, '0', '0', '0'),
            (8, '0', '0', '0'),
            (9, '0', '0', '0'),
            (10, '0', '0', '0'),
            (11, '0', '0', '0'),
            (12, '0', '0', '0'),
            (13, '0', '0', '0'),
            (14, '0', '0', '0'),
            (15, '0', '0', '-1'),
            (16, '+1', '+1', '-2'),
            (17, '+2', '+2', '-3'),
            (18, '+3', '+3', '-4'),
            (19, '+3', '+3', '-4'), ],
    'CON': [(3, '-2', '40', '35'),
            (4, '-1', '45', '40'),
            (5, '-1', '50', '45'),
            (6, '-1', '55', '50'),
            (7, '0', '60', '55'),
            (8, '0', '65', '60'),
            (9, '0', '70', '65'),
            (10, '0', '75', '70'),
            (11, '0', '80', '75'),
            (12, '0', '85', '80'),
            (13, '0', '90', '85'),
            (14, '0', '92', '88'),
            (15, '+1', '94', '91'),
            (16, '+2', '96', '95'),
            (17, '+2 (+3 for Warriors)', '98', '97'),
            (18, '+2 (+4 for Warriors)', '100', '99'),
            (19, '+2 (+5 for Warriors)', '100', '99'), ],
    'CHA': [(3, '1', '-30', '-25'),
            (4, '1', '-25', '-20'),
            (5, '2', '-20', '-15'),
            (6, '2', '-15', '-10'),
            (7, '3', '-10', '-5'),
            (8, '3', '-5', '0'),
            (9, '4', '0', '0'),
            (10, '4', '0', '0'),
            (11, '4', '0', '0'),
            (12, '5', '0', '0'),
            (13, '5', '0', '+5'),
            (14, '6', '+5', '+10'),
            (15, '7', '+15', '+15'),
            (16, '8', '+20', '+25'),
            (17, '10', '+30', '+30'),
            (18, '15', '+40', '+35'),
            (19, '20', '+50', '+40'), ],
}

SYSTEM_PATH = None


def init_system_path(system_path):
    global SYSTEM_PATH
    SYSTEM_PATH = system_path


def has_spells_at_level(level, single_class_dict):
    level = int(level)
    level_dict_list = [row for row in single_class_dict['Classes_meta'] if row['Type'] == 'xp table']
    level_dict = level_dict_list[level-1]
    if level_dict['Casting_Level'] != 0 and level_dict['Casting_Level'] != '':
        return True
    return False


def has_secondary_spells_at_level(level, single_class):
    level = int(level)
    xp_table = [row for row in single_class['Classes_meta'] if row['Type'] == 'xp table']
    xp_row = xp_table[level - 1]
    if xp_row['Level_1_Spells_Secondary'] > 0:
        return True
    return False


def get_race_dict(character_dict):
    race_dict = {}
    for race in DbQuery.getTable('Races'):
        if race['unique_id'] == character_dict['Race']:
            race_dict = race
    return race_dict


def get_attribute_bonuses(attr_key, score):
    score = float(score)
    return_bonus = ()
    for row in bonuses[attr_key]:
        if score > row[0]:
            continue
        return_bonus = row
        break
    return tuple(bonus for bonus in return_bonus[1:])


def get_attribute_bonus_string( attr_key, score ):
    bonuses_dict = {}
    bonuses_dict['STR'] = 'To Hit: {}     Damage: {}     Encumbrance: {}     Minor Test: {}     Major Test: {}%'
    bonuses_dict['INT'] = 'Add\'l Langs: {} Understand Spell Chance: {}% Min/Max Understood / Level: {}'
    bonuses_dict['WIS'] = 'Mental Save: {}     Bonus Cleric Spells: {}     Cleric Spell Failure: {}%'
    bonuses_dict['DEX'] = 'Surprise: {}     Missile To Hit: {}     AC Adjustment: {}'
    bonuses_dict['CON'] = 'HP Bonus: {}   Resurrect/Raise Dead: {}%   System Shock: {}%'
    bonuses_dict['CHA'] = 'Max Henchman: {}     Loyalty: {}     Reaction: {}'

    return bonuses_dict[attr_key].format( *get_attribute_bonuses( attr_key, score ) )


def calculate_ac(attr_dict, class_dict, race_dict, equipment_list):
    base_ac = 10
    dex_score = attr_dict['DEX']
    ac_bonus = get_attribute_bonuses('DEX', dex_score)[2]
    char_base_ac = base_ac + int(ac_bonus)

    armour_list = [e for e in equipment_list if e['unique_id'].startswith('armour_')]
    shield_list = [e for e in equipment_list if e['unique_id'].startswith('shield_')]

    useable_armour = []
    useable_shield = []

    if 'classes' in class_dict:
        ap_lists = []
        sp_lists = []
        for cl in class_dict['classes']:
            armour_permitted_list = [ap.strip() for ap in cl['Armour_Permitted'].split(',')]
            shield_permitted_list = [sp.strip() for sp in cl['Shield_Permitted'].split(',')]
            ap_lists.append(armour_permitted_list)
            sp_lists.append(shield_permitted_list)
        if race_dict['unique_id'] in restrictive_races:
            bucket = []
            all_any = True
            for ap_list in ap_lists:
                if 'None' in ap_list:
                    bucket = []
                    all_any = False
                    break
                elif 'Any' in ap_list:
                    continue
                else:
                    all_any = False
                    for ap in ap_list:
                        if ap not in bucket:
                            bucket.append(ap)
            if all_any:
                useable_armour = armour_list
            else:
                for a in armour_list:
                    if a['Name'] in bucket:
                        useable_armour.append(a)
            bucket = []
            all_any = True
            for sp_list in sp_lists:
                if 'None' in sp_list:
                    bucket = []
                    all_any = False
                    break
                elif 'Any' in ap_list:
                    continue
                else:
                    all_any = False
                    for sp in sp_list:
                        if sp not in sp_list:
                            bucket.append(sp)
            if all_any:
                useable_shield = shield_list
            else:
                for s in shield_list:
                    if s['Name'] in bucket:
                        useable_shield.append(s)
        else:
            bucket = []
            for ap_list in ap_lists:
                for ap in ap_list:
                    if ap not in bucket:
                        bucket.append(ap)

            if 'Any' in bucket:
                useable_armour = armour_list
            else:
                for a in armour_list:
                    if a['Name'] in bucket:
                        useable_armour.append(a)

            bucket = []
            for sp_list in sp_lists:
                for sp in sp_list:
                    if sp not in bucket:
                        bucket.append(sp)

            if 'Any' in bucket:
                useable_shield = shield_list
            else:
                for s in shield_list:
                    if s['Name'] in bucket:
                        useable_shield.append(s)
    else:
        armour_permitted_list = [ap.strip() for ap in class_dict['Armour_Permitted'].split(',')]
        shield_permitted_list = [sp.strip() for sp in class_dict['Shield_Permitted'].split(',')]
        if 'Any' in armour_permitted_list:
            useable_armour = armour_list
        elif 'None' in armour_permitted_list:
            useable_armour = []
        else:
            for a in armour_list:
                if a['Name'] in armour_permitted_list:
                    useable_armour.append(a)
        if 'Any' in shield_permitted_list:
            useable_shield = shield_list
        elif 'None' in shield_permitted_list:
            useable_shield = []
        else:
            for s in shield_list:
                if s['Name'] in shield_permitted_list:
                    useable_shield.append(s)

    best_armour = None
    for a in useable_armour:
        if not best_armour or a['AC_Effect'] < best_armour['AC_Effect']:
            best_armour = a
    best_shield = None
    for s in useable_shield:
        if not best_shield or s['AC_Effect'] < best_shield['AC_Effect']:
            best_shield = s

    if best_armour == None:
        best_armour = {'AC_Effect': 0}
    if best_shield == None:
        best_shield = {'AC_Effect': 0}
    return char_base_ac + best_armour['AC_Effect'] + best_shield['AC_Effect']

def get_saves(level, attr_dict, class_dict, race_dict):
    saves_dict = {'Aimed_Magic_Items': [],
                  'Breath_Weapons': [],
                  'Death_Paralysis_Poison': [],
                  'Petrifaction_Polymorph': [],
                  'Spells': [],}
    if 'classes' in class_dict:
        level_list = [ int(l) for l in level.split('/') ]
        for i, cl in enumerate( class_dict['classes'] ):
            for meta_row in cl['Classes_meta']:
                if meta_row['Type'] == 'xp table' and meta_row['Level'] != 'each' and int(meta_row['Level']) == level_list[i]:
                    for save in list(saves_dict.keys()):
                        saves_dict[save].append(meta_row[save])
        if race_dict['unique_id'] in restrictive_races:
            for save in list(saves_dict.keys()):
                saves_dict[save] = max(*tuple(int(l) for l in saves_dict[save]))
        else:
            for save in list(saves_dict.keys()):
                saves_dict[save] = min(*tuple(int(l) for l in saves_dict[save]))
    else:
        level = int(level)
        for meta_row in class_dict['Classes_meta']:
            if meta_row['Type'] == 'xp table' and meta_row['Level'] != 'each' and int(meta_row['Level']) == level:
                for save in list(saves_dict.keys()):
                    saves_dict[save] = meta_row[save]

    for meta_row in race_dict['Races_meta']:
        if meta_row['Type'] == 'ability' and meta_row['Subtype'] == 'save':
            modifier = meta_row['Modifier']
            modified = meta_row['Modified']
            num_modifier = ''
            for attr_name in list(attr_dict.keys()):
                if attr_name.lower() in modifier.lower():
                    num_modifier = modifier.lower().replace(attr_name.lower(), attr_dict[attr_name])
            #print num_modifier
            for mod in modified.split('/'):
                for save in list(saves_dict.keys()):
                    if mod.strip().replace(' ', '_') == save:
                        saves_dict[save] = int( eval(str(saves_dict[save]) + num_modifier) )
                    elif mod.strip().replace(' ', '_') in save:
                        saves_dict[save] = str(saves_dict[save]) + ' (' + mod.strip() + ' ' + str( int( eval(str(saves_dict[save]) + num_modifier) ) ) + ')'
                    elif save.replace('_', ' ') in mod:
                        mod_list = mod.split(':')
                        saves_dict[save] = str(saves_dict[save]) + ' (' + mod_list[1] + ' ' + str( int( eval(str(saves_dict[save]) + num_modifier) ) ) + ')'
                    if len(str(saves_dict[save])) > 15:
                        saves_dict[save] = str(saves_dict[save]).replace(' (', '<br />(')

    return saves_dict

def get_tohit_row(level, class_dict, race_dict):
    tohit_list = []
    if 'classes' in class_dict:
        level_list = [ int(l) for l in level.split('/') ]
        bucket = []
        for i, cl in enumerate( class_dict['classes'] ):
            for row in cl['Classes_meta']:
                if row['Type'] == 'xp table' and row['Level'].isdigit() and int(row['Level']) == level_list[i]:
                    tohit_tuple = (row['To_Hit_-10'],
                                   row['To_Hit_-9'],
                                   row['To_Hit_-8'],
                                   row['To_Hit_-7'],
                                   row['To_Hit_-6'],
                                   row['To_Hit_-5'],
                                   row['To_Hit_-4'],
                                   row['To_Hit_-3'],
                                   row['To_Hit_-2'],
                                   row['To_Hit_-1'],
                                   row['To_Hit_0'],
                                   row['To_Hit_1'],
                                   row['To_Hit_2'],
                                   row['To_Hit_3'],
                                   row['To_Hit_4'],
                                   row['To_Hit_5'],
                                   row['To_Hit_6'],
                                   row['To_Hit_7'],
                                   row['To_Hit_8'],
                                   row['To_Hit_9'],
                                   row['To_Hit_10'],
                                   )
                    bucket.append(tohit_tuple)
        for i in range(0, 21):
            items = (row[i] for row in bucket)
            if race_dict['unique_id'] in restrictive_races:
                tohit_list.append(str(max(*items)))
            else:
                tohit_list.append(str(min(*items)))

    else:
        level = int(level)
        for row in class_dict['Classes_meta']:
            if row['Type'] == 'xp table' and row['Level'].isdigit() and int(row['Level']) == level:
                tohit_list = [str(row['To_Hit_-10']),
                              str(row['To_Hit_-9']),
                              str(row['To_Hit_-8']),
                              str(row['To_Hit_-7']),
                              str(row['To_Hit_-6']),
                              str(row['To_Hit_-5']),
                              str(row['To_Hit_-4']),
                              str(row['To_Hit_-3']),
                              str(row['To_Hit_-2']),
                              str(row['To_Hit_-1']),
                              str(row['To_Hit_0']),
                              str(row['To_Hit_1']),
                              str(row['To_Hit_2']),
                              str(row['To_Hit_3']),
                              str(row['To_Hit_4']),
                              str(row['To_Hit_5']),
                              str(row['To_Hit_6']),
                              str(row['To_Hit_7']),
                              str(row['To_Hit_8']),
                              str(row['To_Hit_9']),
                              str(row['To_Hit_10']),
                              ]
    return tohit_list


def convert_cost_string(cost_string):
    cost_split = cost_string.split()
    if cost_split[0].lower() == 'free':
        cost = Decimal('0')
        denomination = None
    else:
        cost = Decimal(''.join(d for d in cost_split[0] if d.isdigit()))
        try:
            denomination = cost_split[1]
        except IndexError:
            denomination = None

    if denomination:
        try:
            ratio = Decimal(str(economy[denomination]))
            final_cost = ratio * cost
        except KeyError:
            final_cost = cost
    else:
        final_cost = cost

    return final_cost


def get_coinage_from_float(gp_decimal):
#    bucket = int(gp_decimal * 100)
#    coin_denominations = sorted(economy, key=lambda x: economy[x], reverse=True)
#    return_dict = dict.fromkeys(coin_denominations, 0)
#    for cd in coin_denominations:
#        if economy[cd] <= 1:
#            cd_bucket = 0
#            while bucket >= economy[cd] * 100:
#                bucket = bucket - int(economy[cd] * 100)
#                cd_bucket = cd_bucket + 1
#                return_dict[cd] = cd_bucket

#    return return_dict
    gp_decimal = Decimal( str( gp_decimal ) )
    coin_denominations = sorted(economy, key=lambda x: economy[x], reverse=True)
    return_dict = dict.fromkeys(coin_denominations, 0)
    for cd in coin_denominations:
        if economy[cd] <= 1:
            coin_decimal = Decimal( str( economy[cd] ) )
            coin_mod = gp_decimal // coin_decimal
            gp_decimal -= coin_mod * coin_decimal
            return_dict[cd] = int( coin_mod )

    return return_dict


def get_float_from_coinage(character_or_money_dict):
    total = 0
    coin_denominations = list(economy.keys())
    for cd in coin_denominations:
        total += float(economy[cd] * character_or_money_dict[cd])
    return total


# TODO: Properly implement restrictive races vs permissive races
def race_is_restrictive(race):
    if isinstance(race, dict):
        race = race['unique_id']

    if race in restrictive_races:
        return True

    return False


def race_wp(wp_list, race_id, item_dict_list):
    blunt_list = [blunt['Name'].lower() for blunt in item_dict_list if 'blunt' in blunt['Damage_Type'].split(',')]
    # race_wp = []
    wp_expand = []
    for wp in wp_list:
        wp_expand.append([w.strip().lower() for w in wp.split(',')])
    if race_is_restrictive(race_id):
        bucket = wp_expand[0]
        if 'blunt' in bucket:
            bucket.remove('blunt')
            bucket.extend(blunt_list)
        for i in range(1, len(wp_expand)):
            if 'blunt' in wp_expand[i]:
                wp_expand[i].remove('blunt')
                wp_expand[i].extend(blunt_list)
            if 'any' in bucket:
                bucket = wp_expand[i]
            elif 'any' in wp_expand[i]:
                bucket = bucket
            else:
                bucket = [w for w in bucket if w in wp_expand[i]]

    else:
        wp_flat = sum(wp_expand, [])
        bucket = []
        for wp in wp_flat:
            if wp not in bucket:
                bucket.append(wp)
    if 'any' in bucket:
        bucket = ['any', ]
    return bucket


def calculate_movement(race_dict, class_dict, attr_dict, equipment_list):
    base_movement = race_dict['Movement_Rate']
    str_bonus = get_attribute_bonuses('STR', attr_dict['STR'])[2]
    max_movement = 120
    equipment_weight = 0
    wearable_armour = []
    for equip in equipment_list:
        if equip['Weight'] != 'N/A' and equip['Weight'] != '-':
            equip_weight = ''.join([c for c in equip['Weight'] if c.isdigit() or c == '/'])
            if equip_weight.find('/') != -1:
                equip_weight_tuple = equip_weight.split('/')
                numerator = int(equip_weight_tuple[0])
                denominator = int(equip_weight_tuple[1])
                equipment_weight += numerator / float(denominator)
            else:
                equipment_weight += float(equipment_weight)

        if equip['Max_Move_Rate'] != '' and equip['Max_Move_Rate'] != 'N/A':
            base_ac = calculate_ac(attr_dict, class_dict, race_dict, [])
            adj_ac = calculate_ac(attr_dict, class_dict, race_dict, [equip])
            if adj_ac < base_ac:
                wearable_armour.append(equip)
    best_armour = None
    for wa in wearable_armour:
        if not best_armour or wa['AC_Effect'] < best_armour['AC_Effect']:
            best_armour = wa
    if best_armour:
        max_move = ''.join([c for c in best_armour['Max_Move_Rate'] if c.isdigit()])
        if int(max_move) < max_movement:
            max_movement = int(max_move)

    if equipment_weight <= 35 + int(str_bonus):
        movement = (min(base_movement, max_movement), '+1 (for armour lighter than chain mail only)')
    elif equipment_weight <= 70 + int(str_bonus):
        movement = (min(base_movement - 30, max_movement), 'Normal bonuses apply')
    elif equipment_weight <= 105 + int(str_bonus):
        movement = (min(base_movement - 60, max_movement), 'No normal bonuses apply (but penalties do)')
    elif equipment_weight <= 150 + int(str_bonus):
        movement = (min(30, max_movement), 'No normal bonuses apply (but penalties do); -1 extra penalty')
    else:
        movement = (0, 'No movement possible')

    return movement

def get_spells_by_level(level, attr_dict, single_class_dict):
    level = int(level)
    primary_spell_string = 'Level_{}_Spells'
    secondary_spell_string = 'Level_{}_Spells_Secondary'
    primary = ''
    secondary = ''
    for row in single_class_dict['Classes_meta']:
        if row['Type'] == 'xp table' and row['Level'].isdigit() and int(row['Level']) == level and row['Casting_Level'] > 0:
            for i in range(1, 10):
                primary_key = primary_spell_string.format(i)
                secondary_key = secondary_spell_string.format(i)
                if row[primary_key] > 0:
                    primary_int = row[primary_key]
                    if i > 1:
                        primary += '/'
                    if single_class_dict['Category'] == 'priest':
                        bonus_spells = get_attribute_bonuses('WIS', attr_dict['WIS'])[1]
                        bonus_spells_list = bonus_spells.split('/')
                        if i - 1 < len(bonus_spells_list):
                            primary_int += int(bonus_spells_list[i - 1])
                    primary += str(primary_int)
                if row[secondary_key] > 0:
                    if i > 1:
                        secondary += '/'
                    secondary += str(row[secondary_key])
    return ( primary, secondary )

def get_turn_undead_row( level, single_class_dict ):
    level = int(level)
    tu_list = []
    col_string = 'Turn_Undead_Type_{}'
    for row in single_class_dict['Classes_meta']:
        if row['Type'] == 'xp table' and row['Level'].isdigit() and int( row['Level'] ) == level:
            for i in range( 1, 14 ):
                col = col_string.format(i)
                tu_list.append( row[col] )
    return tu_list

ta_col_list = ['Climb_Walls', 'Find_Traps', 'Hear_Noise', 'Hide_in_Shadows',
               'Move_Quietly', 'Open_Locks', 'Pick_Pockets', 'Read_Languages']
def get_thief_abilities_row( level, single_class_dict ):
    level = int(level)
    ta_list = []
    for row in single_class_dict['Classes_meta']:
        if row['Type'] == 'xp table' and row['Level'].isdigit() and int( row['Level'] ) == level:
            for ta_col in ta_col_list:
                ta_list.append( '{}%'.format( row[ta_col] ) )
    return ta_list

def get_class_abilities( level, attr_dict, single_class_dict ):
    level = int(level)
    spells_by_level = get_spells_by_level( level, attr_dict, single_class_dict )
    cl_ab = []
    if spells_by_level[0]:
        primary_spells = single_class_dict['Primary_Spell_List'].replace('_', ' ').title()
        cl_ab.append(('{} Spells by Level'.format(primary_spells), spells_by_level[0]))
        if spells_by_level[1]:
            secondary_spells = single_class_dict['Secondary_Spell_List'].replace('_', ' ').title()
            cl_ab.append(('{} Spells by Level'.format(secondary_spells), spells_by_level[1]))
    tu_list = get_turn_undead_row( level, single_class_dict )
    ta_list = get_thief_abilities_row( level, single_class_dict )
    for row in single_class_dict['Classes_meta']:
        if row['Type'] == 'ability' and level >= row['Level_Gained']:
            cl_ab.append((row['Ability'], row['Ability_Description']))
            if tu_list and 'turn' in row['Ability'].lower() and 'undead' in row['Ability'].lower():
                headers = [ 'Type {}'.format( i ) for i in range( 1, 14 ) ]
                cl_ab.append( ( '', ( headers, tu_list ) ) )
            if ta_list and 'thief abilities' in row['Ability'].lower():
                headers = [ h.replace( '_', ' ' ) for h in ta_col_list ]
                cl_ab.append( ( '', ( headers, ta_list ) ) )

    return cl_ab


def get_race_dict(character_dict):
    race_dict = {}
    for race in DbQuery.getTable('Races'):
        if race['unique_id'] == character_dict['Race']:
            race_dict = race
    return race_dict


def get_race_abilities( race_dict ):
    return_list = []
    subtype_list = [ 'combat', 'starting languages', 'infravision', 'misc' ]
    for row in race_dict['Races_meta']:
        if row['Type'] == 'ability' and row['Subtype'] in subtype_list:
            if row['Subtype'] == 'infravision':
                first_item = 'Infravision {}'.format( row['Modifier'] )
            elif row['Subtype'] == 'starting languages':
                first_item = 'Starting Languages: '
            else:
                first_item = row['Modifier']
            return_list.append( ( first_item, row['Modified'], row['Notes'] ) )
    return return_list

def get_spell_book( spell_list ):
    output_string = ''
    for spell in spell_list:
        spell['Name']

def get_non_proficiency_penalty( class_dict, race_dict ):
    race_id = race_dict['unique_id']
    if 'classes' in class_dict:
        bucket = []
        for cl in class_dict['classes']:
            bucket.append( cl['Non-Proficiency_Penalty'] )
        if race_id in restrictive_races:
            return min( bucket )
        else:
            return max( bucket )

    return class_dict['Non-Proficiency_Penalty']


def get_class_dict(character_dict):
    class_table = DbQuery.getTable('Classes')
    class_dict = {'Name': '', 'classes': []}
    classes_list = character_dict['Classes'].split('/')
    for class_id in classes_list:
        for cl in class_table:
            if class_id == cl['unique_id']:
                if class_dict['Name'] == '':
                    if len(classes_list) == 1:
                        class_dict = cl
                        break
                    class_dict['Name'] = cl['Name']
                else:
                    class_dict['Name'] += '/{}'.format(cl['Name'])
                class_dict['classes'].append(cl)
    return class_dict


def get_class_names(character_dict):
    return get_class_dict(character_dict)['Name']


def character_tool_tip(character, _fields):
    return f'''\
<div>
<table>
<tr><td rowspan="4"><img height="200"  src=data:image;base64,{character['Portrait']}></td>
<th colspan="2">{character['Name']}</th></tr>
<tr><th>Level:</th><td>{character['Level']}</td></tr>
<tr><th>Class:</th><td>{get_class_names(character)}</td></tr>
<tr><th>Race:</th><td>{get_race_dict(character)['Name']}</td></tr>
</table>
</div>'''


def monster_tool_tip(monster, _fields):
    return f'''\
<style>
table th {{
    text-align: right;
}}
</style>
<table>
<tr><th align="center" colspan="2">{monster['Name']}</th></tr>
<tr><th>Type:</th><td>{monster['Type']}</td></tr>
<tr><th>Frequency:</th><td>{monster['Frequency']}</td></tr>
<tr><th>Size:</th><td>{monster['Size']}</td></tr>
<tr><th>AC:</th><td>{monster['AC']}</td></tr>
<tr><th>HD:</th><td>{monster['HD']}</td></tr>
</table>'''


def get_character_pdf_markup( character_dict ):
    class_table = DbQuery.getTable( 'Classes' )
    race_table = DbQuery.getTable( 'Races' )
    items_table = DbQuery.getTable( 'Items' )
    spells_table = DbQuery.getTable( 'Spells' )

    class_dict = { 'Name' : '', 'classes' : [] }
    classes_list = character_dict['Classes'].split( '/' )
    for class_id in classes_list:
        for cl in class_table:
            if class_id == cl['unique_id']:
                if class_dict['Name'] == '':
                    if len( classes_list ) == 1:
                        class_dict = cl
                        break
                    class_dict['Name'] = cl['Name']
                else:
                    class_dict['Name'] += '/{}'.format( cl['Name'] )
                class_dict['classes'].append(cl)

    level = character_dict['Level']
    class_name = class_dict['Name']
    class_font_size = '14px'
    class_padding = '0px'
    if len( class_name ) > 15:
        class_font_size = '8px'
        class_padding = '4px'

    for race in race_table:
        if race['unique_id'] == character_dict['Race']:
            race_dict = race

    portrait = character_dict['Portrait']
    ext = character_dict['Portrait_Image_Type']

    attr_dict = {
        'STR' : character_dict['STR'],
        'INT' : character_dict['INT'],
        'WIS' : character_dict['WIS'],
        'DEX' : character_dict['DEX'],
        'CON' : character_dict['CON'],
        'CHA' : character_dict['CHA'],
    }

    equip_id_list = []
    spellbook_id_list = []
    daily_spells_id_list = []
    daily_spells2_id_list = []
    daily_spells3_id_list = []
    proficiency_id_dict = {}
    for meta_row in character_dict['Characters_meta']:
        if meta_row['Type'] == 'Equipment':
            equip_id_list.append( meta_row['Entry_ID'] )
        elif meta_row['Type'] == 'Treasure':
            if meta_row['Entry_ID'] == 'gp':
                gp = meta_row['Data']

            elif meta_row['Entry_ID'] == 'pp':
                pp = meta_row['Data']

            elif meta_row['Entry_ID'] == 'ep':
                ep = meta_row['Data']

            elif meta_row['Entry_ID'] == 'sp':
                sp = meta_row['Data']

            elif meta_row['Entry_ID'] == 'cp':
                cp = meta_row['Data']
        elif meta_row['Type'] == 'Spellbook':
            spellbook_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'DailySpells':
            daily_spells_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'DailySpells2':
            daily_spells2_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'DailySpells3':
            daily_spells3_id_list.append(meta_row['Entry_ID'])
        elif meta_row['Type'] == 'Proficiency':
            proficiency_id_dict[meta_row['Entry_ID']] = meta_row['Data']

    proficiency_list = []
    specialised_list = []
    double_specialised_list = []
    for prof in items_table:
        if prof['Is_Proficiency'].lower() == 'yes' and prof['unique_id'] in list( proficiency_id_dict.keys() ):
            prof_name = prof['Name']
            prof_level = proficiency_id_dict[  prof['unique_id'] ]
            if prof_level == 'P':
                proficiency_list.append( prof )
            elif prof_level == 'S':
                specialised_list.append( prof )
            elif prof_level == '2XS':
                double_specialised_list.append( prof )

    equipment_list = []
    for equip in items_table:
        if equip['unique_id'] in equip_id_list:
            equipment_list.append( equip )

    class_abilities = {}
    if 'classes' in class_dict:
        level_list = [ int(l) for l in level.split('/') ]
        for i, cl in enumerate( class_dict['classes'] ):
            class_abilities[ cl['Name'] ] = get_class_abilities( level_list[i], attr_dict, cl )
    else:
        class_abilities[ class_dict['Name'] ] = get_class_abilities( level, attr_dict, class_dict )
    race_abilities = get_race_abilities( race_dict )

    spellbook = []
    daily_spells = []
    daily_spells2 = []
    daily_spells3 = []
    for spell in spells_table:
        if spell['spell_id'] in spellbook_id_list:
            spellbook.append(spell)
        if spell['spell_id'] in daily_spells_id_list:
            daily_spells.append(spell)
        if spell['spell_id'] in daily_spells2_id_list:
            daily_spells2.append(spell)
        if spell['spell_id'] in daily_spells3_id_list:
            daily_spells3.append(spell)

    #print equipment_list
    saves_dict = get_saves( level, attr_dict, class_dict, race_dict )
    movement_tuple = calculate_movement( race_dict, class_dict, attr_dict, equipment_list )
    markup_template_dict = {
        'class_font_size' : class_font_size,
        'class_padding' : class_padding,
        'name' : character_dict['Name'],
        'gender' : character_dict['Gender'],
        'class' : class_dict['Name'],
        'alignment' : character_dict['Alignment'],
        'race' : race_dict['Name'],
        'xp' : character_dict['XP'],
        'hp' : character_dict['HP'],
        'ac' : calculate_ac( attr_dict, class_dict, race_dict, equipment_list ),
        'level' : level,
        'age' : character_dict['Age'],
        'height': character_dict['Height'],
        'weight': character_dict['Weight'],
        'portrait': portrait,
        'image_type': ext,
        'tohit_row': '<td align=center>' + '</td><td align=center>'.join( get_tohit_row( level, class_dict, race_dict ) ) + '</td>',
        'gp' : gp,
        'pp' : pp,
        'ep' : ep,
        'sp' : sp,
        'cp' : cp,
        'movement_rate' : movement_tuple[0],
        'movement_desc' : movement_tuple[1],
        'nonproficiency_penalty' : get_non_proficiency_penalty( class_dict, race_dict ),
        }
    for attr_name in list( attr_dict.keys() ):
        markup_template_dict[attr_name] = attr_dict[attr_name]
        markup_template_dict[ attr_name + '_bonus' ] = get_attribute_bonus_string( attr_name, attr_dict[attr_name] )
    for save in list( saves_dict.keys() ):
        markup_template_dict[save] = saves_dict[save]

    markup = '''\
<style type=text/css>
.border {
color: red;
border-style: solid;
border-color: purple;
margin-right: 5px;
}

.bigger-font {
font-size: 15px;
}

.smaller-font {
font-size: 10px;
}

.pad-cell {
padding-left: 5px;
padding-right: 5px;
}

.pad-bottom {
padding-bottom: 5px;
}

.pad-top-large {
padding-top: 10px;
}

.pad-all {
padding: 5px;
}

.no-pad {
padding: 0px;
}

.lpad {
padding-left: 15px;
}

.float-right {
float: right;
}

.class-font {
font-size: $class_font_size;
padding-top: $class_padding;
}

.alignment-font {
font-size: 10px;
padding-top: 3px;
}

.attr-bonuses {
font-size: 8px;
vertical-align: middle;
white-space: pre;
}

.tohit-table {
border-style: solid;
}

.tohit-table > tr > td {
padding: 2px;
vertical-align: middle;
}

.equipment-table > tr > th {
padding: 4px;
align: center;
font-size: 10px;
}

.equipment-table > tr > td {
padding: 4px;
align: center;
font-size: 10px;
}

.equip-legend {
font-size: 8px;
}

table.ability {
font-size: 12px;
}

table.ability > tr > th {
padding: 2px;
}

.pre {
white-space: pre;
}

p.page-break {
page-break-after:always;
}
</style>
<h1 align=center>$name</h1>

<table width=100%>
<tr><td></td><td></td><td></td><td></td><td></td><td></td><td class=lpad align=center rowspan=5><img height=140 src=data:image;base64,$portrait /></td></tr>
<tr><td class=pad-bottom><b>Name: </b></td><td align=right>$name</td><td class=lpad><b>XP: </b></td><td align=right>$xp</td><td class=lpad><b>Age: </b></td align=right><td align=right>$age</td></tr>
<tr><td class=pad-bottom><b>Class: </b></td><td align=right class=class-font>$class</td><td class=lpad><b>HP: </b></td><td align=right>$hp</td><td class=lpad><b>Height: </b></td><td align=right>$height</td></tr>
<tr><td class=pad-bottom><b>Alignment: </b></td><td align=right class=alignment-font>$alignment</td><td class=lpad><b>AC: </b></td><td align=right>$ac</td><td class=lpad><b>Weight: </b></td><td align=right>$weight</td></tr>
<tr><td class=pad-bottom><b>Race: </b></td><td align=right>$race</td><td class=lpad><b>Level: </b></td><td align=right>$level</td><td class=lpad><b>Gender: </b></td><td align=right>$gender</td></tr>
</table>

<hr />

<table align=center><tr>

<td>
<table class='border bigger-font' border=2 ><tr><td>
<table class=pad-cell>
<tr><td align=right class=pad-cell>Str:</td><td align=right class=pad-cell>$STR</td><td class=attr-bonuses> $STR_bonus </td></tr>
<tr><td align=right class=pad-cell>Int:</td><td align=right class=pad-cell>$INT</td><td class=attr-bonuses> $INT_bonus </td></tr>
<tr><td align=right class=pad-cell>Wis:</td><td align=right class=pad-cell>$WIS</td><td class=attr-bonuses> $WIS_bonus </td></tr>
<tr><td align=right class=pad-cell>Dex:</td><td align=right class=pad-cell>$DEX</td><td class=attr-bonuses> $DEX_bonus </td></tr>
<tr><td align=right class=pad-cell>Con:</td><td align=right class=pad-cell>$CON</td><td class=attr-bonuses> $CON_bonus  </td></tr>
<tr><td align=right class=pad-cell>Cha:</td><td align=right class=pad-cell>$CHA</td><td class=attr-bonuses> $CHA_bonus </td></tr>
</table>
</td></tr></table>
</td>

<td>
<table class=smaller-font align=center border=1>
<tr><td colspan=2><h3 align=center>Saving Throws</h3></td></tr>
<tr><td class=pad-cell>Aimed Magic Items</td><td class=pad-cell align=right>$Aimed_Magic_Items </td></tr>
<tr><td class=pad-cell>Breath Weapon</td><td class=pad-cell align=right>$Breath_Weapons </td></tr>
<tr><td class=pad-cell>Death, Paralysis, Poison</td><td class=pad-cell align=right>$Death_Paralysis_Poison </td></tr>
<tr><td class=pad-cell>Petrifaction, Polymorph</td><td class=pad-cell align=right>$Petrifaction_Polymorph </td></tr>
<tr><td class=pad-cell>Spells</td><td class=pad-cell align=right>$Spells </td></tr>
</tr></table>
</td>

</tr></table>

<hr />

<table class=tohit-table border=1 align=center>
<tr><td><b>Enemy AC</b></td><td align=center> -10 </td><td align=center> -9 </td><td align=center> -8 </td><td align=center> -7 </td><td align=center> -6 </td><td align=center> -5 </td>
<td align=center> -4 </td><td align=center> -3 </td><td align=center> -2 </td><td align=center> -1 </td><td align=center> 0 </td><td align=center> 1 </td>
<td align=center> 2 </td><td align=center> 3 </td><td align=center> 4 </td><td align=center> 5 </td><td align=center> 6 </td><td align=center> 7 </td>
<td align=center> 8 </td><td align=center> 9 </td><td align=center> 10 </td></tr>
<tr><td><b>To Hit</b></td>$tohit_row</tr>
</table>

<hr />

<div class=pre align=center>GP: $gp     PP: $pp     EP: $ep     SP: $sp     CP: $cp</div>

<hr />

<table align=center>
<tr><th><h4>Equipment</h4></th></tr>
<tr><td><table border=1 class=equipment-table>
<tr><th>Name</th><th>Damage Vs S or M</th><th>Damage Vs L</th><th>Damage Type</th><th>RoF</th><th>Range</th><th>Max Move</th><th>AC Effect</th><th>Notes</th></tr>
'''

#    proficiency_page = self.pages['ProficiencyPage']
#    specialised_list = proficiency_page.specialised_list
#    double_specialised_list = proficiency_page.double_specialised_list
    for equip in equipment_list:
        equip_name = equip['Name']
        if equip in double_specialised_list:
            equip_name = equip_name + '<sup>&Dagger;</sup>'
        elif equip in specialised_list:
            equip_name = equip_name + '<sup>&dagger;</sup>'
        elif equip in proficiency_list:
            equip_name = equip_name + '*'
        equip_list = [ equip_name, equip['Damage_Vs_S_or_M'], equip['Damage_Vs_L'], equip['Damage_Type'],
                       equip['Rate_of_Fire'], equip['Range'], equip['Max_Move_Rate'], str( equip['AC_Effect'] ), equip['Notes'] ]
        markup += '<tr><td align=center>' + '</td><td align=center>'.join( equip_list ) + '</td></tr>'

    markup += '''
</table></td></tr></table>
<div align=center class="equip-legend pre">*=Proficient     &dagger;=Specialised     &Dagger;=Double Specialised</div>
<div><b>Movement Rate: </b>$movement_rate ft/round<br />
<b>Surprise: </b>$movement_desc<br />
<b>Non-Proficiency Penalty: </b>$nonproficiency_penalty</div>

<p class=page-break></p>
<h2>Ablities</h2>
'''

    if class_abilities:
        for cl in list( class_abilities.keys() ):
            markup += '\n<h5>{} Abilities</h5>\n'.format( cl )
            for i, a in enumerate( class_abilities[cl] ):
                if a[0]:
                    if i > 0:
                        markup += '<br />'
                    markup += '<b>{}: </b>{}\n'.format( *a )
                else:
                    markup += '<table class=ability align=center border=1>\n<tr>'
                    for h in a[1][0]:
                        markup += '<th align=center>{}</th>'.format(h)
                    markup += '</tr>\n<tr>'
                    for d in a[1][1]:
                        markup += '<td align=center>{}</td>'.format(d)
                    markup += '</tr>\n</table>\n'

    if race_abilities:
        markup += '\n<h5>{} Abilites</h5>\n'.format( race_dict['Name'] )
        markup += '<ul>\n'
        for a in race_abilities:
            markup += '<li>'
            markup += a[0]
            if a[1]:
                markup += ' {}'.format( a[1] )
            if a[2]:
                markup += ' {}'.format( a[2] )
            markup += '</li>\n'
        markup += '</ul>\n'

    spellcaster = False
    if 'classes' in class_dict:
        level_list = [ int(l) for l in level.split( '/' ) ]
        for i, cl in enumerate( class_dict['classes'] ):
            if has_spells_at_level( level_list[i], cl ):
                spellcaster = True
    else:
        if has_spells_at_level( level, class_dict ):
            spellcaster = True

    if spellcaster:
        spell_item_string = '''
<h3>{Name}</h3>
<b>Reversible: </b>{Reversible}<br/>
<b>Level: </b>{Level}<br />
<b>Damage: </b>{Damage}<br />
<b>Range: </b>{Range}<br />
<b>Duration: </b>{Duration}<br />
<b>Area of Effect: </b>{Area_of_Effect}<br />
<b>Components: </b>{Components}<br />
<b>Casting Time: </b>{Casting_Time}<br />
<b>Saving Throw: </b>{Saving_Throw}<br />
<b>Description: </b><span class=pre>{Description}</span><br /><br />
'''
        markup += '<p class=page-break></p>\n<h2>Spells</h2>\n'
        if spellbook:
            markup += '<h5>Spellbook</h5>\n<hr />'
            for spell in spellbook:
                markup += spell_item_string.format( **spell )
            markup += '<hr />\n'
        if daily_spells:
            markup += '<h5>{} Daily Spells</h5>\n<hr />'.format( daily_spells[0]['Type'].title().replace( '_', ' ' ) )
            for spell in daily_spells:
                markup += spell_item_string.format( **spell )
            markup += '<hr />\n'
        if daily_spells2:
            markup += '<h5>{} Daily Spells</h5>\n<hr />'.format( daily_spells2[0]['Type'].title().replace( '_', ' ' ) )
            for spell in daily_spells2:
                markup += spell_item_string.format( **spell )
            markup += '<hr />\n'
        if daily_spells3:
            markup += '<h5>{} Daily Spells</h5>\n<hr />'.format(daily_spells3[0]['Type'].title().replace('_', ' '))
            for spell in daily_spells2:
                markup += spell_item_string.format(**spell)
            markup += '<hr />\n'

    t = Template(markup)
    final_markup = t.safe_substitute( markup_template_dict )

    return '{}.pdf'.format(character_dict['Name']), final_markup
