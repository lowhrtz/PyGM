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
        super().__init__('Encounter Tracker')

        self.add_wizard_page(EncounterIntro())
        self.add_wizard_page(SurprisePage())


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
                enemies.append(enemy)
        serialized_enemies = json.dumps(enemies)
        DbQuery.insertRow('Encounters', (self.encounter_id, '', serialized_enemies))
        DbQuery.commit()


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
Surprise: {surprise}
'''

        def enemy_tool_tip(enemy, _fields, _pages, _external):
            if enemy['TableName'] == 'Monsters':
                special_attacks = enemy['Special_Attacks']
                special_defences = enemy['Special_Defences']
                description = enemy['Description']
                return f'''\
<b>{enemy['Name']}</b><br />
Special Attacks: {special_attacks}<br />
Special Defences: {special_defences}<br /><br />
{description}
'''
            else:
                return pc_tool_tip(enemy, _fields, _pages, _external)

        # character_windows = {}

        # def open_character_tracker(fields, _pages, _external):
        #     characters = fields['PC Team']
        #     character_window = CharacterTracker(characters)
        #     return character_window
        #
        # def open_enemy_tracker(_fields, pages, _external):
        #     # enemies = fields['Monster Team']
        #     enemies_window = EnemyTracker(pages['Encounter Tracker'].encounter_id)
        #     return enemies_window

        def open_hp_tracker(fields, pages, _external):
            characters = fields['PC Team']
            encounter_id = pages['Encounter Tracker'].encounter_id
            return HpTracker(characters, encounter_id)

        # Define Widgets
        pc_team_surprise = Widget('PC Team Surprise', 'SpinBox')
        pc_team = Widget('PC Team', 'ListBox', tool_tip=pc_tool_tip)
        monster_team_surprise = Widget('Monster Team Surprise', 'SpinBox')
        monster_team = Widget('Monster Team', 'ListBox', tool_tip=enemy_tool_tip)

        # Add Actions
        self.add_action(Action('Window', pc_team, callback=open_hp_tracker))
        self.add_action(Action('Window', monster_team, callback=open_hp_tracker))

        # Initialize GUI
        self.add_row([pc_team_surprise])
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


class HpTracker(Manage):
    def __init__(self, characters, encounter_id):
        super().__init__(modality='unblock')

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


# class CharacterTracker(Manage):
#     def __init__(self, characters):
#         super().__init__(modality='unblock')
#
#         pcs = DbQuery.getTable('Characters')
#         pcs_indexed = {pc['unique_id']: pc for pc in pcs}
#
#         # Define Internal Functions
#         def get_meta_indexed(char):
#             meta_indexed = {}
#             for row in char['Characters_meta']:
#                 meta_type = row['Type']
#                 meta_list = meta_indexed.get(meta_type, [])
#                 meta_list.append(row)
#                 meta_indexed[meta_type] = meta_list
#             return meta_indexed
#
#         def get_character_hp(char):
#             char_id = char['unique_id']
#             char = pcs_indexed[char_id]
#             meta_indexed = get_meta_indexed(char)
#
#             return int(meta_indexed.get('Current HP', [{'Data': char['HP']}])[0]['Data'])
#
#         def adjust_character_hp(dialog_return, fields, char_id):
#             new_hp = dialog_return + fields[f'Current HP {char_id}']
#             meta_indexed = get_meta_indexed(pcs_indexed[char_id])
#             cur_hp_meta_row = meta_indexed.get('Current HP', None)
#
#             if cur_hp_meta_row is None:
#                 cur_hp_insert_row = (char_id, 'Current HP', None, new_hp, None)
#                 DbQuery.insertRow('Characters_meta', cur_hp_insert_row)
#                 DbQuery.commit()
#             else:
#                 DbQuery.update_cols('Characters_meta', 'character_id', char_id,
#                                     ('Data',), (new_hp,), 'Type', 'Current HP')
#                 DbQuery.commit()
#
#             return {
#                 f'Current HP {char_id}': new_hp,
#             }
#
#         # Define Widgets
#
#         for character in characters:
#             character_id = character['unique_id']
#             character_name = Widget('Character Text', 'TextLabel', data=f'<b>{character["Name"]}</b>')
#             current_hp = Widget(f'Current HP {character_id}_', 'SpinBox',
#                                 enable_edit=False, data=get_character_hp(character))
#             adjust_hp = Widget(f'Adjust HP {character_id}', 'PushButton', data='Adjust HP')
#             # Add Actions
#             self.add_action(Action('EntryDialog', adjust_hp, current_hp,
#                                    callback=callback_factory_2param(adjust_character_hp, character_id)))
#             # Initialize GUI
#             self.add_row([character_name, current_hp, adjust_hp])
#
#
# class EnemyTracker(Manage):
#     def __init__(self, encounter_id):
#         super().__init__(modality='unblock')
#
#         # monsters = DbQuery.getTable('Monsters')
#         # characters = DbQuery.getTable('Characters')
#         encounters = DbQuery.getTable('Encounters')
#
#         # monsters_indexed = {m['unique_id']: m for m in monsters}
#         # characters_indexed = {c['unique_id']: c for c in characters}
#         encounters_indexed = {e['unique_id']: e for e in encounters}
#         current_encounter = encounters_indexed[encounter_id]
#         enemies_serialized = current_encounter['enemy_team']
#         enemies = json.loads(enemies_serialized)
#
#         # Define Internal Functions
#         def get_enemy_hp(en):
#             if en['TableName'] == 'Monsters':
#                 return en['HP']
#             return 0
#
#         # Define Widgets
#         for i, enemy in enumerate(enemies):
#             enemy_name = Widget('Enemy Text', 'TextLabel', data=f'<b>{enemy["Name"]}</b>')
#             enemy_hp = Widget(f'Enemy HP {i}_', 'SpinBox',
#                               enable_edit=False, data=get_enemy_hp(enemy))
#             # Add Actions
#
#             # Initialize GUI
#             self.add_row([enemy_name, enemy_hp])
