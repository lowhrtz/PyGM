# -*- coding: utf-8 -*-

import DbQuery
import Dice
import SystemSettings
from GuiDefs import *


class LevelUpWizard( Wizard ):
    def __init__( self ):
        #super( LevelUpWizard, self ).__init__( 'Level Up' )
        super().__init__( 'Level Up' )

        self.add_wizard_page( IntroPage() )
        self.add_wizard_page( SpellbookPage() )
        self.add_wizard_page( SpellsPage() )
        self.add_wizard_page( ProficiencyPage() )
        self.add_wizard_page( ReviewPage() )

    def accept( self, fields, pages, external_data ):
#        print fields['Name']
        return

class IntroPage( WizardPage ):
    def __init__( self ):
        #super( IntroPage, self ).__init__( 0, 'Level Up' )
        super().__init__( 0, 'Level Up' )
        self.set_subtitle( 'Level-up Wizard' )

        text = Widget( 'Intro Text', 'TextLabel',
                        align='Center' , data='There are one or more classes ready to level up for this character!' )
        self.add_row( [ text ] )

        text2 = Widget( 'Intro Text2', 'TextLabel', align='Center', data='Click <b>Next</b> to continue.' )
        self.add_row( [ text2 ] )

        self.ready_list = None
        self.ready_dict_list = None
        self.wizard_category = False
        self.priest_category = False

    def initialize_page( self, fields, pages, external_data ):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        level = str( pc['Level'] ).split( '/' )
        self.ready_list = ready_to_level_up( pc )
        self.ready_dict_list = [ cl for cl in DbQuery.getTable( 'Classes' ) if cl['unique_id'] in self.ready_list ]
        self.wizard_category = False
        self.priest_category = False
        self.proficiency_slots_available = 0
        for cl in self.ready_dict_list:
            if cl['Category'] == 'wizard':
                self.wizard_category = cl
            if cl['Category'] == 'priest':
                self.priest_category == cl
            wpa = cl['Weapon_Proficiency_Advancement'].split('/')
            slots = int( wpa[0] )
            per_level = int( wpa[1] )
            pc_level = int( level[ classes.index( cl['unique_id'] ) ] )
            if pc_level % per_level == 0:
                self.proficiency_slots_available = slots

        if self.wizard_category:
            self.next_page_id = pages['Spellbook'].get_page_id()

        elif self.proficiency_slots_available:
            self.next_page_id = pages['Proficiencies'].get_page_id()

        elif self.ready_list:
            self.next_page_id = pages['Review'].get_page_id()

        else:
            self.next_page_id = -1
            return { 'Intro Text': 'There are no classes ready to level up for this character!',
                     'Intro Text2': '' }

    def get_next_page_id( self, fields, pages, external_data ):
        return self.next_page_id


class SpellbookPage( WizardPage ):
    def __init__( self ):
        #super( SpellbookPage, self ).__init__( 1, 'Spellbook' )
        super().__init__( 1, 'Spellbook' )
        self.set_subtitle( 'Choose a spell to add to your spellbook' )

        self.orig_spells = []
        self.spell_slots = None
        self.spells_table = DbQuery.getTable( 'Spells' )

        sb_data = {
            'fill_avail': self.fill_spells,
            'slots': self.get_spell_slots,
            'slots_name': 'Spells',
            'category_field': 'Level',
            'tool_tip': self.get_tool_tip,
            'add': self.add_spell,
            'remove': self.remove_spell,
        }
        sb_list = Widget( 'Spellbook', 'DualList', align='Center', data=sb_data )

        self.add_row( [ sb_list, ] )

    def fill_spells( self, owned_items, fields, pages, external_data ):
        self.orig_spells = owned_items
        spells_table = self.spells_table
        spells_table = [ spell for spell in spells_table if spell['Type'] == pages['Level Up'].wizard_category['unique_id'] ]
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        levels = str( pc['Level'] ).split( '/' )
        cl = pages['Level Up'].wizard_category
        level = int( levels[ classes.index( cl['unique_id'] ) ] )
        meta_row = [ row for row in cl['Classes_meta'] if row['Level'].isdigit() and int( row['Level'] ) == level ][0]
        highest_spell_level = 0
        for spell_level in range( 1, 10 ):
            sl_column_name = 'Level_{}_Spells'.format( spell_level )
            if meta_row[sl_column_name] > 0:
                highest_spell_level = spell_level

        return [ spell for spell in spells_table if spell['Level'] == highest_spell_level and spell not in owned_items ]

    def get_spell_slots( self, fields, pages, external_data ):
        return self.spell_slots

    def get_tool_tip( self, item, fields, pages, external_data ):
        return '<b>{}</b><br />{}'.format( item['Name'], item['Description'] )

    def add_spell( self, spell, fields, pages, external_data ):
        if self.spell_slots == '1':
            self.spell_slots = '0'
            return { 'valid': True,
                     'slots_new_value': self.spell_slots,
                     'remove': True,
                     'new_display': spell['Name'],
                     }
        return {}

    def remove_spell( self, spell, fields, pages, external_data ):
        if spell in self.orig_spells:
            return {}

        if self.spell_slots == '0':
            self.spell_slots = '1'
            return { 'valid' : True,
                     'slots_new_value': self.spell_slots,
                     'replace': True,
                     'new_display': spell['Name'],
                  }
        return {}

    def initialize_page( self, fields, pages, external_data ):
        self.spell_slots = '1'
        spells_table = DbQuery.getTable( 'Spells' )
        pc = external_data['Character List Current']
        spellbook_ids = []
        for meta_row in pc['Characters_meta']:
            if meta_row['Type'] == 'Spellbook':
                spellbook_ids.append( meta_row['Entry_ID'] )
        spellbook = []
        for spell in spells_table:
            if spell['spell_id'] in spellbook_ids:
                spellbook.append( spell )
        return { 'Spellbook': spellbook }

    def is_complete( self, fields, pages, external_data ):
        if self.spell_slots == '0':
            return True
        return False

    def get_next_page_id( self, fields, pages, external_data ):
        return pages['Daily Wizard Spells'].get_page_id()


class SpellsPage( WizardPage ):
    def __init__( self ):
        #super( SpellsPage, self ).__init__( 2, 'Daily Wizard Spells' )
        super().__init__( 2, 'Daily Wizard Spells' )
        self.set_subtitle( 'Choose Daily Spells' )

        self.spell_slots = None

        ds_data = {
            'fill_avail': self.fill_spells,
            'slots': self.get_spell_slots,
            'slots_name': 'Spells',
            'category_field': 'Level',
            'tool_tip': self.get_tool_tip,
            'add': self.add_spell,
            'remove': self.remove_spell,
        }
        daily_spells = Widget( 'Daily Spells', 'DualList', data=ds_data )

        self.add_row( [ daily_spells, ] )

    def fill_spells( self, owned_items, fields, pages, external_data ):
        #spells_table = DbQuery.getTable( 'Spells' )
        #spells_table = [ spell for spell in spells_table if spell['Type'] == pages['Level Up'].wizard_category['unique_id'] ]
        spells_table = fields['Spellbook']
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        levels = str( pc['Level'] ).split( '/' )
        cl = pages['Level Up'].wizard_category
        level = int( levels[ classes.index( cl['unique_id'] ) ] )
        meta_row = [ row for row in cl['Classes_meta'] if row['Level'].isdigit() and int( row['Level'] ) == level ][0]
        highest_spell_level = 0
        for spell_level in range( 1, 10 ):
            sl_column_name = 'Level_{}_Spells'.format( spell_level )
            if meta_row[sl_column_name] > 0:
                highest_spell_level = spell_level

        return [ spell for spell in spells_table if spell['Level'] <= highest_spell_level and spell not in owned_items ]

    def get_spell_slots( self, fields, pages, external_data ):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        levels = str( pc['Level'] ).split( '/' )
        cl = pages['Level Up'].wizard_category
        #print( pages['Level Up'].wizard_category )
        level = int( levels[ classes.index( cl['unique_id'] ) ] )
        meta_row = [ row for row in cl['Classes_meta'] if row['Level'].isdigit() and int( row['Level'] ) == level ][0]
        slot_list = []
        for spell_level in range( 1, 10 ):
            sl_column_name = 'Level_{}_Spells'.format( spell_level )
            if meta_row[sl_column_name] > 0:
                slot_list.append( str( meta_row[sl_column_name] ) )
        self.spell_slots = '/'.join( slot_list )
        return self.spell_slots

    def get_tool_tip( self, item, fields, pages, external_data ):
        return '<b>{}</b><br />{}'.format( item['Name'], item['Description'] )

    def add_spell( self, spell, fields, pages, external_data ):
        spell_level = spell['Level']
        slot_list = self.spell_slots.split( '/' )
        level_slots = int( slot_list[ spell_level - 1 ] )

        if level_slots > 0:
            new_level_slots = level_slots - 1
            slot_list[ spell_level - 1 ] = str( new_level_slots )
            self.spell_slots = '/'.join( slot_list )
            return { 'valid': True,
                     'slots_new_value': self.spell_slots,
                     'remove': True,
                     'new_display': spell['Name'],
                     }
        return { 'valid': False }

    def remove_spell( self, spell, fields, pages, external_data ):
        spell_level = spell['Level']
        slot_list = self.spell_slots.split( '/' )
        level_slots = int( slot_list[ spell_level - 1 ] )
        new_level_slots = level_slots + 1
        slot_list[ spell_level - 1 ] = str( new_level_slots )
        self.spell_slots = '/'.join( slot_list )
        return { 'valid' : True,
                 'slots_new_value': self.spell_slots,
                 'replace': True,
                 'new_display': spell['Name'],
                 }

    def initialize_page( self, fields, pages, external_data ):
        spells_table = DbQuery.getTable( 'Spells' )
        #spells_table = pages['Spellbook'].spells_table
        pc = external_data['Character List Current']
        spell_ids = []
        for meta_row in pc['Characters_meta']:
            if meta_row['Type'] == 'DailySpells':
                spell_ids.append( meta_row['Entry_ID'] )
        spells = []
        for spell in spells_table:
            if spell['spell_id'] in spell_ids:
                spells.append( spell )
        return { 'Daily Spells': spells }

    def is_complete( self, fields, pages, external_data ):
        if self.spell_slots == None:
            return False

        slot_list = self.spell_slots.split( '/' )
        for slot in slot_list:
            if slot != '0':
                return False

        return True

    def get_next_page_id( self, fields, pages, external_data ):
        if pages['Level Up'].priest_category:
            return pages['Daily Priest Spells'].get_page_id()
        elif pages['Level Up'].proficiency_slots_available:
            return pages['Proficiencies'].get_page_id()
        else:
            return pages['Review'].get_page_id()


class SpellsPage2( WizardPage ):
    def __init__( self ):
        #super( SpellsPage, self ).__init__( 2, 'Daily Priest Spells' )
        super().__init__( 2, 'Daily Priest Spells' )
        self.set_subtitle( 'Choose Daily Spells' )

        self.spell_slots = None

        ds_data = {
            'fill_avail': self.fill_spells,
            'slots': self.get_spell_slots,
            'slots_name': 'Spells',
            'category_field': 'Level',
            'tool_tip': self.get_tool_tip,
            'add': self.add_spell,
            'remove': self.remove_spell,
        }
        daily_spells = Widget( 'Daily Spells2', 'DualList', data=ds_data )

        self.add_row( [ daily_spells, ] )

    def fill_spells( self, owned_items, fields, pages, external_data ):
#        spells_table = DbQuery.getTable( 'Spells' )
        spells_table = pages['Spellbook'].spells_table
        spells_table = [ spell for spell in spells_table if spell['Type'] == pages['Level Up'].priest_category['unique_id'] ]
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        levels = str( pc['Level'] ).split( '/' )
        cl = pages['Level Up'].wizard_category
        level = int( levels[ classes.index( cl['unique_id'] ) ] )
        meta_row = [ row for row in cl['Classes_meta'] if row['Level'].isdigit() and int( row['Level'] ) == level ][0]
        highest_spell_level = 0
        for spell_level in range( 1, 10 ):
            sl_column_name = 'Level_{}_Spells'.format( spell_level )
            if meta_row[sl_column_name] > 0:
                highest_spell_level = spell_level

        return [ spell for spell in spells_table if spell['Level'] <= highest_spell_level and spell not in owned_items ]

    def get_spell_slots( self, fields, pages, external_data ):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        levels = str( pc['Level'] ).split( '/' )
        cl = pages['Level Up'].wizard_category
        level = int( levels[ classes.index( cl['unique_id'] ) ] )
        meta_row = [ row for row in cl['Classes_meta'] if row['Level'].isdigit() and int( row['Level'] ) == level ][0]
        slot_list = []
        for spell_level in range( 1, 10 ):
            sl_column_name = 'Level_{}_Spells'.format( spell_level )
            if meta_row[sl_column_name] > 0:
                slot_list.append( str( meta_row[sl_column_name] ) )
        self.spell_slots = '/'.join( slot_list )
        return self.spell_slots

    def get_tool_tip( self, item, fields, pages, external_data ):
        return '<b>{}</b><br />{}'.format( item['Name'], item['Description'] )

    def add_spell( self, spell, fields, pages, external_data ):
        spell_level = spell['Level']
        slot_list = self.spell_slots.split( '/' )
        level_slots = int( slot_list[ spell_level - 1 ] )

        if level_slots > 0:
            new_level_slots = level_slots - 1
            slot_list[ spell_level - 1 ] = str( new_level_slots )
            self.spell_slots = '/'.join( slot_list )
            return { 'valid': True,
                     'slots_new_value': self.spell_slots,
                     'remove': True,
                     'new_display': spell['Name'],
                     }
        return { 'valid': False }

    def remove_spell( self, spell, fields, pages, external_data ):
        spell_level = spell['Level']
        slot_list = self.spell_slots.split( '/' )
        level_slots = int( slot_list[ spell_level - 1 ] )
        new_level_slots = level_slots + 1
        slot_list[ spell_level - 1 ] = str( new_level_slots )
        self.spell_slots = '/'.join( slot_list )
        return { 'valid' : True,
                 'slots_new_value': self.spell_slots,
                 'replace': True,
                 'new_display': spell['Name'],
                 }

    def initialize_page( self, fields, pages, external_data ):
#        spells_table = DbQuery.getTable( 'Spells' )
        spells_table = pages['Spellbook'].spells_table
        pc = external_data['Character List Current']
        spell_ids = []
        for meta_row in pc['Characters_meta']:
            if meta_row['Type'] == 'DailySpells':
                spell_ids.append( meta_row['Entry_ID'] )
        spells = []
        for spell in spells_table:
            if spell['spell_id'] in spell_ids:
                spells.append( spell )
        return { 'Daily Spells2': spells }

    def is_complete( self, fields, pages, external_data ):
        if self.spell_slots == None:
            return False

        slot_list = self.spell_slots.split( '/' )
        for slot in slot_list:
            if slot != '0':
                return False

        return True

    def get_next_page_id( self, fields, pages, external_data ):
        if pages['Level Up'].proficiency_slots_available:
            return pages['Proficiencies'].get_page_id()
        else:
            return pages['Review'].get_page_id()


class ProficiencyPage( WizardPage ):
    def __init__( self ):
        #super( ProficiencyPage, self ).__init__( 4, 'Proficiencies' )
        super().__init__( 4, 'Proficiencies' )
        self.set_subtitle( 'Choose available proficiencies' )

        self.proficiency_table = [ row for row in DbQuery.getTable( 'Items' ) if row['Is_Proficiency'].lower() == "yes" ]
        self.class_table = DbQuery.getTable( 'Classes' )
        self.race_table = DbQuery.getTable( 'Races' )
        self.slots_remaining = 0

        prof_data = {
        'fill_avail': self.fill_proficiencies,
        'slots': self.get_proficiency_slots,
        'slots_name': 'Proficiency',
        'category_field': 'Damage_Type',
        'tool_tip': self.get_tool_tip,
        'add': self.add_proficiency,
        'remove': self.remove_proficiency,
        }
        proficiencies = Widget( 'Proficiencies', 'DualList', data=prof_data )

        self.add_row( [ proficiencies, ] )

    def fill_proficiencies( self, owned_items, fields, pages, external_data ):
        pc = external_data['Character List Current']

        self.specialised_list = []
        self.double_specialised_list = []
        class_id_list = [ cl.strip() for cl in pc['Classes'].split( '/' ) ]
        class_list = [ row for row in self.class_table if row['unique_id'] in class_id_list ]
        if len( class_list ) == 1:
            class_dict = class_list[0]
        elif len( class_list ) > 1:
            class_dict = { 'classes': class_list }
        race_dict = [ row for row in self.race_table if row['race_id'] == pc['Race'] ][0]
        if 'classes' in class_dict:
            wp_list = [ cl['Weapons_Permitted' ] for cl in class_dict[ 'classes' ] ]
            weapons_permitted = SystemSettings.race_wp( wp_list, race_dict['unique_id'], self.proficiency_table )
        else:
            weapons_permitted = [ weapon.strip().lower() for weapon in class_dict['Weapons_Permitted'].split( ',' ) ]
        item_list = []
        for item_dict in item_dict_list:
            item_tuple = ( item_dict['Name'], item_dict )
            damage_type_list = [ damage_type.strip().lower() for damage_type in item_dict['Damage_Type'].split( ',' ) ]
            if 'any' in weapons_permitted:
                item_list.append( item_tuple )
            elif any( weapon in item_dict['Name'].lower() for weapon in weapons_permitted ):
                item_list.append( item_tuple )
            elif [ i for i in weapons_permitted if i in damage_type_list ]:
                item_list.append( item_tuple )
            elif 'single-handed swords (except bastard swords)' in weapons_permitted:
                if item_dict['unique_id'].startswith( 'sword' ) and \
                'both-hand' not in damage_type_list and 'two-hand' not in damage_type_list:
                    item_list.append( item_tuple )
        return item_list

    def get_proficiency_slots( self, fields, pages, external_data ):
        self.slots_remaining = pages['Level Up'].proficiency_slots_available
        return self.slots_remaining

    def get_tool_tip( self, item, fields, pages, external_data ):
        return '{}'.format( item['Notes'] )

    def add_proficiency( self, item, fields, pages, external_data ):
        return {}

    def remove_proficiency( self, item, fields, pages, external_data ):
        return {}

    def initialize_page( self, fields, pages, external_data ):
        pc = external_data['Character List Current']

        pc_proficiency_list = [ row['Entry_ID'] for row in pc['Characters_meta'] if row['Type'] == 'Proficiency' ]
        pc_proficiencies = [ row for row in self.proficiency_table if row['unique_id'] in pc_proficiency_list ]

        return { 'Proficiencies', pc_proficiencies }

    def is_complete( self, fields, pages, external_data ):
        return True


class ReviewPage( WizardPage ):
    def __init__( self ):
        #super( ReviewPage, self ).__init__( 5, 'Review' )
        super().__init__( 5, 'Review' )
        self.set_subtitle( 'Make sure you like what you see' )

        review_text = Widget( 'Review Text', 'TextLabel', align='Center' )

        self.add_row( [ review_text, ] )

    def initialize_page( self, fields, pages, external_data ):
        pc = external_data['Character List Current']
        classes = pc['Classes'].split( '/' )
        level = str( pc['Level'] ).split( '/' )

        ready_dict_list = pages['Level Up'].ready_dict_list
        hp_add = 0
        for cl in ready_dict_list:
            pc_level = int( level[ classes.index( cl['unique_id'] ) ] )
            if pc_level < cl['Hit_Die_Max']:
                hp_roll = Dice.rollString( 'd{}'.format( cl['Hit_Die_Type'] ) )
            else:
                hp_roll = [ row for row in cl['Classes_meta'] if row['Level'] == 'each' ][0]['Hit_Dice']
#            print hp_roll
            hp_add += hp_roll // len( classes ) or 1

            return { 'Review Text' : '<b>Hit Points Added: </b>{}'.format( str( hp_add ) ) }

    def is_complete( self, fields, pages, external_data ):
        return True


def ready_to_level_up( pc ):
    classes_meta = DbQuery.getTable( 'Classes_meta' )
    classes = pc['Classes'].split( '/' )
    xp = str( pc['XP'] ).split( '/' )
    level = str( pc['Level'] ).split( '/' )
    level_up_classes = []
    for i, cl in enumerate( classes ):
        cl_xp = int( xp[i] )
        cl_level = int( level[i] )
        xp_table = [ row for row in classes_meta if row['class_id'] == cl and row['Type'] == 'xp table' ]
        each = None
        for j, row in enumerate( xp_table ):
            if row['Level'].lower() == 'each':
                each = j
        if each is not None:
            each = xp_table.pop( each )

        xp_table.sort( key=lambda x: int( x['Level'] ) )
        top_row = xp_table[ len( xp_table ) - 1 ]
        top_row_level = int( top_row['Level'] )
        if cl_level > top_row_level:
            levels_past_top_row = ( cl_xp - top_row['XP'] ) // each['XP']
            if top_row_level + levels_past_top_row > cl_level:
                level_up_classes.append( cl )
        else:
            for j, row in enumerate( xp_table ):
                if int( row['Level'] ) == cl_level + 1:
                    if cl_xp >= row['XP']:
                        level_up_classes.append( cl )
                    break

    return level_up_classes
