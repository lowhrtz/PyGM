# -*- coding: utf-8 -*-

import DbQuery
import Dice
import SystemSettings
from GuiDefs import *


class LevelUpWizard(Wizard):

    def __init__(self):
        super().__init__('Level Up')

        self.add_wizard_page(IntroPage())
        self.add_wizard_page(SpellbookPage())
        self.add_wizard_page(DailySpellsPage())
        self.add_wizard_page(DailySpellsPage2())
        self.add_wizard_page(ProficiencyPage())
        self.add_wizard_page(ReviewPage())

    def accept(self, fields, pages, external_data):
        if pages['Review'].new_hp is None:
            return
        pc = external_data['Character List Current']
        classes = pc['Classes'].split('/')
        level = str(pc['Level']).split('/')
        for cl in pages['Level Up'].ready_list:
            level[classes.index(cl)] = str(int(level[classes.index(cl)]) + 1)
        accept_return = {
            'HP': int(pages['Review'].new_hp),
            'Level': '/'.join(level),
        }
        if fields['Proficiencies']:
            specialised_list = pages['Proficiencies'].specialised_list
            double_specialised_list = pages['Proficiencies'].double_specialised_list
            accept_return['Proficiencies'] = []
            for prof in fields['Proficiencies']:
                if prof in double_specialised_list:
                    prof['level'] = '2XS'
                    prof_item = ('{} ({})'.format(prof['Name'], 'Double Specialised'), prof)
                elif prof in specialised_list:
                    prof['level'] = 'S'
                    prof_item = ('{} ({})'.format(prof['Name'], 'Specialised'), prof)
                else:
                    prof['level'] = 'P'
                    prof_item = prof
                accept_return['Proficiencies'].append(prof_item)
        if fields['Spellbook']:
            accept_return['Spellbook'] = fields['Spellbook']
        if fields['Daily Spells']:
            if pages['Daily Spells'].meta_row_type == 'DailySpells':
                fieldname = 'Daily Spells'
            else:
                fieldname = 'Daily Spells 2'
            accept_return[fieldname] = fields['Daily Spells']
        if fields['Daily Spells2']:
            accept_return['Daily Spells 2'] = fields['Daily Spells2']
        return accept_return


class IntroPage(WizardPage):
    def __init__(self):
        super().__init__(0, 'Level Up')
        self.set_subtitle('Level-up Wizard')

        text = Widget('Intro Text', 'TextLabel',
                      align='Center', data='There are one or more classes ready to level up for this character!')
        self.add_row([text])

        text2 = Widget('Intro Text2', 'TextLabel', align='Center', data='Click <b>Next</b> to continue.')
        self.add_row([text2])

        self.ready_list = None
        self.ready_dict_list = None
        self.spell_classes = 0
        self.wizard_category = False
        self.other_spellcaster_category = False
        self.proficiency_slots_available = 0
        self.next_page_id = -1

    def initialize_page(self, fields, pages, external_data):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split('/')
        level = str(pc['Level']).split('/')
        self.ready_list = ready_to_level_up(pc)
        self.ready_dict_list = [cl for cl in DbQuery.getTable('Classes') if cl['unique_id'] in self.ready_list]
        self.wizard_category = False
        self.other_spellcaster_category = False
        self.proficiency_slots_available = 0
        self.spell_classes = 0
        for cl in self.ready_dict_list:
            wpa = cl['Weapon_Proficiency_Advancement'].split('/')
            slots = int(wpa[0])
            per_level = int(wpa[1])
            pc_level = int(level[classes.index(cl['unique_id'])])
            # self.proficiency_slots_available = 2
            if pc_level % per_level == 0:
                self.proficiency_slots_available = slots
            has_spells = SystemSettings.has_spells_at_level(pc_level + 1, cl)
            if cl['Category'] == 'wizard' and has_spells:
                self.wizard_category = cl
                self.spell_classes += 1
            elif cl['Primary_Spell_List'] != 'None' and has_spells:
                self.other_spellcaster_category = cl
                self.spell_classes += 1

        if self.wizard_category:
            self.next_page_id = pages['Spellbook'].get_page_id()

        elif self.other_spellcaster_category:
            self.next_page_id = pages['Daily Spells'].get_page_id()

        elif self.proficiency_slots_available:
            self.next_page_id = pages['Proficiencies'].get_page_id()

        elif self.ready_list:
            self.next_page_id = pages['Review'].get_page_id()

        else:
            self.next_page_id = -1
            return {
                'Intro Text': 'There are no classes ready to level up for this character!',
                'Intro Text2': ''
            }

    def get_next_page_id(self, fields, pages, external_data):
        return self.next_page_id


class SpellbookPage(WizardPage):
    def __init__(self):
        super().__init__(1, 'Spellbook')
        self.set_subtitle('Choose a spell to add to your spellbook')

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
        spells_table = self.spells_table
        spells_table = [spell for spell in spells_table
                        if spell['Type'] == pages['Level Up'].wizard_category['unique_id']]
        pc = external_data['Character List Current']
        classes = pc['Classes'].split('/')
        levels = str(pc['Level']).split('/')
        cl = pages['Level Up'].wizard_category
        level = int(levels[classes.index(cl['unique_id'])])
        meta_row = [row for row in cl['Classes_meta'] if row['Level'].isdigit() and int(row['Level']) == level + 1][0]
        highest_spell_level = 0
        for spell_level in range(1, 10):
            sl_column_name = 'Level_{}_Spells'.format(spell_level)
            if meta_row[sl_column_name] > 0:
                highest_spell_level = spell_level

        return [spell for spell in spells_table if spell['Level'] == highest_spell_level and spell not in owned_items]

    def get_spell_slots(self, fields, pages, external_data):
        return self.spell_slots

    def get_tool_tip(self, item, fields, pages, external_data):
        return '<b>{}</b><br />{}'.format(item['Name'], item['Description'])

    def add_spell(self, spell, fields, pages, external_data):
        if self.spell_slots == '1':
            self.spell_slots = '0'
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

        if self.spell_slots == '0':
            self.spell_slots = '1'
            return {
                'valid': True,
                'slots_new_value': self.spell_slots,
                'replace': True,
                'new_display': spell['Name'],
            }
        return {}

    def initialize_page(self, fields, pages, external_data):
        self.spell_slots = '1'
        spells_table = DbQuery.getTable('Spells')
        pc = external_data['Character List Current']
        spellbook_ids = []
        for meta_row in pc['Characters_meta']:
            if meta_row['Type'] == 'Spellbook':
                spellbook_ids.append(meta_row['Entry_ID'])
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

    def __init__(self, page_id=2, title='Daily Spells'):
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
        if page_id == 2:
            self.field_name = field_name = 'Daily Spells'
        else:
            self.field_name = field_name = 'Daily Spells2'
        ds_list = Widget(field_name, 'DualList', data=ds_data)
        self.add_row([ds_list, ])

        # self.attr_dict = None
        self.spell_slots = None
        self.meta_row_type = None

    def initialize_page(self, fields, pages, external_data):
        spells_table = DbQuery.getTable('Spells')
        pc = external_data['Character List Current']
        wizard_category = pages['Level Up'].wizard_category
        other_spellcaster_category = pages['Level Up'].other_spellcaster_category
        if wizard_category:
            class_name = wizard_category['Name']
            spell_type = wizard_category['Primary_Spell_List'].replace('_', ' ').title()
        else:
            class_name = other_spellcaster_category['Name']
            spell_type = other_spellcaster_category['Primary_Spell_List'].replace('_', ' ').title()
        if spell_type != class_name:
            class_name = spell_type
        self.meta_row_type = 'DailySpells'
        if external_data['Daily Spells 2'] and\
                external_data['Daily Spells 2'][0]['Type'].replace('_', ' ').title() == class_name:
            self.meta_row_type = 'DailySpells2'
        spell_ids = []
        for meta_row in pc['Characters_meta']:
            if meta_row['Type'] == self.meta_row_type:
                spell_ids.append(meta_row['Entry_ID'])
        spells = []
        for spell in spells_table:
            if spell['spell_id'] in spell_ids:
                for _ in range(spell_ids.count(spell['spell_id'])):
                    spells.append(spell)
        self.set_subtitle('Choose Daily {} Spells'.format(class_name))
        return {self.field_name: spells}

    def is_complete(self, fields, pages, external_data):
        if self.spell_slots is None:
            return False
        spell_slots_split = self.spell_slots.split('/')
        for slots in spell_slots_split:
            if slots != '0':
                return False
        return True

    def get_next_page_id(self, fields, pages, external_data):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split('/')
        level = [int(l) for l in str(pc['Level']).split('/')]
        wizard_category = pages['Level Up'].wizard_category
        other_spellcaster_category = pages['Level Up'].other_spellcaster_category
        if pages['Level Up'].spell_classes > 1:
            return pages['More Daily Spells'].get_page_id()
        elif wizard_category and wizard_category['Secondary_Spell_List'] != 'None'\
                and SystemSettings.has_secondary_spells_at_level(
                level[classes.classes.index(wizard_category['unique_id'])] + 1, wizard_category):
            return pages['More Daily Spells'].get_page_id()
        elif other_spellcaster_category and other_spellcaster_category['Secondary_Spell_List'] != 'None'\
                and SystemSettings.has_secondary_spells_at_level(
                level[classes.index(other_spellcaster_category['unique_id'])] + 1, other_spellcaster_category):
            return pages['More Daily Spells'].get_page_id()
        elif pages['Level Up'].proficiency_slots_available > 0:
            return pages['Proficiencies'].get_page_id()
        return pages['Review'].get_page_id()

    def fill_spells(self, owned_items, fields, pages, external_data):
        if pages['Level Up'].wizard_category:
            spells_table = [spell for spell in fields['Spellbook']]
        else:
            spells_table = [spell for spell in pages['Spellbook'].spells_table
                            if spell['Type'] == pages['Level Up'].other_spellcaster_category['Primary_Spell_List']
                            and spell['Level'] <= len(self.spell_slots.split('/'))]
        # avail_spells = [spell for spell in spells_table if spell not in owned_items]
        # avail_spells.sort(key=lambda x: x['Level'])
        spells_table.sort(key=lambda x: x['Level'])
        # return avail_spells
        return spells_table

    def get_spell_slots(self, fields, pages, external_data):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split('/')
        levels = str(pc['Level']).split('/')
        cl = pages['Level Up'].wizard_category or pages['Level Up'].other_spellcaster_category
        level = int(levels[classes.index(cl['unique_id'])])
        meta_row = [row for row in cl['Classes_meta'] if row['Level'].isdigit() and int(row['Level']) == level + 1][0]
        slot_list = []
        for spell_level in range(1, 10):
            sl_column_name = 'Level_{}_Spells'.format(spell_level)
            if meta_row[sl_column_name] > 0:
                slot_list.append(meta_row[sl_column_name])
        if cl['unique_id'] == 'cleric':
            _, spell_bonus, _ = SystemSettings.get_attribute_bonuses('WIS', external_data['WIS'])
            spell_bonuses = [int(bonus) for bonus in spell_bonus.split('/')]
            for i in range(min(len(slot_list), len(spell_bonuses))):
                slot_list[i] += spell_bonuses[i]
        if self.meta_row_type == 'DailySpells':
            fieldname = 'Daily Spells'
        else:
            fieldname = 'Daily Spells 2'
        for owned_spell in external_data[fieldname]:
            spell_level = owned_spell['Level']
            slot_list[spell_level - 1] -= 1
        slot_list = [str(slot) for slot in slot_list]
        self.spell_slots = '/'.join(slot_list)
        return self.spell_slots

    def get_tool_tip(self, item, fields, pages, external_data):
        return pages['Spellbook'].get_tool_tip(item, fields, pages, external_data)

    def add_spell(self, spell, fields, pages, external_data):
        spell_level = spell['Level']
        slots_split = self.spell_slots.split('/')
        slots = int(slots_split[spell_level - 1])
        if slots > 0:
            slots -= 1
            slots_split[spell_level - 1] = str(slots)
            self.spell_slots = '/'.join(slots_split)
            return {
                'valid': True,
                'slots_new_value': self.spell_slots,
                # 'remove': True,
                'new_display': spell['Name'],
            }
        return {}

    def remove_spell(self, spell, fields, pages, external_data):
        spell_level = spell['Level']
        slots_split = self.spell_slots.split('/')
        slots = int(slots_split[spell_level - 1])
        slots += 1
        slots_split[spell_level - 1] = str(slots)
        self.spell_slots = '/'.join(slots_split)
        return {
            'valid': True,
            'slots_new_value': self.spell_slots,
            # 'replace': True,
            'new_display': spell['Name'],
        }


class DailySpellsPage2(DailySpellsPage):

    def __init__(self):
        super().__init__(3, 'More Daily Spells')

    def initialize_page(self, fields, pages, external_data):
        wizard_category = pages['Level Up'].wizard_category
        other_spellcaster_category = pages['Level Up'].other_spellcaster_category
        if pages['Level Up'].spell_classes == 1:
            if wizard_category and wizard_category['Secondary_Spell_List'] != 'None':
                class_name = wizard_category['Secondary_Spell_List'].replace('_', ' ').title()
            else:
                class_name = other_spellcaster_category['Secondary_Spell_List'].replace('_', ' ').title()
        else:
            class_name = other_spellcaster_category['Name']
        self.set_subtitle('Choose Daily {} Spells'.format(class_name))
        return {self.field_name: external_data['Daily Spells 2']}

    def get_next_page_id(self, fields, pages, external_data):
        if pages['Level Up'].proficiency_slots_available > 0:
            return pages['Proficiencies'].get_page_id()
        else:
            return pages['Review'].get_page_id()

    def fill_spells(self, owned_items, fields, pages, external_data):
        wizard_category = pages['Level Up'].wizard_category
        other_spellcaster_category = pages['Level Up'].other_spellcaster_category
        if pages['Level Up'].spell_classes == 1:
            if wizard_category and wizard_category['Secondary_Spell_List'] != 'None':
                spells_table = [spell for spell in pages['Spellbook'].spells_table
                                if spell['Type'] == wizard_category['Secondary_Spell_List'] and
                                spell['Level'] <= len(self.spell_slots)]
            else:
                spells_table = [spell for spell in pages['Spellbook'].spells_table
                                if spell['Type'] == other_spellcaster_category['Secondary_Spell_List'] and
                                spell['Level'] <= len(self.spell_slots)]
        else:
            spells_table = [spell for spell in pages['Spellbook'].spells_table
                            if spell['Type'] == pages['Level Up'].other_spellcaster_category['Primary_Spell_List']
                            and spell['Level'] <= len(self.spell_slots)]
        # avail_spells = [spell for spell in spells_table if spell not in owned_items]
        # avail_spells.sort(key=lambda x: x['Level'])
        # return avail_spells
        spells_table.sort(key=lambda x: x['Level'])
        return spells_table


class ProficiencyPage(WizardPage):
    def __init__(self):
        super().__init__(4, 'Proficiencies')
        self.set_subtitle('Choose available proficiencies')

        self.proficiency_table = [row for row in DbQuery.getTable('Items') if row['Is_Proficiency'].lower() == "yes"]
        self.class_table = DbQuery.getTable('Classes')
        self.race_table = DbQuery.getTable('Races')
        self.slots_remaining = 0
        self.orig_proficiencies = []
        self.specialised_list = []
        self.double_specialised_list = []
        self.shadow_list = None

        prof_data = {
            'fill_avail': self.fill_proficiencies,
            'slots': self.get_proficiency_slots,
            'slots_name': 'Proficiency',
            # 'category_field': 'Damage_Type',
            # 'category_callback': self.get_category_tab_name,
            'tool_tip': self.get_tool_tip,
            'add': self.add_proficiency,
            'remove': self.remove_proficiency,
        }
        proficiencies = Widget('Proficiencies', 'DualList', data=prof_data)

        self.add_row([proficiencies, ])

    def fill_proficiencies(self, owned_items, fields, pages, external_data):
        pc = external_data['Character List Current']

        class_id_list = [cl.strip() for cl in pc['Classes'].split('/')]
        class_list = [row for row in self.class_table if row['unique_id'] in class_id_list]
        if len(class_list) == 1:
            class_dict = class_list[0]
        else:
            class_dict = {'classes': class_list}
        race_dict = [row for row in self.race_table if row['unique_id'] == pc['Race']][0]
        if 'classes' in class_dict:
            wp_list = [cl['Weapons_Permitted'] for cl in class_dict['classes']]
            weapons_permitted = SystemSettings.race_wp(wp_list, race_dict['unique_id'], self.proficiency_table)
        else:
            weapons_permitted = [weapon.strip().lower() for weapon in class_dict['Weapons_Permitted'].split(',')]
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

    def get_proficiency_slots(self, fields, pages, external_data):
        self.slots_remaining = pages['Level Up'].proficiency_slots_available
        return self.slots_remaining

    def get_category_tab_name(self, category, fields, pages, external_data):
        return category.title()

    def get_tool_tip(self, item, fields, pages, external_data):
        return '{}'.format(item['Notes'])

    def add_proficiency(self, item, fields, pages, external_data):
        if self.slots_remaining > 0 and item not in self.double_specialised_list:
            # print(item)
            new_display = item['Name']
            if self.shadow_list:
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
            self.slots_remaining -= 1
            return {
                'valid': True,
                'slots_new_value': self.slots_remaining,
                # 'remove': True,
                # 'new_display': item['Name'],
                'new_display': new_display,
            }
        return {}

    def remove_proficiency(self, item, fields, pages, external_data):
        orig_state = None
        for orig_prof in self.orig_proficiencies:
            if type(orig_prof).__name__ == 'dict':
                if item == orig_prof:
                    orig_state = 'P'
                    break
            elif type(orig_prof).__name__ == 'tuple':
                if item == orig_prof[1]:
                    specialised_text = orig_prof[0].split('-')[1].strip()
                    if specialised_text == 'Specialised':
                        orig_state = 'S'
                        break
                    elif specialised_text == '2X Specialised':
                        orig_state = '2X'
                        break
        new_display = item['Name']
        item_index = fields['Proficiencies'].index(item)
        # print(orig_state)
        if orig_state == 'P':
            if item in self.double_specialised_list:
                self.double_specialised_list.remove(item)
                new_display = (item_index, '{} - {}'.format(item['Name'], 'Specialised'))
            elif item in self.specialised_list:
                self.specialised_list.remove(item)
                new_display = (item_index, item['Name'])
            else:
                return {}
        elif orig_state == 'S':
            if item in self.double_specialised_list:
                self.double_specialised_list.remove(item)
                new_display = (item_index, '{} - {}'.format(item['Name'], 'Specialised'))
            else:
                return {}
        elif orig_state == '2X':
            return {}
        else:
            if item in self.double_specialised_list:
                self.double_specialised_list.remove(item)
                new_display = (item_index, '{} - {}'.format(item['Name'], 'Specialised'))
            elif item in self.specialised_list:
                self.specialised_list.remove(item)
                new_display = (item_index, item['Name'])
            else:
                pass
        self.slots_remaining += 1
        return {
            'valid': True,
            'slots_new_value': self.slots_remaining,
            'new_display': new_display,
        }

    def initialize_page(self, fields, pages, external_data):
        pc = external_data['Character List Current']

        # pc_proficiency_list = [row['Entry_ID'] for row in pc['Characters_meta'] if row['Type'] == 'Proficiency']
        pc_proficiency_list = [row for row in pc['Characters_meta'] if row['Type'] == 'Proficiency']
        pc_proficiency_ids = []
        specialised_ids = []
        double_specialised_ids = []
        for row in pc_proficiency_list:
            # print(row)
            specialisation_level = row['Data']
            if specialisation_level == 'S':
                specialised_ids.append(row['Entry_ID'])
            elif specialisation_level == '2XS':
                double_specialised_ids.append(row['Entry_ID'])
            pc_proficiency_ids.append(row['Entry_ID'])
        self.specialised_list = [row for row in self.proficiency_table if row['unique_id'] in specialised_ids]
        self.double_specialised_list = [row for row in self.proficiency_table
                                        if row['unique_id'] in double_specialised_ids]
        # pc_proficiencies = [row for row in self.proficiency_table if row['unique_id'] in pc_proficiency_ids]
        self.orig_proficiencies = pc_proficiencies = []
        for row in self.proficiency_table:
            if row['unique_id'] in pc_proficiency_ids:
                prof = row
                if row['unique_id'] in double_specialised_ids:
                    prof = ('{} - {}'.format(row['Name'], 'Double Specialised'), row)
                elif row['unique_id'] in specialised_ids:
                    prof = ('{} - {}'.format(row['Name'], 'Specialised'), row)
                pc_proficiencies.append(prof)
        pc_classes = pc['Classes'].split('/')
        if 'fighter' in pc_classes:
            self.shadow_list = pc_proficiencies
        return {'Proficiencies': pc_proficiencies}

    def is_complete(self, fields, pages, external_data):
        if self.slots_remaining > 0:
            return False
        return True


class ReviewPage(WizardPage):
    def __init__(self):
        super().__init__(5, 'Review')
        self.set_subtitle('Make sure you like what you see')

        hp_review = Widget('HP Review', 'TextLabel', align='Center')

        self.add_row([hp_review, ])

        proficiency_review = Widget('Proficiency Review', 'TextLabel', align='Center')

        self.add_row([proficiency_review, ])

        daily_spells_review = Widget('Daily Spells Review', 'TextLabel', align='Center')
        # daily_spells2_review = Widget('Daily Spells2 Review', 'TextLabel', align='Center')

        self.add_row([daily_spells_review, ])

        self.new_hp = None

    def initialize_page(self, fields, pages, external_data):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split('/')
        level = str(pc['Level']).split('/')

        ready_dict_list = pages['Level Up'].ready_dict_list
        warrior_level_up = False
        hp_add = 0
        for cl in ready_dict_list:
            if cl['Category'].lower() == 'warrior':
                warrior_level_up = True
            pc_level = int(level[classes.index(cl['unique_id'])])
            if pc_level < cl['Hit_Die_Max']:
                hp_roll = Dice.rollString('d{}'.format(cl['Hit_Die_Type']))
            else:
                hp_roll = [row for row in cl['Classes_meta'] if row['Level'] == 'each'][0]['Hit_Dice']
#            print hp_roll
            hp_add += hp_roll // len(classes) or 1

        con_score = external_data['CON']
        con_bonus = SystemSettings.get_attribute_bonuses('CON', con_score)[0]
        con_bonus_list = con_bonus.replace(' for Warriors)', '').split(' (')
        if len(con_bonus_list) == 1:
            con_bonus_list.append(con_bonus_list[0])
        if warrior_level_up:
            con_bonus = con_bonus_list[1]
        else:
            con_bonus = con_bonus_list[0]
        hp_add += int(con_bonus)
        self.new_hp = str(hp_add + external_data['HP'])

        fill = {}
        hp_review = '<b>Hit Points to be added:</b> {}<br />' \
                    '<b>For a total of:</b> {}'.format(str(hp_add), self.new_hp)
        fill['HP Review'] = hp_review

        if pages['Level Up'].proficiency_slots_available > 0:
            proficiency_review = '<b>Proficiencies</b><br />'
            for prof in fields['Proficiencies']:
                if prof in pages['Proficiencies'].double_specialised_list:
                    proficiency_review += '{} (2X)<br />'.format(prof['Name'])
                elif prof in pages['Proficiencies'].specialised_list:
                    proficiency_review += '{} (S)<br />'.format(prof['Name'])
                else:
                    proficiency_review += '{}<br />'.format(prof['Name'])
            fill['Proficiency Review'] = proficiency_review
        if fields['Daily Spells']:
            spell_type = fields['Daily Spells'][0]['Type'].replace('_', ' ').title()
            daily_spells_review = '<table cellspacing=20><tr><td><b>Daily {} Spells</b><br />'.format(spell_type)
            for ds in fields['Daily Spells']:
                daily_spells_review += '{}<br />'.format(ds['Name'])
            daily_spells_review += '</td>'
            if fields['Daily Spells2']:
                spell_type = fields['Daily Spells2'][0]['Type'].replace('_', ' ').title()
                daily_spells_review += '<td><b>Daily {} Spells</b><br />'.format(spell_type)
                for ds2 in fields['Daily Spells2']:
                    daily_spells_review += '{}<br />'.format(ds2['Name'])
                daily_spells_review += '</td>'
            daily_spells_review += '</tr></table>'
            fill['Daily Spells Review'] = daily_spells_review

        return fill


def ready_to_level_up(pc):
    classes_meta = DbQuery.getTable('Classes_meta')
    classes = pc['Classes'].split('/')
    xp = str(pc['XP']).split('/')
    level = str(pc['Level']).split('/')
    level_up_classes = []
    for i, cl in enumerate(classes):
        cl_xp = int(xp[i])
        cl_level = int(level[i])
        xp_table = [row for row in classes_meta if row['class_id'] == cl and row['Type'] == 'xp table']
        each = None
        for j, row in enumerate(xp_table):
            if row['Level'].lower() == 'each':
                each = j
        if each is not None:
            each = xp_table.pop(each)

        xp_table.sort(key=lambda x: int(x['Level']))
        top_row = xp_table[len(xp_table) - 1]
        top_row_level = int(top_row['Level'])
        if cl_level > top_row_level:
            levels_past_top_row = (cl_xp - top_row['XP']) // each['XP']
            if top_row_level + levels_past_top_row > cl_level:
                level_up_classes.append(cl)
        else:
            for j, row in enumerate(xp_table):
                if int(row['Level']) == cl_level + 1:
                    if cl_xp >= row['XP']:
                        level_up_classes.append(cl)
                    break

    return level_up_classes
