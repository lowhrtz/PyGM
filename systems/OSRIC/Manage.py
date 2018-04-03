import base64
import DbQuery
import SystemSettings
from decimal import Decimal
from CharacterCreation import CharacterCreationWizard
from LevelUp import LevelUpWizard
from ManageDefs import Manage
from GuiDefs import *


class Characters(Manage):
    def __init__(self):

        empty_widget = Widget('', 'Empty')
        hr = Widget('hr', 'hr', col_span=4)

        intro = Widget('Intro', 'TextLabel', col_span=2, data='This is where you manage characters.')
        add_xp_button = Widget('Add XP', 'PushButton')
#        self.add_row( [ intro, empty_widget, add_xp_button ] )
#        test_field = Widget( 'Test Field', 'LineEdit' )
#        self.add_row( [ test_field ] )

        # character_list = Widget( 'Character List_', 'ListBox', row_span=4, data=DbQuery.getTable( 'Characters' ) )
        character_list = Widget('Character List_', 'ListBox', row_span=4)
        # name = Widget( 'Name', 'LineEdit', data='Lance the Impressive' )
        name = Widget('Name', 'LineEdit')
#        xp = Widget( 'XP', 'SpinBox', enable_edit=False )
        xp = Widget('XP', 'LineEdit', enable_edit=False)
        age = Widget('Age', 'SpinBox')
        self.add_row([character_list, name, xp, age])

        cl = Widget('Class', 'LineEdit', enable_edit=False)
        hp = Widget('HP', 'SpinBox')
        height = Widget('Height', 'LineEdit')
        self.add_row([empty_widget, cl, hp, height])

        alignment = Widget('Alignment', 'ComboBox', data=SystemSettings.alignment)
        ac = Widget('AC', 'SpinBox', enable_edit=False)
        weight = Widget('Weight', 'LineEdit')
        self.add_row([empty_widget, alignment, ac, weight])

        race = Widget('Race', 'LineEdit', enable_edit=False)
        level = Widget('Level', 'LineEdit', enable_edit=False)
        gender = Widget('Gender', 'ComboBox', data=SystemSettings.gender)
        self.add_row([empty_widget, race, level, gender])
        self.add_row([hr, ])

        portrait = Widget('Portrait_', 'Image', row_span=6, align='Center', data=image_data)
        str = Widget('STR', 'LineEdit', stretch=False)
        gp = Widget('GP', 'SpinBox', align='Center')
        proficiencies = Widget('Proficiencies', 'ListBox', row_span=6)
        self.add_row([portrait, str, gp, proficiencies])

        intel = Widget('INT', 'LineEdit', stretch=False)
        pp = Widget('PP', 'SpinBox', align='Center')
        self.add_row([empty_widget, intel, pp])

        wis = Widget('WIS', 'LineEdit', stretch=False)
        ep = Widget('EP', 'SpinBox', align='Center')
        self.add_row([empty_widget, wis, ep])

        dex = Widget('DEX', 'LineEdit', stretch=False)
        sp = Widget('SP', 'SpinBox', align='Center')
        self.add_row([empty_widget, dex, sp])

        con = Widget('CON', 'LineEdit', stretch=False)
        cp = Widget('CP', 'SpinBox', align='Center')
        self.add_row([empty_widget, con, cp])

        cha = Widget('CHA', 'LineEdit', stretch=False)
        self.add_row([empty_widget, cha, ])

        self.add_row([hr, ])

        equipment = Widget('Equipment', 'ListBox')
        spellbook = Widget('Spellbook', 'ListBox')
        daily_spells = Widget('Daily Spells', 'ListBox')
        daily_spells2 = Widget('Daily Spells 2_', 'ListBox')
        self.add_row([equipment, spellbook, daily_spells, daily_spells2])

#        pdf_button = Widget( 'Save PDF', 'PushButton' )
#        self.add_row( [ pdf_button, ] )
#        self.add_action( Action( 'SavePDF', pdf_button, character_list, callback=self.get_pdf_markup ) )
#        ch = Widget( 'Text Edit', 'TextEdit' )
#        self.add_row( [ ch, ] )

        self.add_action(Action('OnShow', character_list, callback=self.get_character_table))
        self.add_action(Action('FillFields', character_list, callback=self.fill_page))
#        self.add_action( Action( 'EntryDialog', add_xp_button, xp, callback=self.add_xp ) )

        file_menu = Menu('&File')
        file_menu.add_action(Action('FillFields', Widget('&Save Character', 'MenuAction'),
                                    callback=self.save_character))
        file_menu.add_action(Action('Wizard', Widget('&Create Character', 'MenuAction'), data=CharacterCreationWizard,
                                    callback=self.character_creator_callback))
        self.add_menu(file_menu)

        print_menu = Menu('&Print')
        print_menu.add_action(Action('SavePDF', Widget('&Save PDF', 'MenuAction'), character_list,
                                     callback=self.get_pdf_markup))
        print_menu.add_action(Action('PrintPreview', Widget('&Print Preview', 'MenuAction'), character_list,
                                     callback=self.get_pdf_markup))
        self.add_menu(print_menu)

        character_menu = Menu('&Character')
        character_menu.add_action(Action('EntryDialog', Widget('&Add XP', 'MenuAction'), hp, callback=self.add_xp))
        character_menu.add_action(Action('Wizard', Widget('&Level Up', 'MenuAction'), data=LevelUpWizard))
        character_menu.add_action(Action('EntryDialog', Widget('&Change Portrait', 'MenuAction'), portrait,
                                         callback=self.convert_image))
        equipment_data = {
            'fill_avail': self.equipment_fill,
            'slots': self.get_money_slots,
            'slots_name': 'Gold',
            'tool_tip': self.get_tool_tip,
            # 'category_field': None,
            'category_field': 'Category',
            'add': self.add_equipment,
            'remove': self.remove_equipment
        }
        self.current_money = 0
        character_menu.add_action(Action('ListDialog',
                                         Widget('&Buy/Sell Equipment', 'MenuAction'),
                                         equipment,
                                         callback=self.equipment_callback,
                                         data=equipment_data))
        self.add_menu(character_menu)

        self.class_table = DbQuery.getTable('Classes')

    def get_character_table(self, fields):
        return {'Character List': DbQuery.getTable('Characters')}

    def fill_page(self, fields):
        character_dict = fields['Character List Current']
        if character_dict is None:
            return {}
        class_table = DbQuery.getTable('Classes')
        race_table = DbQuery.getTable('Races')
        items_table = DbQuery.getTable('Items')
        spells_table = DbQuery.getTable('Spells')

        class_id_list = character_dict['Classes'].split('/')
        class_list = []
        for cl in class_table:
            if cl['unique_id'] in class_id_list:
                class_list.append(cl)
        if len(class_list) == 1:
            class_dict = class_list[0]
            class_string = class_dict['Name']
        else:
            class_dict = {
                'classes': class_list,
            }
            class_string = '/'.join([cl['Name'] for cl in class_dict['classes']])

        for race in race_table:
            if race['unique_id'] == character_dict['Race']:
                race_dict = race
                break

        equip_id_list = []
        spellbook_id_list = []
        daily_spells_id_list = []
        daily_spells2_id_list = []
        proficiency_id_dict = {}
        gp = pp = ep = sp = cp = 0
        for meta_row in character_dict['Characters_meta']:
            if meta_row['Type'] == 'Equipment':
                equip_id_list.append(meta_row['Entry_ID'])
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
            elif meta_row['Type'] == 'Proficiency':
                proficiency_id_dict[meta_row['Entry_ID']] = meta_row['Data']

        proficiency_list = []
        for prof in items_table:
            if prof['Is_Proficiency'].lower() == 'yes' and prof['unique_id'] in list(proficiency_id_dict.keys()):
                prof_name = prof['Name']
                prof['level'] = prof_level = proficiency_id_dict[prof['unique_id']]
                prof_add = ''
                if prof_level == 'S':
                    prof_add = ' (Specialised)'
                elif prof_level == '2XS':
                    prof_add = ' (Double Specialised)'
                prof_display = prof_name + prof_add
                proficiency_list.append((prof_display, prof))

        equipment_list = []
        for equip in items_table:
            if equip['unique_id'] in equip_id_list:
                equipment_list.append(equip)

        ac = SystemSettings.calculate_ac(character_dict, class_dict, race_dict, equipment_list)

        spellbook_list = []
        daily_spells_list = []
        daily_spells2_list = []
        for spell in spells_table:
            if spell['spell_id'] in spellbook_id_list:
                spellbook_list.append(spell)
            if spell['spell_id'] in daily_spells_id_list:
                daily_spells_list.append(spell)
            if spell['spell_id'] in daily_spells2_id_list:
                daily_spells2_list.append(spell)

        fill_dict = {
            'Name': character_dict['Name'],
            'Class': class_string,
            'Alignment': character_dict['Alignment'],
            'Race': race_dict['Name'],
            # 'XP' : int( character_dict['XP'] ),
            'XP': str(character_dict['XP']),
            'HP': int(character_dict['HP']),
            'AC': int(ac),
            'Level': character_dict['Level'],
            'Age': int(character_dict['Age']),
            'Height': character_dict['Height'],
            'Weight': character_dict['Weight'],
            'Gender': character_dict['Gender'],
            'STR': character_dict['STR'],
            'INT': character_dict['INT'],
            'WIS': character_dict['WIS'],
            'DEX': character_dict['DEX'],
            'CON': character_dict['CON'],
            'CHA': character_dict['CHA'],
            'Portrait': character_dict['Portrait'],
            'GP': int(gp),
            'PP': int(pp),
            'EP': int(ep),
            'SP': int(sp),
            'CP': int(cp),
            'Proficiencies': proficiency_list,
            'Equipment': equipment_list,
            'Spellbook': spellbook_list,
            'Daily Spells': daily_spells_list,
            'Daily Spells 2': daily_spells2_list,
        }

        return fill_dict

    def save_character(self, fields):
        if fields['Character List Current'] is None:
            return {}
        unique_id = fields['Character List Current']['unique_id']
        update_list = [
            unique_id,
            fields['Name'],
            fields['Level'],
            fields['XP'],
            fields['Gender'],
            fields['Alignment'],
            fields['Class'].lower().replace(' ', '_'),
            fields['Race'].lower().replace(' ', '_'),
            fields['HP'],
            fields['Age'],
            fields['Height'],
            fields['Weight'],
            fields['Portrait'],
            'jpg',
            fields['STR'],
            fields['INT'],
            fields['WIS'],
            fields['DEX'],
            fields['CON'],
            fields['CHA'],
            ]

        DbQuery.begin()

        success = DbQuery.updateRow('Characters', 'unique_id', unique_id, update_list)
        if success:
            DbQuery.deleteRow('Characters_meta', 'character_id', unique_id)

            for equip in fields['Equipment']:
                data_list = [unique_id, 'Equipment', equip['unique_id'], '', '']
                DbQuery.insertRow('Characters_meta', data_list)

            money_dict = {
                'gp': fields['GP'],
                'pp': fields['PP'],
                'ep': fields['EP'],
                'sp': fields['SP'],
                'cp': fields['CP']
            }
            for denomination in list(money_dict.keys()):
                DbQuery.insertRow('Characters_meta', [unique_id, 'Treasure',
                                                      denomination, money_dict[denomination], ''])

            for prof in fields['Proficiencies']:
                data_list = [unique_id, 'Proficiency', prof['unique_id'], prof['level'], prof['Notes']]
                DbQuery.insertRow('Characters_meta', data_list)

            for s in fields['Spellbook']:
                data_list = [unique_id, 'Spellbook', s['spell_id'], '', '']
                DbQuery.insertRow('Characters_meta', data_list)

            for s in fields['Daily Spells']:
                data_list = [unique_id, 'DailySpells', s['spell_id'], '', '']
                DbQuery.insertRow('Characters_meta', data_list)

            for s in fields['Daily Spells 2']:
                data_list = [unique_id, 'DailySpells2', s['spell_id'], '', '']
                DbQuery.insertRow('Characters_meta', data_list)

        DbQuery.commit()
        return self.get_character_table(fields)

    def character_creator_callback(self, character, fields):
        # character = pages['ReviewPage'].make_character_dict()

        data_list = [
            character['unique_id'],
            character['Name'],
            character['Level'],
            character['XP'],
            character['Gender'],
            character['Alignment'],
            character['Classes'],
            character['Race'],
            character['HP'],
            character['Age'],
            character['Height'],
            character['Weight'],
            character['Portrait'],
            character['Portrait_Image_Type'],
            character['STR'],
            character['INT'],
            character['WIS'],
            character['DEX'],
            character['CON'],
            character['CHA'],
        ]

        DbQuery.begin()
        row_id = DbQuery.insertRow('Characters', data_list)

        for meta_row in character['Characters_meta']:
            data_list = [
                meta_row['character_id'],
                meta_row['Type'],
                meta_row['Entry_ID'],
                meta_row['Data'],
                meta_row['Notes'],
            ]
            DbQuery.insertRow('Characters_meta', data_list)

        DbQuery.commit()

        character_table = DbQuery.getTable('Characters')
        return {'Character List': character_table}

    def get_pdf_markup(self, fields):
        character_dict = fields['Character List Current']
        if character_dict is None:
            return ()

        return SystemSettings.get_character_pdf_markup(character_dict)

    def add_xp(self, dialog_return, fields):

        xp_list = fields['XP'].split('/')
        add_xp = int(dialog_return) // len(xp_list)
        pc_class_split = fields['Character List Current']['Classes'].split('/')
        if len(pc_class_split) == 1:
            for cl in self.class_table:
                if cl['unique_id'] == pc_class_split[0]:
                    xp_bonus_string = cl['Experience_Bonus']
                    xp_bonus = self.parse_xp_bonus(xp_bonus_string, fields)
                    if xp_bonus:
                        add_xp = add_xp * (1 + Decimal(xp_bonus) / Decimal(100))
        for index, xp in enumerate(xp_list):
            xp_list[index] = int(xp) + int(add_xp)

        return {'XP': '/'.join(str(xp) for xp in xp_list)}

    def parse_xp_bonus(self, bonus, attr_dict):
        if bonus.lower() == 'None':
            return 0
        bonus_split = bonus.split()
        if len(bonus_split) == 2:
            attr = bonus_split[0]
            score = bonus_split[1].replace('+', '')
            if int(attr_dict[attr.upper()]) >= int(score):
                return 10
        else:
            score = bonus_split.pop().replace('+', '')
            attrs = [attr.strip().replace(',', '') for attr in bonus_split if attr.lower().find('and') != -1]
            bonus_in_effect = True
            for attr in attrs:
                if attr_dict[attr.upper()] < score:
                    bonus_in_effect = False
            if bonus_in_effect:
                return 10
        return 0

    def convert_image(self, filename, fields):
        with open(filename, 'rb') as image_file:
            data = base64.b64encode(image_file.read())
        return {'Portrait': data.decode()}

    def equipment_fill(self, owned_item_list, fields):
        return_list = []
        for item in DbQuery.getTable('Items'):
            if item['Cost'].lower() != 'not sold' and not item['Cost'].lower().startswith('proficiency'):
                return_list.append(('{} - {}'.format(item['Name'], item['Cost']), item))

        # These two lines sort the list to guarantee the tab order
        category_order = {'General': 0, 'Weapon': 1, 'Armour': 2, 'Clothing': 3}
        return_list.sort(key=lambda x: category_order.get(x[1].get('Category', 'General'), 4))

        return return_list

    def equipment_callback(self, owned_item_list, fields):
        # coin_dict = SystemSettings.get_coinage_from_float( float( '{0:.2f}'.format( self.current_money ) ) )
        coin_dict = SystemSettings.get_coinage_from_float(self.current_money)
        # print self.current_money
        return {
            'GP': coin_dict['gp'],
            'PP': coin_dict['pp'],
            'EP': coin_dict['ep'],
            'SP': coin_dict['sp'],
            'CP': coin_dict['cp'],
            'Equipment': owned_item_list,
        }

    def get_money_slots(self, fields):
        # money_dict = {}
        # for row in fields['Character List Current']['Characters_meta']:
        #     if row['Entry_ID'] in list( SystemSettings.economy.keys() ):
        #         money_dict[ row['Entry_ID'] ] = int( row['Data'] )
        money_dict = {
            'gp': fields['GP'],
            'pp': fields['PP'],
            'ep': fields['EP'],
            'sp': fields['SP'],
            'cp': fields['CP'],
        }

        self.current_money = money_slots = Decimal(str(SystemSettings.get_float_from_coinage(money_dict)))
        return '{0:.2f}'.format(money_slots)

    def convert_cost_string(self, cost_string):
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
                ratio = Decimal(str(SystemSettings.economy[denomination]))
                final_cost = ratio * cost
            except KeyError:
                final_cost = cost
        else:
            final_cost = cost

        return final_cost

    def add_equipment(self, item, fields):
        cost = self.convert_cost_string(item['Cost'])
        if cost < self.current_money:
            self.current_money -= cost
            return {
                'valid': True,
                'slots_new_value': '{0:.2f}'.format( self.current_money ),
                # 'remove': True,
                'new_display': item['Name'],
             }
        else:
            return {}

    def remove_equipment(self, item, fields):
        cost_string = item['Cost']
        if cost_string.lower() == 'not sold':
            return {}
        else:
            cost = self.convert_cost_string(cost_string)
            self.current_money += cost
            return {
                'valid': True,
                'slots_new_value': '{0:.2f}'.format( self.current_money ),
                # 'replace': True,
                'new_display': item['Name'],
            }

    def get_tool_tip(self, item, fields):
        return '{}<br /><b>{}</b>'.format(item['Name'], item['Cost'])


image_data = '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\
0dHX//Z'
