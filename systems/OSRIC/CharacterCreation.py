import base64
import os
import re
import time
import DbQuery
# import Dice
import SystemSettings
from decimal import Decimal
from Common import find_image
from GuiDefs import *


class CharacterCreationWizard(Wizard):

    def __init__(self):
        super().__init__('Character Creator')

        self.add_wizard_page(IntroPage())
        self.add_wizard_page(ChooseMethodPage())
        self.add_wizard_page(RollAttributesPage())
        self.add_wizard_page(ChooseRacePage())
        self.add_wizard_page(ChooseClassPage())
        self.add_wizard_page(SpellbookPage())
        self.add_wizard_page(DailySpellsPage())
        self.add_wizard_page(DailySpellsPage2())
        self.add_wizard_page(ProficiencyPage())
        self.add_wizard_page(EquipmentPage())
        self.add_wizard_page(InfoPage())
        self.add_wizard_page(ChoosePortraitPage())
        self.add_wizard_page(ReviewPage())

    def accept(self, fields, pages, external_data):
        full_class = pages['Choose Class'].get_full_class(fields['Classes Current'])
        if 'classes' in full_class:
            level = '/'.join('1' for _ in full_class['classes'])
            classes = '/'.join(cl['unique_id'] for cl in full_class['classes'])
            xp = '/'.join('0' for _ in full_class['classes'])
        else:
            level = '1'
            classes = full_class['unique_id']
            xp = '0'
        unique_id = '{}-{}-{}'.format(fields['Name'].lower().replace(' ', '_'), full_class['unique_id'],
                                      time.time())
        character_dict = {
            'unique_id': unique_id,
            'Name': fields['Name'],
            'Level': level,
            'XP': xp,
            'Gender': fields['Gender'],
            'Alignment': fields['Alignment'],
            'Classes': classes,
            'Race': fields['Races Current']['unique_id'],
            'HP': pages['Review'].hp,
            'Age': pages['Review'].age,
            'Height': '{}ft {}in'.format(pages['Review'].height[0], pages['Review'].height[1]),
            'Weight': '{} lbs'.format(pages['Review'].weight),
            'Portrait': fields['Portrait'],
            'Portrait_Image_Type': 'jpg',
            'STR': pages['Review'].attr_dict['STR'],
            'INT': pages['Review'].attr_dict['INT'],
            'WIS': pages['Review'].attr_dict['WIS'],
            'DEX': pages['Review'].attr_dict['DEX'],
            'CON': pages['Review'].attr_dict['CON'],
            'CHA': pages['Review'].attr_dict['CHA'],
        }

        def make_meta_row(data_list):
            meta_row = {
                'character_id': data_list[0],
                'Type': data_list[1],
                'Entry_ID': data_list[2],
                'Data': data_list[3],
                'Notes': data_list[4]
            }
            return meta_row

        character_dict['Characters_meta'] = []

        for e in fields['Equipment']:
            equip_data = [
                unique_id,
                'Equipment',
                e['unique_id'],
                '',
                '',
            ]
            character_dict['Characters_meta'].append(make_meta_row(equip_data))

        money_dict = SystemSettings.get_coinage_from_float(pages['Buy Equipment'].current_money)
        for denomination in list(money_dict.keys()):
            money_data = [
                unique_id,
                'Treasure',
                denomination,
                money_dict[denomination],
                '',
            ]
            character_dict['Characters_meta'].append(make_meta_row(money_data))

        for p in fields['Proficiencies']:
            if p not in pages['Proficiencies'].specialised_list:
                p_data = [
                    unique_id,
                    'Proficiency',
                    p['unique_id'],
                    'P',
                    '',
                ]
                character_dict['Characters_meta'].append(make_meta_row(p_data))

        for s in pages['Proficiencies'].specialised_list:
            if s not in pages['Proficiencies'].double_specialised_list:
                s_data = [
                    unique_id,
                    'Proficiency',
                    s['unique_id'],
                    'S',
                    '',
                ]
                character_dict['Characters_meta'].append(make_meta_row(s_data))

        for ds in pages['Proficiencies'].double_specialised_list:
            ds_data = [
                unique_id,
                'Proficiency',
                ds['unique_id'],
                '2XS',
                '',
            ]
            character_dict['Characters_meta'].append(make_meta_row(ds_data))

        for s in fields['Spellbook']:
            s_data = [
                unique_id,
                'Spellbook',
                s['spell_id'],
                '',
                '',
            ]
            character_dict['Characters_meta'].append(make_meta_row(s_data))

        for s in fields['Daily Spells']:
            s_data = [
                unique_id,
                'DailySpells',
                s['spell_id'],
                '',
                '',
            ]
            character_dict['Characters_meta'].append(make_meta_row(s_data))

        for s in fields['Daily Spells2']:
            s_data = [
                unique_id,
                'DailySpells2',
                s['spell_id'],
                '',
                '',
            ]
            character_dict['Characters_meta'].append(make_meta_row(s_data))
        return character_dict


class IntroPage(WizardPage):

    def __init__(self):
        super().__init__(0, 'Character Creator')

        self.set_subtitle('Character Creation Wizard')

        text = Widget('IntroText', 'TextLabel', align='Center', data='Welcome to the Character Creation Wizard')
        self.add_row([text, ])

        text2 = Widget('Intro Text2', 'TextLabel', align='Center', data='Click <b>Next</b> to continue.')
        self.add_row([text2, ])


class ChooseMethodPage(WizardPage):

    def __init__(self):
        super().__init__(1, 'Choose Method')

        self.set_subtitle('You must choose but choose wisely.')

        empty = Widget('', 'Empty')
        self.add_row([empty, ])
        self.add_row([empty, ])

        text = Widget('ChooseText', 'TextLabel', align='Center', data='How do you want to create your character?')
        self.add_row([text, ])

        choices = ['Roll Attributes First', 'Choose Race, Class, etc. First', ]
        radio = Widget('ChooseMethod', 'RadioButton', align='Center', data=choices)
        self.add_row([radio, ])

    def get_next_page_id(self, fields, pages, external_data):
        chosen_id = fields['ChooseMethod']
        if chosen_id == 0:
            return pages['Roll Attributes'].get_page_id()
        else:
            pages['Roll Attributes'].attr_dict = None
            return pages['Choose Race'].get_page_id()


class RollAttributesPage(RollMethodsPage):

    def __init__(self):
        self.attributes = attributes = [attr[0] for attr in SystemSettings.attributes]
        # self.method_names = ['Classic', 'Classic - Drop Lowest', 'Rearrange', 'Rearrange - Drop Lowest']
        super().__init__(2, 'Roll Attributes', attributes)

        self.races = DbQuery.getTable('Races')
        self.classes = DbQuery.getTable('Classes')

    # def fill_attribute_fields(self, fields, pages, external_data):
    #     # print(fields['Methods'])
    #     fill = {}
    #     for attr in self.attributes:
    #         if fields['Methods'].endswith('Drop Lowest'):
    #             rolls = [Dice.rollString('d6') for _ in range(4)]
    #             # print(rolls)
    #             rolls.remove(min(rolls))
    #             # print(rolls)
    #             fill[attr] = sum(rolls)
    #         else:
    #             fill[attr] = Dice.rollString('3d6')
    #
    #     return fill

    def is_complete(self, fields, pages, external_data):
        # print(fields.keys())
        self.attr_dict = {attr: fields[attr] for attr in self.attributes}
        for attr in self.attributes:
            attr_field = fields[attr]
            if len(attr_field) == 0 or attr_field.isspace():
                # print('False')
                return False

        races = self.get_available_races()
        for race in races:
            if self.has_classes_available(race):
                # print('False')
                return True

        # print('True')
        return False

    def get_available_races(self):
        # races = DbQuery.getTable('Races')
        races = self.races
        attr_dict = self.attr_dict
        if attr_dict is None:
            return races
        available_races = []
        for race in races:
            allowed = True
            for attr in self.attributes:
                attr_cap = attr.capitalize()
                min_score = race['Minimum_' + attr_cap]
                max_score = race['Maximum_' + attr_cap]
                if not min_score <= int(attr_dict[attr]) <= max_score:
                    allowed = False
            if allowed:
                available_races.append(race)

        return available_races

    def find_class_record(self, unique_id):
        for cla in self.classes:
            if cla['unique_id'] == unique_id.strip():
                return cla

    def class_allowed(self, cla):
        if self.attr_dict is None:
            return True

        minimum_scores = [i.strip() for i in cla['Minimum_Scores'].split(',')]
        for score in minimum_scores:
            score_key = score[:3].upper()
            score_value = int(score[3:].strip())
            # if score_key.strip() == 'CHA':
            #     print(self.attr_dict[score_key], score_value)
            if int(self.attr_dict[score_key]) < score_value:
                return False

        return True

    def has_classes_available(self, race):
        class_options = None
        for races_meta in race['Races_meta']:
            if races_meta['Type'] == 'class' and races_meta['Subtype'] == 'permitted class options':
                class_options_string = races_meta['Modified']
                class_options = class_options_string.split(',')
        if class_options is None:
            class_options = [cl['unique_id'] for cl in self.classes]

        for class_option in class_options:
            if '/' in class_option:
                option_allowed = True
                for cl in class_option.split('/'):
                    if not self.class_allowed(self.find_class_record(cl)):
                        option_allowed = False
                        break
                if option_allowed:
                    return True
            else:
                if self.class_allowed(self.find_class_record(class_option)):
                    return True
        return False


class ChooseRacePage(WizardPage):

    def __init__(self):
        super().__init__(3, 'Choose Race')

        self.set_subtitle('Choose from the availale races.')

        race_image = Widget('RaceImage', 'Image', data=resources.noImage_jpg)
        race_list = Widget('Races_', 'ListBox')
        self.add_row([race_image, race_list])
        self.add_action(Action('FillFields', race_list, callback=self.change_image))
        self.system_path = SystemSettings.SYSTEM_PATH

    def change_image(self, fields, pages, external_data):
        current_race = fields['Races Current']
        # print(current_race)
        if current_race is None:
            return {}

        with open(find_image(self.system_path, 'Races', current_race['unique_id']), 'rb') as image_file:
            data = base64.b64encode(image_file.read())
        return {'RaceImage': data.decode()}

    def initialize_page(self, fields, pages, external_data):
        # print(pages['Roll Attributes'].get_available_races())
        return {'Races': pages['Roll Attributes'].get_available_races()}


class ChooseClassPage(WizardPage):

    def __init__(self):
        super().__init__(4, 'Choose Class')

        self.set_subtitle('Choose from the available classes.')
        class_image = Widget('ClassImage', 'Image', data=resources.noImage_jpg)
        class_list = Widget('Classes_', 'ListBox')
        self.add_row([class_image, class_list])
        self.add_action(Action('FillFields', class_list, callback=self.change_image))
        self.system_path = SystemSettings.SYSTEM_PATH
        self.roll_page = None
        self.full_available_classes = None
        self.spell_classes = 0
        self.wizard_category = None
        self.other_spellcaster_category = None
        self.other_spellcaster_category2 = None

    def change_image(self, fields, pages, external_data):
        current_class = fields['Classes Current']
        if current_class is None:
            return {}

        with open(find_image(self.system_path, 'Classes', current_class), 'rb') as image_file:
            data = base64.b64encode(image_file.read())
        return {'ClassImage': data.decode()}

    def initialize_page(self, fields, pages, external_data):
        self.roll_page = pages['Roll Attributes']
        return {'Classes': self.get_available_classes(fields['Races Current'])}

    def get_next_page_id(self, fields, pages, external_data):
        self.wizard_category = None
        self.other_spellcaster_category = None
        if fields['Classes Current'] is None:
            return -2
        cl = self.get_full_class(fields['Classes Current'])
        if 'classes' in cl:
            classes = cl['classes']
        else:
            classes = [cl]
        self.spell_classes = 0
        for cla in classes:
            if cla['Category'] == 'wizard':
                self.wizard_category = cla
                self.spell_classes += 1
            elif cla['Primary_Spell_List'] != 'None':
                if self.other_spellcaster_category is None:
                    self.other_spellcaster_category = cla
                else:
                    self.other_spellcaster_category2 = cla
                self.spell_classes += 1
        if self.wizard_category:
            return pages['Spellbook'].get_page_id()
        elif self.other_spellcaster_category and SystemSettings.has_spells_at_level(1, self.other_spellcaster_category):
            return pages['Daily Spells'].get_page_id()
        else:
            return pages['Proficiencies'].get_page_id()

    def get_full_class(self, unique_id):
        for cl in self.full_available_classes:
            if cl['unique_id'] == unique_id:
                return cl

    def get_available_classes(self, race):
        classes = self.roll_page.classes
        self.full_available_classes = []
        class_options = []
        missing_permitted_class_options = True
        for races_meta in race['Races_meta']:
            if races_meta['Type'] == 'class' and races_meta['Subtype'] == 'permitted class options':
                missing_permitted_class_options = False
                class_options_string = races_meta['Modified']
                for class_option in class_options_string.split(','):
                    class_option = class_option.strip()
                    if '/' in class_option:
                        multiclass = {
                            'unique_id': class_option.replace('/', '_'),
                            'Name': class_option.title().replace('_', ' '),
                            # 'Primary_Spell_List': [],
                            'classes': [],
                        }
                        multiclass_allowed = True
                        for cl in class_option.split('/'):
                            class_record = self.roll_page.find_class_record(cl)
                            if not self.roll_page.class_allowed(class_record):
                                multiclass_allowed = False
                                break
                            multiclass['classes'].append(class_record)
                            # if class_record['Primary_Spell_List'] != 'None' and \
                            #         SystemSettings.has_spells_at_level(1, class_record):
                            #     multiclass['Primary_Spell_List'].append(class_record['Primary_Spell_List'])
                        if multiclass_allowed:
                            self.full_available_classes.append(multiclass)
                            class_item = (multiclass['Name'], multiclass['unique_id'])
                            class_options.append(class_item)
                    else:
                        class_item = self.roll_page.find_class_record(class_option)
                        if self.roll_page.class_allowed(class_item):
                            self.full_available_classes.append(class_item)
                            class_options.append((class_item['Name'], class_item['unique_id']))
        if missing_permitted_class_options:
            class_options = [(normal_class['Name'], normal_class['unique_id']) for normal_class in classes
                             if self.roll_page.class_allowed(normal_class)]
            self.full_available_classes = [normal_class for normal_class in classes
                                           if self.roll_page.class_allowed(normal_class)]

        return class_options


class SpellbookPage(WizardPage):
    def __init__(self):
        super().__init__(5, 'Spellbook')
        self.set_subtitle('Choose a spell to add to your spellbook.')

        self.orig_spells = []
        self.spell_slots = None
        self.spells_table = DbQuery.getTable('Spells')

        sb_data = {
            'fill_avail': self.fill_spells,
            'slots': self.get_spell_slots,
            'slots_name': 'Spells',
            'category_field': 'Level',
            'tool_tip': self.get_tool_tip,
            'add': self.add_spell,
            'remove': self.remove_spell,
        }
        sb_list = Widget('Spellbook', 'DualList', align='Center', data=sb_data)

        self.add_row([sb_list, ])

    def fill_spells(self, owned_items, fields, pages, external_data):
        self.orig_spells = owned_items
        unique_id = pages['Choose Class'].wizard_category['unique_id']
        spells_table = [spell for spell in self.spells_table if spell['Type'] == unique_id]
        cl = pages['Choose Class'].wizard_category
        # level = int(levels[classes.index(cl['unique_id'])])
        level = 1
        meta_row = [row for row in cl['Classes_meta'] if row['Level'].isdigit() and int(row['Level']) == level][0]
        highest_spell_level = 0
        for spell_level in range(1, 10):
            sl_column_name = 'Level_{}_Spells'.format(spell_level)
            if meta_row[sl_column_name] > 0:
                highest_spell_level = spell_level

        available_spells = [spell for spell in spells_table
                            if spell['Level'] == highest_spell_level and spell not in owned_items]
        return available_spells

    def get_spell_slots(self, fields, pages, external_data):
        return self.spell_slots

    def get_tool_tip(self, item, fields, pages, external_data):
        return '<b>{}</b><br />{}'.format(item['Name'], item['Description'])

    def add_spell(self, spell, fields, pages, external_data):
        if int(self.spell_slots) > 0:
            self.spell_slots = str(int(self.spell_slots) - 1)
            return {
                'valid': True,
                'slots_new_value': self.spell_slots,
                'remove': True,
                'new_display': spell['Name'],
            }
        return {}

    def remove_spell(self, spell, fields, pages, external_data):
        if spell in self.orig_spells:
            return {}

        # if self.spell_slots == '0':
        #     self.spell_slots = '1'
        self.spell_slots = str(int(self.spell_slots) + 1)
        return {
            'valid': True,
            'slots_new_value': self.spell_slots,
            'replace': True,
            'new_display': spell['Name'],
        }

    def initialize_page(self, fields, pages, external_data):
        unique_id = pages['Choose Class'].wizard_category['unique_id']
        level = 1
        spells_table = [spell for spell in self.spells_table
                        if spell['Type'] == unique_id and spell['Level'] == level]
        spellbook_ids = []
        self.spell_slots = '2'
        if unique_id == 'magic_user':
            self.spell_slots = '1'
            spellbook_ids.append('read_magic')
        for _ in range(2):
            while True:
                random_spell_index = Dice.randomInt(0, len(spells_table) - 1)
                random_spell_id = spells_table[random_spell_index]['spell_id']
                if random_spell_id not in spellbook_ids:
                    spellbook_ids.append(random_spell_id)
                    break

        spellbook = []
        for spell in spells_table:
            if spell['spell_id'] in spellbook_ids:
                spellbook.append(spell)
        return {'Spellbook': spellbook}

    def is_complete(self, fields, pages, external_data):
        if self.spell_slots == '0':
            return True
        return False

    def get_next_page_id(self, fields, pages, external_data):
        return pages['Daily Spells'].get_page_id()


class DailySpellsPage(WizardPage):

    def __init__(self, page_id=6, title='Daily Spells'):
        super().__init__(page_id, title)

        ds_data = {
            'fill_avail': self.fill_spells,
            'slots': self.get_spell_slots,
            'slots_name': 'Spells',
            'category_field': 'Level',
            'tool_tip': self.get_tool_tip,
            'add': self.add_spell,
            'remove': self.remove_spell,
        }
        if page_id == 6:
            self.field_name = field_name = 'Daily Spells'
        else:
            self.field_name = field_name = 'Daily Spells2'
        ds_list = Widget(field_name, 'DualList', data=ds_data)
        self.add_row([ds_list, ])

        self.attr_dict = None
        self.spell_slots = None

    def initialize_page(self, fields, pages, external_data):
        ra_attr_dict = pages['Roll Attributes'].attr_dict
        race = fields['Races Current']
        full_class = pages['Choose Class'].get_full_class(fields['Classes Current'])
        self.attr_dict = self.roll_attributes(ra_attr_dict, race, full_class)
        wizard_category = pages['Choose Class'].wizard_category
        other_spellcaster_category = pages['Choose Class'].other_spellcaster_category
        class_name = ''
        if wizard_category:
            class_name = wizard_category['Name']
            self.spell_slots = [meta_row['Level_1_Spells'] for meta_row in wizard_category['Classes_meta']
                                if meta_row['Type'] == 'xp table' and meta_row['Level'] == '1'][0]
        elif other_spellcaster_category:
            class_name = other_spellcaster_category['Name']
            self.spell_slots = [meta_row['Level_1_Spells'] for meta_row in other_spellcaster_category['Classes_meta']
                                if meta_row['Type'] == 'xp table' and meta_row['Level'] == '1'][0]
            if other_spellcaster_category['Wis_Spell_Bonus'].lower() == 'yes':
                _, spell_bonus, _ = SystemSettings.get_attribute_bonuses('WIS', self.attr_dict['WIS'])
                spell_bonuses = spell_bonus.split('/')
                self.spell_slots += int(spell_bonuses[0])
        self.set_subtitle('Choose Daily {} Spells'.format(class_name))

        return {self.field_name: []}

    def is_complete(self, fields, pages, external_data):
        if self.spell_slots == '0':
            return True
        else:
            return False

    def get_next_page_id(self, fields, pages, external_data):
        other_spellcaster_category2 = pages['Choose Class'].other_spellcaster_category2
        other_spellcaster_category2_has_spells = False
        if other_spellcaster_category2:
            other_spellcaster_category2_has_spells = SystemSettings.has_spells_at_level(1, other_spellcaster_category2)
        if pages['Choose Class'].spell_classes > 1 and\
                (pages['Choose Class'].wizard_category or other_spellcaster_category2_has_spells):
            return pages['More Daily Spells'].get_page_id()
        return pages['Proficiencies'].get_page_id()

    def fill_spells(self, owned_items, fields, pages, external_data):
        if pages['Choose Class'].wizard_category:
            spells_table = [spell for spell in fields['Spellbook']]
        else:
            spells_table = [spell for spell in pages['Spellbook'].spells_table
                            if spell['Type'] == pages['Choose Class'].other_spellcaster_category['Primary_Spell_List']
                            and spell['Level'] == 1]
        avail_spells = [spell for spell in spells_table if spell not in owned_items]
        return avail_spells

    def get_spell_slots(self, fields, pages, external_data):
        return self.spell_slots

    def get_tool_tip(self, item, fields, pages, external_data):
        return pages['Spellbook'].get_tool_tip(item, fields, pages, external_data)

    def add_spell(self, spell, fields, pages, external_data):
        if int(self.spell_slots) > 0:
            self.spell_slots = str(int(self.spell_slots) - 1)
            return {
                'valid': True,
                'slots_new_value': self.spell_slots,
                # 'remove': True,
                'new_display': spell['Name'],
            }
        return {}

    def remove_spell(self, spell, fields, pages, external_data):
        self.spell_slots = str(int(self.spell_slots) + 1)
        return {
            'valid': True,
            'slots_new_value': self.spell_slots,
            # 'replace': True,
            'new_display': spell['Name'],
        }

    def roll_attributes(self, wiz_attr_dict, race, full_class):
        is_warrior = False
        if 'classes' in full_class:
            for cl in full_class['classes']:
                if cl['Category'].lower() == 'warrior':
                    is_warrior = True
        else:
            if full_class['Category'].lower() == 'warrior':
                is_warrior = True

        attr_dict = {}
        min_dict = {}
        if not wiz_attr_dict:
            if 'classes' in full_class:
                for cl in full_class['classes']:
                    min_scores_string = cl['Minimum_Scores']
                    min_scores_list = [score.strip() for score in min_scores_string.split(',')]
                    for min_score in min_scores_list:
                        min_score_split = min_score.split()
                        attr = min_score_split[0]
                        min_score = int(min_score_split[1])
                        if attr not in min_dict:
                            min_dict[attr] = min_score
                        else:
                            min_dict[attr] = max(min_score, min_dict[attr])
            else:
                min_scores_string = full_class['Minimum_Scores']
                min_scores_list = [score.strip() for score in min_scores_string.split(',')]
                for min_score in min_scores_list:
                    min_score_split = min_score.split()
                    attr = min_score_split[0]
                    min_score = int(min_score_split[1])
                    min_dict[attr] = min_score

            if len(min_dict) < 6:
                for attr in [attr[0] for attr in SystemSettings.attributes]:
                    if attr.title() not in min_dict:
                        min_dict[attr.title()] = 3

            for attr in min_dict:
                minimum = max(min_dict[attr], race['Minimum_' + attr])
                maximum = race['Maximum_' + attr]
                score = Dice.randomInt(minimum, maximum)
                attr_dict[attr.upper()] = str(score)
        else:
            attr_dict = self.adjust_attributes(wiz_attr_dict, race)

        for attr in attr_dict:
            if attr.lower() == 'str' and attr_dict[attr] == '18' and is_warrior:
                score = 18
                exceptional_strength = Dice.randomInt(1, 99) / float(100)
                attr_dict[attr] = '{0:.2f}'.format(score + exceptional_strength)

        return attr_dict

    def adjust_attributes(self, attr_dict, race_dict):
        for meta_row in race_dict['Races_meta']:
            if meta_row['Type'] == 'ability' and meta_row['Subtype'] == 'attribute':
                attr_to_modify = meta_row['Modified'].upper()[:3]
                modifier = meta_row['Modifier']
                attr_orig_score = attr_dict[attr_to_modify]
                new_score = eval(attr_orig_score + modifier)
                attr_dict[attr_to_modify] = str(new_score)
        return attr_dict


class DailySpellsPage2(DailySpellsPage):

    def __init__(self):
        super().__init__(7, 'More Daily Spells')

    def initialize_page(self, fields, pages, external_data):
        other_spellcaster_category = pages['Choose Class'].other_spellcaster_category
        other_spellcaster_category2 = pages['Choose Class'].other_spellcaster_category2
        if other_spellcaster_category2:
            other_spellcaster_category = other_spellcaster_category2
        class_name = other_spellcaster_category['Name']
        self.spell_slots = [meta_row['Level_1_Spells'] for meta_row in other_spellcaster_category['Classes_meta']
                            if meta_row['Type'] == 'xp table' and meta_row['Level'] == '1'][0]
        if other_spellcaster_category['Wis_Spell_Bonus'].lower() == 'yes':
            _, spell_bonus, _ = SystemSettings.get_attribute_bonuses('WIS', pages['Daily Spells'].attr_dict['WIS'])
            spell_bonuses = spell_bonus.split('/')
            self.spell_slots += int(spell_bonuses[0])
        self.set_subtitle('Choose Daily {} Spells'.format(class_name))
        return {self.field_name: []}

    def get_next_page_id(self, fields, pages, external_data):
        return pages['Proficiencies'].get_page_id()

    def fill_spells(self, owned_items, fields, pages, external_data):
        spells_table = [spell for spell in pages['Spellbook'].spells_table
                        if spell['Type'] == pages['Choose Class'].other_spellcaster_category['Primary_Spell_List']
                        and spell['Level'] == 1]
        avail_spells = [spell for spell in spells_table if spell not in owned_items]
        return avail_spells


class ProficiencyPage(WizardPage):

    def __init__(self):
        super().__init__(8, 'Proficiencies')

        self.set_subtitle('Choose your proficiencies.')

        profs_data = {
            'fill_avail': self.fill_proficiencies,
            'slots': self.get_slots,
            'slots_name': 'Proficiencies',
            'tool_tip': self.get_tool_tip,
            'add': self.add_proficiency,
            'remove': self.remove_proficiency,
        }
        profs = Widget('Proficiencies', 'DualList', data=profs_data)
        self.add_row([profs, ])

        self.proficiency_table = [row for row in DbQuery.getTable('Items') if row['Is_Proficiency'].lower() == "yes"]
        self.slots = '0'
        self.specialised_list = []
        self.double_specialised_list = []
        self.shadow_list = None

    def initialize_page(self, fields, pages, external_data):
        self.slots = '0'
        self.specialised_list = []
        self.double_specialised_list = []
        self.shadow_list = None
        class_id = fields['Classes Current']
        full_class = pages['Choose Class'].get_full_class(class_id)
        if 'classes' in full_class:
            self.slots = str(max([cl['Initial_Weapon_Proficiencies'] for cl in full_class['classes']]))
            if 'fighter' in [cl['unique_id'] for cl in full_class['classes']]:
                self.shadow_list = []
        else:
            self.slots = str(full_class['Initial_Weapon_Proficiencies'])
            if full_class['unique_id'] == 'fighter':
                self.shadow_list = []
        return {'Proficiencies': []}

    def is_complete(self, fields, pages, external_data):
        if self.slots == '0':
            return True
        return False

    def fill_proficiencies(self, owned_items, fields, pages, external_data):
        class_id = fields['Classes Current']
        full_class = pages['Choose Class'].get_full_class(class_id)
        race = fields['Races Current']
        if 'classes' in full_class:
            wp_list = [cl['Weapons_Permitted'] for cl in full_class['classes']]
            weapons_permitted = SystemSettings.race_wp(wp_list, race['unique_id'], self.proficiency_table)
        else:
            weapons_permitted = [weapon.strip().lower() for weapon in full_class['Weapons_Permitted'].split(',')]
        item_list = []
        for item_dict in self.proficiency_table:
            item_tuple = (item_dict['Name'], item_dict)
            damage_type_list = [damage_type.strip().lower() for damage_type in item_dict['Damage_Type'].split(',')]
            if 'any' in weapons_permitted:
                item_list.append(item_tuple)
            elif any(weapon in item_dict['Name'].lower() for weapon in weapons_permitted):
                item_list.append(item_tuple)
            elif [i for i in weapons_permitted if i in damage_type_list]:
                item_list.append(item_tuple)
            elif 'single-handed swords (except bastard swords)' in weapons_permitted:
                if item_dict['unique_id'].startswith('sword') and \
                        'both-hand' not in damage_type_list and 'two-hand' not in damage_type_list:
                    item_list.append(item_tuple)
        return item_list

    def get_slots(self, fields, pages, external_data):
        return self.slots

    def get_tool_tip(self, item, fields, pages, external_data):
        return '{}'.format(item['Notes'])

    def add_proficiency(self, item, fields, pages, external_data):
        if int(self.slots) > 0 and item not in self.double_specialised_list:
            # print(item)
            new_display = item['Name']
            if self.shadow_list is not None:
                self.shadow_list = fields['Proficiencies']
                if item in self.shadow_list:
                    item_index = self.shadow_list.index(item)
                    if item in self.specialised_list:
                        self.double_specialised_list.append(item)
                        new_display = (item_index, '{} - {}'.format(item['Name'], '2X Specialised'))
                    else:
                        self.specialised_list.append(item)
                        new_display = (item_index, '{} - {}'.format(item['Name'], 'Specialised'))
            elif item in fields['Proficiencies']:
                return {}
            self.slots = str(int(self.slots) - 1)
            return {
                'valid': True,
                'slots_new_value': self.slots,
                # 'remove': True,
                # 'new_display': item['Name'],
                'new_display': new_display,
            }
        return {}

    def remove_proficiency(self, item, fields, pages, external_data):
        new_display = item['Name']
        item_index = fields['Proficiencies'].index(item)
        self.slots = str(int(self.slots) + 1)
        if item in self.double_specialised_list:
            self.double_specialised_list.remove(item)
            new_display = (item_index, '{} - {}'.format(item['Name'], 'Specialised'))
        elif item in self.specialised_list:
            self.specialised_list.remove(item)
            new_display = (item_index, item['Name'])
        else:
            pass
        return {
            'valid': True,
            'slots_new_value': self.slots,
            'new_display': new_display,
        }


class EquipmentPage(WizardPage):

    def __init__(self):
        super().__init__(9, 'Buy Equipment')

        self.set_subtitle('Buy equipment you need.')

        eq_data = {
            'fill_avail': self.fill_equipment,
            'slots': self.get_money,
            'slots_name': 'Gold',
            'category_field': 'Category',
            'tool_tip': self.get_tool_tip,
            'add': self.buy_equipment,
            'remove': self.sell_equipment,
        }
        equip = Widget('Equipment', 'DualList', data=eq_data)
        self.add_row([equip, ])

        self.item_table = DbQuery.getTable('Items')
        self.current_money = Decimal(0)

    def initialize_page(self, fields, pages, external_data):
        race = fields['Races Current']
        class_id = fields['Classes Current']
        full_class = pages['Choose Class'].get_full_class(class_id)
        if 'classes' in full_class:
            classes = full_class['classes']
        else:
            classes = [full_class]
        item_ids = []
        if race['unique_id'] == 'elf' and 'fighter' in full_class['unique_id']:
            percent = Dice.randomInt(1, 100)
            if percent <= 5:
                item_ids.append('armour_elfin_chain')
        if 'wizard' in [cl['Category'] for cl in classes]:
            item_ids.append('spellbook')
        if 'cleric' in full_class['unique_id']:
            item_ids.append('holy_symbol_pewter')
        if 'druid' in full_class['unique_id']:
            item_ids.append('holy_symbol_wooden')
        if 'rogue' in [cl['Category'] for cl in classes]:
            item_ids.append('thieves_tools')
        items = []
        for item in self.item_table:
            if item['unique_id'] in item_ids:
                # items.append((item['Name'] + ' - ' + item['Cost'], item))
                items.append(item)

        if 'classes' in full_class:
            dice_strings = [cl['Initial_Wealth_GP'] for cl in full_class['classes']]
            best_dice = Dice.get_best_dice(dice_strings)
            initial_wealth_gp = Dice.rollString(best_dice)
        else:
            dice_string = full_class['Initial_Wealth_GP']
            initial_wealth_gp = Dice.rollString(dice_string)
        self.current_money = Decimal(initial_wealth_gp)

        return {'Equipment': items}

    def fill_equipment(self, owned_items, fields, pages, external_data):
        items = [('{} - {}'.format(item['Name'], item['Cost']), item) for item in self.item_table
                 if item['Cost'].lower() != 'not sold' and not item['Cost'].lower().startswith('proficiency')]
        # These two lines sort the list to guarantee the tab order
        category_order = {'General': 0, 'Weapon': 1, 'Armour': 2, 'Clothing': 3}
        items.sort(key=lambda x: category_order.get(x[1].get('Category', 'General'), 4))
        return items

    def get_money(self, fields, pages, external_data):
        # return '{0:.2f}'.format(Decimal(self.current_money))
        return '{0:.2f}'.format(self.current_money)

    def get_tool_tip(self, item, fields, pages, external_data):
        return '{}<br /><b>{}</b>'.format(item['Name'], item['Cost'])

    def buy_equipment(self, item, fields, pages, external_data):
        cost = SystemSettings.convert_cost_string(item['Cost'])
        if cost < self.current_money:
            self.current_money -= cost
            return {
                'valid': True,
                'slots_new_value': '{0:.2f}'.format(self.current_money),
                'new_display': item['Name'],
             }
        else:
            return {}

    def sell_equipment(self, item, fields, pages, external_data):
        cost_string = item['Cost']
        if cost_string.lower() == 'not sold':
            return {}
        else:
            cost = SystemSettings.convert_cost_string(cost_string)
            self.current_money += cost
            return {
                'valid': True,
                'slots_new_value': '{0:.2f}'.format(self.current_money),
                'new_display': item['Name'],
            }


class InfoPage(WizardPage):

    def __init__(self):
        super().__init__(10, 'Personal Information')

        self.set_subtitle('Enter personal informaiton for your character.')

        empty = Widget('Empty', 'Empty')
        self.add_row([empty, ])

        name = Widget('Name', 'LineEdit')
        self.add_row([name, ])
        alignment = Widget('Alignment', 'ComboBox')
        self.add_row([alignment, ])
        gender = Widget('Gender', 'ComboBox', data=self.get_gender())
        self.add_row([gender, ])

    def initialize_page(self, fields, pages, external_data):
        available_alignments = self.get_available_alignments(fields, pages)
        return {'Alignment': available_alignments}

    def is_complete(self, fields, pages, external_data):
        if len(fields['Name']) == 0 or fields['Name'].isspace():
            return False
        return True

    def get_available_alignments(self, fields, pages):
        class_id = fields['Classes Current']
        full_class = pages['Choose Class'].get_full_class(class_id)
        alignment_options = []
        if 'classes' in full_class:
            for full_class in full_class['classes']:
                alignment_options.append(full_class['Alignment'])
        else:
            alignment_options.append(full_class['Alignment'])

        alignment_list = list(SystemSettings.alignment)
        for align_option in alignment_options:
            if align_option == 'Any Good':
                for align in SystemSettings.alignment:
                    if align.endswith('Neutral') or align.endswith('Evil'):
                        alignment_list.remove(align)

            elif align_option == 'Any Evil':
                for align in SystemSettings.alignment:
                    if align.endswith('Neutral') or align.endswith('Good'):
                        alignment_list.remove(align)

            elif align_option == 'Any Neutral or Evil':
                for align in SystemSettings.alignment:
                    if align.endswith('Good'):
                        alignment_list.remove(align)

            elif align_option == 'Neutral only':
                alignment_list = ['True Neutral', ]

            elif align_option.lower().endswith('only'):
                alignment_list = [align_option[:-5], ]

        return alignment_list

    def get_gender(self):
        return [gender for gender in SystemSettings.gender if gender.lower() != 'na']


class ChoosePortraitPage(WizardPage):

    def __init__(self):
        super().__init__(11, 'Choose Portrait')

        self.set_subtitle('Choose a portrait or click <b>Browse</b> to upload your own.')

        portrait = Widget('Portrait', 'Image', row_span=2, data=resources.noImage_jpg)
        self.add_row([portrait, ])
        empty = Widget('Empty', 'Empty')
        image_list = Widget('Images_', 'ListBox')
        self.add_action(Action('FillFields', image_list, callback=self.select_image))
        self.add_row([empty, image_list, ])
        browse_button = Widget('Browse', 'PushButton', align='Center')
        self.add_row([empty, browse_button, ])
        self.add_action(Action('FileDialog', browse_button, callback=self.browse))

    def initialize_page(self, fields, pages, external_data):
        # extensions = ['jpg', 'jpeg', 'gif', 'png', ]
        image_match = re.compile('([-\w]+\.(?:jpg|jpeg|gif|png)$)')
        system_path = SystemSettings.SYSTEM_PATH
        portraits_path = os.path.join(system_path, 'portraits')
        images = []
        for base_path, _, files in os.walk(portraits_path):
            for file in files:
                if image_match.match(file):
                    full_path = os.path.join(base_path, file)
                    images.append((file, full_path))

        return {'Images': images}

    def select_image(self, fields, pages, external_data):
        filename = fields['Images Current']
        if filename is None:
            return {}
        with open(filename, 'rb') as image_file:
            data = base64.b64encode(image_file.read())
        return {'Portrait': data.decode()}

    def browse(self, filename, fields, pages, external_data):
        with open(filename, 'rb') as image_file:
            data = base64.b64encode(image_file.read())
        return {'Portrait': data.decode()}


class ReviewPage(WizardPage):

    def __init__(self):
        super().__init__(12, 'Review')

        self.set_subtitle('If you like what you see click <b>Finish</b>.')

        portrait = Widget('ReviewPortrait', 'Image', row_span=4)
        info = Widget('ReviewInfo', 'TextLabel', col_span=2)
        self.add_row([portrait, info, ])
        empty = Widget('Empty', 'Empty')
        attrs = Widget('ReviewAttrs', 'TextLabel', col_span=2)
        self.add_row([empty, attrs, ])
        proficiencies = Widget('ReviewProficiencies', 'TextLabel', align='Top')
        equipment = Widget('ReviewEquipment', 'TextLabel', align='Top')
        self.add_row([empty, proficiencies, equipment, ])

        self.attr_dict = None
        self.hp = 0
        self.age = None
        self.height = None
        self.weight = None

    def initialize_page(self, fields, pages, external_data):
        full_class = pages['Choose Class'].get_full_class(fields['Classes Current'])
        class_name = full_class['Name']
        pre_attr_dict = pages['Roll Attributes'].attr_dict or pages['Daily Spells'].attr_dict
        if pre_attr_dict:
            pre_attr_dict = dict(pre_attr_dict)
        self.attr_dict = attr_dict = pages['Daily Spells'].roll_attributes(pre_attr_dict, fields['Races Current'], full_class)
        self.hp = self.roll_hp(1, full_class)
        self.age = self.roll_age(fields, pages)
        self.height, self.weight = self.roll_height_weight(fields)
        prof_names = []
        for prof in fields['Proficiencies']:
            if prof in pages['Proficiencies'].double_specialised_list:
                prof_names.append('{} (2X)'.format(prof['Name']))
            elif prof in pages['Proficiencies'].specialised_list:
                prof_names.append('{} (S)'.format(prof['Name']))
            else:
                prof_names.append(prof['Name'])
        prof_label = '<b>Proficiencies</b><br />'
        prof_label += '<br />'.join(prof_names)
        equip_label = '<b>Equipment</b><br />'
        equip_label += '<br />'.join([equip['Name'] for equip in fields['Equipment']])
        return {
            'ReviewPortrait': fields['Portrait'],
            'ReviewInfo': '<b>{}</b><br />{} {} {} {}<br />{}hp {}ft {}in {}lbs'
            .format(fields['Name'],
                    fields['Alignment'],
                    fields['Races Current']['Name'],
                    fields['Gender'],
                    class_name,
                    self.hp,
                    self.height[0],
                    self.height[1],
                    self.weight),
            'ReviewAttrs': '<b>STR:</b> {}<br /><b>INT</b>: {}<br /><b>WIS</b>: {}<br /><b>DEX</b>: {}<br />'
                           '<b>CON</b>: {}<br /><b>CHA</b>: {}'
            .format(attr_dict['STR'], attr_dict['INT'], attr_dict['WIS'],
                    attr_dict['DEX'], attr_dict['CON'], attr_dict['CHA']),
            'ReviewProficiencies': prof_label,
            'ReviewEquipment': equip_label,
        }

    def roll_hp(self, level, full_class):
        hp = 0
        con_score = self.attr_dict['CON']
        con_bonus = SystemSettings.get_attribute_bonuses('CON', con_score)[0]
        con_bonus_list = con_bonus.replace(' for Warriors)', '').split(' (')
        if len(con_bonus_list) == 1:
            con_bonus_list.append(con_bonus_list[0])
        if 'classes' in full_class:
            for cl in full_class['classes']:
                hp_temp = 0
                if cl['Category'].lower() == 'warrior':
                    con_bonus = con_bonus_list[1]
                else:
                    con_bonus = con_bonus_list[0]
                hit_dice_string = 'd{}'.format(cl['Hit_Die_Type'])
                for i in range(0, int(level)):
                    hp_temp += Dice.rollString(hit_dice_string)
                    hp_temp += int(con_bonus)
                hp += hp_temp // len(full_class['classes']) or 1  # No HP roll should ever be lower than one
        else:
            if full_class['Category'].lower() == 'warrior':
                con_bonus = con_bonus_list[1]
            else:
                con_bonus = con_bonus_list[0]
            hd_number = [row['Hit_Dice'] for row in full_class['Classes_meta']
                         if row['Type'] == 'xp table' and row['Level'] == '1'][0]
            hit_dice_string = '{}d{}'.format(hd_number, full_class['Hit_Die_Type'])
            for i in range(0, int(level)):
                hp += Dice.rollString(hit_dice_string)
                hp += int(con_bonus)

        return hp

    def roll_age(self, fields, pages):
        race_dict = fields['Races Current']
        full_class = pages['Choose Class'].get_full_class(fields['Classes Current'])

        starting_ages = [row for row in race_dict['Races_meta'] if row['Type'] == 'class' and row['Subtype'] == 'starting age']

        class_groups = {'Cleric': ['cleric', 'druid'],
                        'Fighter': ['fighter', 'ranger', 'paladin'],
                        'Magic User': ['magic_user', 'illusionist'],
                        'Thief': ['thief', 'assassin'],
                        'Druid': ['druid'],
                        }

        dice_string = ''
        if 'classes' in full_class:
            bucket = []
            for cl in full_class['classes']:
                for row in starting_ages:
                    if cl['unique_id'] in class_groups[row['Modified']]:
                        bucket.append( row )
            rating = 0
            best_dice = ''
            for row in bucket:
                new_rating = eval(row['Modifier'].replace('d', '*'))
                if new_rating > rating:
                    rating = new_rating
                    best_dice = row['Modifier']
            dice_string = best_dice
        else:
            for row in starting_ages:
                if full_class['unique_id'] in class_groups[row['Modified']]:
                    dice_string = row['Modifier']

        dice_string_list = dice_string.split('+')
        dice_string = dice_string_list[1].strip() + '+' + dice_string_list[0].strip()
        return Dice.rollString(dice_string)

    def roll_height_weight(self, fields):
        race_dict = fields['Races Current']
        gender = fields['Gender']

        height_table = [row for row in race_dict['Races_meta'] if row['Type'] == 'height table' and row['Subtype'].lower() == gender.lower()]
        weight_table = [row for row in race_dict['Races_meta'] if row['Type'] == 'weight table' and row['Subtype'].lower() == gender.lower()]

        height_roll = Dice.randomInt(1, 100)
        weight_roll = Dice.randomInt(1, 100)

        def lookup(roll, table):
            for row in table:
                d = row['Modifier']
                result = row['Modified']
                bounds = [int(b) for b in d.split('-')]
                if roll >= bounds[0] and roll <= bounds[1]:
                    return result

        height_result = lookup(height_roll, height_table)
        weight_result = lookup(weight_roll, weight_table)

        height_result_list = height_result.split('+')
        weight_result_list = weight_result.split('+')

        height_base = height_result_list[0].split()
        height_base_in = int( height_base[0] ) * 12 + int(height_base[2])
        height_mod = height_result_list[1].replace(' in', '')
        weight_base = weight_result_list[0].replace(' lbs', '')
        weight_mod = weight_result_list[1].replace(' lbs', '')

        height = height_base_in + Dice.rollString(height_mod)
        weight = int(weight_base) + Dice.rollString(weight_mod)

        last_height_roll = Dice.rollString('d6')
        last_weight_roll = Dice.rollString('d6')

        while last_height_roll == 1 or last_height_roll == 6:
            height_sign = 1
            if last_height_roll == 1:
                height_sign = -1
            height = height + height_sign * Dice.rollString('1d4')
            last_height_roll = Dice.rollString('d6')

        while last_weight_roll == 1 or last_weight_roll == 6:
            weight_sign = 1
            if last_weight_roll == 1:
                weight_sign = -1
            weight = weight + weight_sign * Dice.rollString('1d20')
            last_weight_roll = Dice.rollString('d6')

        height_tuple = (height // 12, height % 12)

        return height_tuple, weight
