import Dice
import SystemSettings
import DbQuery
import json
import re
import time
from Common import callback_factory_2param
from GuiDefs import *
from ManageDefs import Manage


class EncounterTrackerWizard(Wizard):

    def __init__(self):
        super().__init__('Encounter Tracker', modality='unblock')

        self.add_wizard_page(EncounterIntro())
        self.add_wizard_page(SurprisePage())
        # self.add_wizard_page(DeclareActionsPage())
        self.add_wizard_page(BattleRoundsPage())
        # self.add_wizard_page(PcTeamAttackPage())
        # self.add_wizard_page(MonsterTeamAttackPage())
        # self.add_wizard_page(SimultaneousAttackPage())
        self.add_wizard_page(WrapUpPage())


class EncounterIntro(WizardPage):
    def __init__(self):
        super().__init__(0, 'Encounter Tracker')
        self.set_subtitle('Encounter Wizard')
        self.encounter_id = None

        # Define internal functions

        # Define Widgets
        info = '''\
The encounter is about to begin. Remember the order of events:<ol><li>Determine Surprise</li>
<li>Declare Spells and General Actions</li><li>Determine Initiative</li>
<li>Party with initiative acts first and results take effect</li>
<li>Party that lost initiative acts and results take effect</li>
<li>The round is complete (start the next round on step 2)</li></ol>'''
        intro_text = Widget('Intro Text', 'TextLabel', align='Center', data=info)

        # Add Actions

        # Initialize GUI
        self.add_row([intro_text])

    def initialize_page(self, fields, pages, external_data):
        t = time.time()
        self.encounter_id = f'encounter-{t}'
        hd_plus_minus_pattern = re.compile(r'^\d+[+-]\d+$')
        monster_team = external_data['Monster Team']
        enemies = []
        for enemy in monster_team:
            if enemy['TableName'] == 'Characters':
                enemies.append(enemy)
            else:
                hd = enemy['HD']
                if hd.isdigit():
                    roll_string = f'''{hd}d8'''
                    hp = Dice.rollString(roll_string)
                elif hd_plus_minus_pattern.match(hd):
                    hd_split = re.split(r'([+-])', hd)
                    roll_string = f'{hd_split[0]}d8{hd_split[1]}{hd_split[2]}'
                    hp = max(Dice.rollString(roll_string), 1)
                elif hd.endswith('hp'):
                    roll_string = f'''{hd.replace('hp', '').strip()}'''
                    hp = max(Dice.rollString(roll_string), 1)
                else:
                    hp = hd
                enemy['HP'] = hp
                enemy['XP Value'] = SystemSettings.get_xp_value(enemy)
                enemies.append(enemy)
        serialized_enemies = json.dumps(enemies)
        DbQuery.insertRow('Encounters', (self.encounter_id, '', serialized_enemies))
        DbQuery.commit()


def open_hp_tracker(fields, pages, _external):
    characters = fields['PC Team']
    encounter_id = pages['Encounter Tracker'].encounter_id
    return HpTracker(characters, encounter_id)


class SurprisePage(WizardPage):
    def __init__(self):
        super().__init__(1, 'Surprise')
        self.set_subtitle('Determine Surprise')

        item_table = DbQuery.getTable('Items')
        indexed_items = {item['unique_id']: item for item in item_table}

        # Define internal functions
        def pc_tool_tip(pc, _fields, _pages, _external):
            race_dict = SystemSettings.get_race_dict(pc)
            class_dict = SystemSettings.get_class_dict(pc)
            equipment_ids = [row['Entry_ID'] for row in pc['Characters_meta'] if row['Type'] == 'Equipment']
            # equipment = [equip for equip in item_table if equip['unique_id'] in equipment_ids]
            equipment = [indexed_items[equipment_id] for equipment_id in equipment_ids]
            _, surprise = SystemSettings.calculate_movement(race_dict, class_dict, pc, equipment)
            return f'''\
<b>{pc['Name']}</b><br />
Surprise: {surprise}<br />
AC: {SystemSettings.calculate_ac(pc, class_dict, race_dict, equipment)}
'''

        def enemy_tool_tip(enemy, _fields, _pages, _external):
            if enemy['TableName'] == 'Monsters':
                special_attacks = enemy['Special_Attacks']
                special_defences = enemy['Special_Defences']
                description = enemy['Description']
                return f'''\
<b>{enemy['Name']}</b><br />
AC: {enemy['AC']}<br />
Special Attacks: {special_attacks}<br />
Special Defences: {special_defences}<br /><br />
{description}
'''
            else:
                return pc_tool_tip(enemy, _fields, _pages, _external)

        # Define Widgets
        pc_team_surprise = Widget('PC Team Surprise', 'SpinBox')
        open_hp_tracker_button = Widget('Open HP Tracker', 'PushButton', align='Right')
        pc_team = Widget('PC Team', 'ListBox', tool_tip=pc_tool_tip, col_span=2)
        monster_team_surprise = Widget('Monster Team Surprise', 'SpinBox')
        monster_team = Widget('Monster Team', 'ListBox', tool_tip=enemy_tool_tip, col_span=2)

        # Add Actions
        self.add_action(Action('Window', open_hp_tracker_button, callback=open_hp_tracker))
        # self.add_action(Action('Window', pc_team, callback=open_hp_tracker))
        # self.add_action(Action('Window', monster_team, callback=open_hp_tracker))

        # Initialize GUI
        self.add_row([pc_team_surprise, open_hp_tracker_button])
        self.add_row([pc_team])
        self.add_row([monster_team_surprise])
        self.add_row([monster_team])

    def initialize_page(self, fields, pages, external_data):
        surprise_roll = '1d6'
        pc_team_roll = Dice.rollString(surprise_roll)
        monster_team_roll = Dice.rollString(surprise_roll)
        return {
            'PC Team Surprise': pc_team_roll,
            'PC Team': external_data['PC Team'],
            'Monster Team Surprise': monster_team_roll,
            'Monster Team': external_data['Monster Team']
        }


# class DeclareActionsPage(WizardPage):
#     def __init__(self):
#         super().__init__(2, 'Declare Actions')
#         self.set_subtitle('Declare spells and general actions')
#
#         info = '''Remember to have everybody declare their intended actions<br />
# for the coming round. If a spellcaster is using a spell<br />
# then the spell must be declared here.'''
#         text = Widget('DeclareText', 'TextLabel', data=info)
#         self.add_row([text])

def spell_tooltip(spell):
    return f'''\
<b>Reversible: </b>{spell['Reversible']}<br />
<b>Level: </b>{spell['Level']}<br />
<b>Damage: </b>{spell['Damage']}<br />
<b>Range: </b>{spell['Range']}<br />
<b>Duration: </b>{spell['Duration']}<br />
<b>Area of Effect: </b>{spell['Area_of_Effect']}<br />
<b>Components: </b>{spell['Components']}<br />
<b>Casting Time: </b>{spell['Casting_Time']}<br />
<b>Saving Throw: </b>{spell['Saving_Throw']}<br />
<b>Description: </b>{spell['Description']}<br /><br />
'''


class BattleRoundsPage(WizardPage):
    def __init__(self):
        super().__init__(3, 'Battle Rounds')
        self.set_subtitle('Each round is one minute')

        # self.initiative_winner = None
        self.round_number = 1
        self.initiative_roll = '1d6'
        self.spells_table = DbQuery.getTable('Spells')
        self.spells_indexed = {spell['spell_id']: spell for spell in self.spells_table}

        # Define Internal Functions
        def next_round(_fields, _pages, _external):
            self.round_number += 1
            return {
                'Round Text': f'Round {self.round_number}',
                'PC Team Initiative': Dice.rollString(self.initiative_roll),
                'Monster Team Initiative': Dice.rollString(self.initiative_roll),
            }

        def select_spell(field_name, fields):
            spell = fields[f'{field_name} Current']
            return {
                'Casting Time': spell['Casting_Time']
            }

        # Define Widgets
        round_text = Widget('Round Text', 'TextLabel', data=f'Round {self.round_number}')
        next_round_button = Widget('Next Round', 'PushButton')
        open_hp_tracker_button = Widget('Open HP Tracker', 'PushButton', align='Right')
        initiative_text = Widget('Initiative Text', 'TextLabel', data='<b>Initiative</b>', align='Center', col_span=5)
        pc_team = Widget('PC Team Initiative', 'SpinBox', col_span=3)
        monster_team = Widget('Monster Team Initiative', 'SpinBox', col_span=3)
        pc_team_text = Widget('PC Team Text', 'TextLabel', col_span=3)
        monster_team_text = Widget('Monster Team Text', 'TextLabel', col_span=3)
        casting_time_text = Widget('Spell Duration Text', 'TextLabel', data='<b>Casting Time:</b>')
        casting_time = Widget('Casting Time', 'TextLabel')
        pc_spells = Widget('PC Spells', 'ListBox', tool_tip=lambda s, f, p, e: spell_tooltip(s), col_span=2)
        all_spells = Widget('All Spells', 'ListBox', tool_tip=lambda s, f, p, e: spell_tooltip(s), col_span=3)

        # Add Actions
        self.add_action(Action('FillFields', next_round_button, callback=next_round))
        self.add_action(Action('Window', open_hp_tracker_button, callback=open_hp_tracker))
        self.add_action(Action('FillFields', pc_spells, callback=lambda f, p, e: select_spell('PC Spells', f)))
        self.add_action(Action('FillFields', all_spells, callback=lambda f, p, e: select_spell('All Spells', f)))

        # Initialize GUI
        empty = Widget('', 'Empty')
        self.add_row([round_text, next_round_button, empty, empty, open_hp_tracker_button])
        self.add_row([initiative_text])
        self.add_row([pc_team])
        self.add_row([monster_team])
        self.add_row([pc_team_text])
        self.add_row([monster_team_text])
        self.add_row([casting_time_text, casting_time])
        self.add_row([pc_spells, empty, all_spells])

    def initialize_page(self, fields, pages, external_data):
        pc_team_roll = Dice.rollString(self.initiative_roll)
        monster_team_roll = Dice.rollString(self.initiative_roll)

        def get_pc_spells():
            spell_ids = []
            spells = []
            for pc in fields['PC Team']:
                for meta_row in pc['Characters_meta']:
                    if (meta_row['Type'].startswith('DailySpells') or meta_row['Type'] == 'Spellbook')\
                            and meta_row['Entry_ID'] not in spell_ids:
                        spell_ids.append(meta_row['Entry_ID'])
                        spells.append(self.spells_indexed[meta_row['Entry_ID']])
            return spells

        return {
            'PC Team Initiative': pc_team_roll,
            'Monster Team Initiative': monster_team_roll,
            'PC Team Text': f'PC team will act on segment {monster_team_roll}.',
            'Monster Team Text': f'Monster team will act on segment {pc_team_roll}.',
            'PC Spells': get_pc_spells(),
            'All Spells': self.spells_table,
        }

    def on_change(self, fields, pages, external_data):
        return {
            'PC Team Text': f'PC team will act on segment {fields["Monster Team Initiative"]}.',
            'Monster Team Text': f'Monster team will act on segment {fields["PC Team Initiative"]}.'
        }

    # def is_complete(self, fields, pages, external_data):
    #     pc_team_initiative = fields['PC Team Initiative']
    #     monster_team_initiative = fields['Monster Team Initiative']
    #
    #     if pc_team_initiative > monster_team_initiative:
    #         self.initiative_winner = 'PC Team'
    #     elif monster_team_initiative > pc_team_initiative:
    #         self.initiative_winner = 'Monster Team'
    #
    #     return True

    # def get_next_page_id(self, fields, pages, external_data):
    #     if self.initiative_winner == 'PC Team':
    #         return pages['PC Team Attack'].get_page_id()
    #     elif self.initiative_winner == 'Monster Team':
    #         return pages['Monster Team Attack'].get_page_id()
    #     else:
    #         return pages['Simultaneous Attack'].get_page_id()


# class PcTeamAttackPage(WizardPage):
#     def __init__(self):
#         super().__init__(4, 'PC Team Attack')
#         self.set_subtitle('The PC team can attack now')
#
#     def get_next_page_id(self, fields, pages, external_data):
#         if pages['Determine Initiative'].initiative_winner == 'PC Team':
#             return pages['Monster Team Attack'].get_page_id()
#         elif pages['Determine Initiative'].initiative_winner == 'Monster Team':
#             return pages['Wrap Up'].get_page_id()
#         else:
#             return pages['Wrap Up'].get_page_id()
#
#
# class MonsterTeamAttackPage(WizardPage):
#     def __init__(self):
#         super().__init__(5, 'Monster Team Attack')
#         self.set_subtitle('The Monster team can attack now')
#
#     def get_next_page_id(self, fields, pages, external_data):
#         if pages['Determine Initiative'].initiative_winner == 'PC Team':
#             return pages['Wrap Up'].get_page_id()
#         elif pages['Determine Initiative'].initiative_winner == 'Monster Team':
#             return pages['PC Team Attack'].get_page_id()
#         else:
#             return pages['Wrap Up'].get_page_id()
#
#
# class SimultaneousAttackPage(WizardPage):
#     def __init__(self):
#         super().__init__(6, 'Simultaneous Attack')
#         self.set_subtitle('All attacks happen at once')


class WrapUpPage(WizardPage):
    def __init__(self):
        super().__init__(7, 'Wrap Up')
        self.set_subtitle('Calculate XP and Treasure')

        # Define Internal Functions

        # Define Widgets
        wrap_up_text = Widget('Wrap Up Text', 'TextLabel', data='You may now collect your spoils!')
        xp_text = Widget('XP Text', 'TextLabel')
        treasure_text = Widget('Treasure Text', 'TextLabel')

        # Add Actions

        # Initialize GUI
        self.add_row([wrap_up_text])
        self.add_row([xp_text])
        self.add_row([treasure_text])

    def initialize_page(self, fields, pages, external_data):
        enemies = fields['Monster Team']
        xp_text = ', '.join([f'{e["Name"]}: {e["XP Value"]}xp' for e in enemies])
        # treasure_text = '<br />'.join([f'{e["Name"]}: {e["Treasure"]}' for e in enemies])
        treasure_text = ''
        import Treasure
        for enemy in enemies:
            # print([f'{t["Subcategory"]}, {t["Value"]}, {t["Actual Value"]}' for t in Treasure.parse_treasure_text(enemy['Treasure'], wandering=False)['gems']])
            # print([f'{t["Name"]} | {t["Value"]} | {t["Actual Value"]}' for t in Treasure.parse_treasure_text(enemy['Treasure'], wandering=False)['jewellery']])
            print([f'{p["Name"]} | {p["Value"]}' for p in Treasure.parse_treasure_text(enemy['Treasure'], wandering=False)['potions']])
            # print(Treasure.parse_treasure_text(enemy['Treasure'], wandering=False))
        return {
            'XP Text': xp_text,
            'Treasure Text': treasure_text,
        }

    # def get_next_page_id(self, fields, pages, external_data):
    #     if fields['Battle Over'] is False:
    #         return pages['Declare Actions'].get_page_id()
    #     else:
    #         return -1


# base_pattern = r'(\d+d\d+[+-x×]?[\d,]*) ?'
# percent_pattern = r' ?\(?(\d+)?%?\)?'
# cp_pattern = re.compile(base_pattern + 'cp' + percent_pattern)
# sp_pattern = re.compile(base_pattern + 'sp' + percent_pattern)
# ep_pattern = re.compile(base_pattern + 'ep' + percent_pattern)
# gp_pattern = re.compile(base_pattern + 'gp' + percent_pattern)
# pp_pattern = re.compile(base_pattern + 'pp' + percent_pattern)
# gems_pattern = re.compile(base_pattern + 'gems' + percent_pattern)
# jewellery_pattern = re.compile(base_pattern + 'jewellery' + percent_pattern)
# potions_pattern = re.compile(base_pattern + 'potions' + percent_pattern)
#
#
# def get_treasure_list(match):
#     return [Dice.rollString(m[0]) for m in match if not m[1] or int(m[1]) >= Dice.randomInt(1, 100)]
#
#
# def parse_treasure_text(treasure_text, wandering=True):
#     treasure_split = treasure_text.split(';')
#     if len(treasure_split) == 1:
#         individual = treasure_split[0]
#         lair = None
#     else:
#         if 'individual' in treasure_split[0].lower():
#             individual = treasure_split[0]
#             lair = treasure_split[1]
#         else:
#             lair = treasure_split[0]
#             individual = treasure_split[1]
#     if wandering:
#         t = individual
#     else:
#         t = lair or ''
#     cp_match = cp_pattern.findall(t)
#     sp_match = sp_pattern.findall(t)
#     ep_match = ep_pattern.findall(t)
#     gp_match = gp_pattern.findall(t)
#     pp_match = pp_pattern.findall(t)
#
#     return {
#         'cp': sum(get_treasure_list(cp_match)),
#         'sp': sum(get_treasure_list(sp_match)),
#         'ep': sum(get_treasure_list(ep_match)),
#         'gp': sum(get_treasure_list(gp_match)),
#         'pp': sum(get_treasure_list(pp_match))
#     }


class HpTracker(Manage):
    def __init__(self, characters, encounter_id):
        super().__init__(title='HP Tracker', modality='unblock')

        pcs = DbQuery.getTable('Characters')
        encounters = DbQuery.getTable('Encounters')

        pcs_indexed = {pc['unique_id']: pc for pc in pcs}
        encounters_indexed = {e['unique_id']: e for e in encounters}

        current_encounter = encounters_indexed[encounter_id]
        enemies_serialized = current_encounter['enemy_team']
        enemies = json.loads(enemies_serialized)

        # Define Internal Functions
        def get_meta_indexed(char):
            meta_indexed = {}
            for row in char['Characters_meta']:
                meta_type = row['Type']
                meta_list = meta_indexed.get(meta_type, [])
                meta_list.append(row)
                meta_indexed[meta_type] = meta_list
            return meta_indexed

        def get_character_hp(char):
            char_id = char['unique_id']
            char = pcs_indexed[char_id]
            meta_indexed = get_meta_indexed(char)

            return int(meta_indexed.get('Current HP', [{'Data': char['HP']}])[0]['Data'])

        def get_enemy_hp(en):
            if en['TableName'] == 'Monsters':
                return en['HP']
            return get_character_hp(en)

        def save_character_hp(char_id, new_hp):
            meta_indexed = get_meta_indexed(pcs_indexed[char_id])
            cur_hp_meta_row = meta_indexed.get('Current HP', None)

            if cur_hp_meta_row is None:
                cur_hp_insert_row = (char_id, 'Current HP', None, new_hp, None)
                DbQuery.insertRow('Characters_meta', cur_hp_insert_row)
                DbQuery.commit()
            else:
                DbQuery.update_cols('Characters_meta', 'character_id', char_id,
                                    ('Data',), (new_hp,), 'Type', 'Current HP')
                DbQuery.commit()

        def adjust_character_hp(dialog_return, fields, char_id):
            new_hp = dialog_return + fields[f'Current HP {char_id}']
            save_character_hp(char_id, new_hp)

            return {
                f'Current HP {char_id}': new_hp,
            }

        def adjust_enemy_hp(dialog_return, fields, enemy_index):
            new_hp = dialog_return + fields[f'Current HP {enemy_index}']
            en = enemies[enemy_index]
            if en['TableName'] == 'Monsters':
                enemies[enemy_index]['HP'] = new_hp
                serialized_enemies = json.dumps(enemies)
                DbQuery.update_cols('Encounters', 'unique_id', encounter_id,
                                    ('enemy_team',), (serialized_enemies,))
                DbQuery.commit()
            else:
                char_id = en['unique_id']
                save_character_hp(char_id, new_hp)

            return {
                f'Current HP {enemy_index}': new_hp,
            }

        # Define Widgets
        tools_menu = Menu('&Tools')
        tools_menu.add_action(Action('Window', Widget('&Dice Roller', 'MenuAction'), callback=lambda x: DiceWindow()))
        self.add_menu(tools_menu)

        pc_team_header = Widget('PC Team Header', 'TextLabel', data='<b>PC Team</b>', align='Center', col_span=3)
        self.add_row([pc_team_header])
        for character in characters:
            character_id = character['unique_id']
            character_name = Widget('Character Name', 'TextLabel', data=f'<b>{character["Name"]}</b>')
            current_hp = Widget(f'Current HP {character_id}_', 'SpinBox',
                                enable_edit=False, data=get_character_hp(character))
            adjust_hp = Widget(f'Adjust HP {character_id}', 'PushButton', data='Adjust HP')
            # Add Actions
            self.add_action(Action('EntryDialog', adjust_hp, current_hp,
                                   callback=callback_factory_2param(adjust_character_hp, character_id)))
            # Initialize GUI
            self.add_row([character_name, current_hp, adjust_hp])

        enemy_team_header = Widget('Enemy Team Header', 'TextLabel',
                                   data='<b>Enemy Team</b>', align='Center', col_span=3)
        self.add_row([enemy_team_header])
        for i, enemy in enumerate(enemies):
            enemy_name = Widget('Enemy Name', 'TextLabel', data=f'<b>{enemy["Name"]}</b>')
            current_hp = Widget(f'Current HP {i}_', 'SpinBox', enable_edit=False, data=get_enemy_hp(enemy))
            adjust_hp = Widget(f'Adjust HP {i}', 'PushButton', data='Adjust HP')
            # Add Actions
            self.add_action(Action('EntryDialog', adjust_hp, current_hp,
                                   callback=callback_factory_2param(adjust_enemy_hp, i)))
            # Initialize GUI
            self.add_row([enemy_name, current_hp, adjust_hp])
