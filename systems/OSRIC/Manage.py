import base64
import DbQuery
import mimetypes
import os
import SystemSettings
import time
from Common import callback_factory_1param
from decimal import Decimal
from CharacterCreation import CharacterCreationWizard
from LevelUp import LevelUpWizard
from ManageDefs import Manage
from GuiDefs import *
from wsgiref.simple_server import make_server

mimetypes.add_type('application/font', '.woff2')


class Characters(Manage):
    def __init__(self):

        super().__init__()
        empty_widget = Widget('', 'Empty')
        hr = Widget('hr', 'hr', col_span=4)

        intro = Widget('Intro', 'TextLabel', col_span=2, data='This is where you manage characters.')
        add_xp_button = Widget('Add XP', 'PushButton')
        #        self.add_row( [ intro, empty_widget, add_xp_button ] )
        #        test_field = Widget( 'Test Field', 'LineEdit' )
        #        self.add_row( [ test_field ] )

        # character_list = Widget( 'Character List_', 'ListBox', row_span=4, data=DbQuery.getTable( 'Characters' ) )
        character_list = Widget('Character List_', 'ListBox', col_span=2, row_span=4)
        # name = Widget( 'Name', 'LineEdit', data='Lance the Impressive' )
        name = Widget('Name', 'LineEdit')
        #        xp = Widget( 'XP', 'SpinBox', enable_edit=False )
        xp = Widget('XP', 'LineEdit', enable_edit=False)
        age = Widget('Age', 'SpinBox')
        self.add_row([character_list, empty_widget, name, xp, age])

        cl = Widget('Class', 'LineEdit', enable_edit=False)
        hp = Widget('HP', 'SpinBox')
        height = Widget('Height', 'LineEdit')
        self.add_row([empty_widget, empty_widget, cl, hp, height])

        alignment = Widget('Alignment', 'ComboBox', data=SystemSettings.alignment)
        ac = Widget('AC', 'SpinBox', enable_edit=False)
        weight = Widget('Weight', 'LineEdit')
        self.add_row([empty_widget, empty_widget, alignment, ac, weight])

        race = Widget('Race', 'LineEdit', enable_edit=False)
        level = Widget('Level', 'LineEdit', enable_edit=False)
        gender = Widget('Gender', 'ComboBox', data=SystemSettings.gender)
        self.add_row([empty_widget, empty_widget, race, level, gender])
        self.add_row([hr, ])

        portrait = Widget('Portrait_', 'Image', row_span=6, align='Right', data=image_data)
        str = Widget('STR', 'LineEdit', width=50, stretch=False)
        gp = Widget('GP', 'SpinBox', align='Center')
        proficiencies = Widget('Proficiencies', 'ListBox', row_span=6)
        equipment = Widget('Equipment', 'ListBox', row_span=6)
        self.add_row([portrait, str, gp, proficiencies, equipment])

        intel = Widget('INT', 'LineEdit', width=50, stretch=False)
        pp = Widget('PP', 'SpinBox', align='Center')
        self.add_row([empty_widget, intel, pp])

        wis = Widget('WIS', 'LineEdit', width=50, stretch=False)
        ep = Widget('EP', 'SpinBox', align='Center')
        self.add_row([empty_widget, wis, ep])

        dex = Widget('DEX', 'LineEdit', width=50, stretch=False)
        sp = Widget('SP', 'SpinBox', align='Center')
        self.add_row([empty_widget, dex, sp])

        con = Widget('CON', 'LineEdit', width=50, stretch=False)
        cp = Widget('CP', 'SpinBox', align='Center')
        self.add_row([empty_widget, con, cp])

        cha = Widget('CHA', 'LineEdit', width=50, stretch=False)
        self.add_row([empty_widget, cha, ])

        self.add_row([hr, ])

        spellbook = Widget('Spellbook', 'ListBox', col_span=2)
        daily_spells = Widget('Daily Spells', 'ListBox')
        daily_spells2 = Widget('Daily Spells 2_', 'ListBox')
        dail_spells3 = Widget('Daily Spells 3_', 'ListBox')
        self.add_row([spellbook, empty_widget, daily_spells, daily_spells2, dail_spells3])

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
        character_menu.add_action(Action('Wizard', Widget('&Level Up', 'MenuAction'), data=LevelUpWizard,
                                         callback=self.level_up_fill))
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

        def save_background(new_text, fields):
            DbQuery.update_cols('Characters', 'unique_id',
                                fields['Character List Current']['unique_id'], ['Background'], [new_text])
            DbQuery.commit()
            return {}

        def get_background(fields):
            character_id = fields['Character List Current']['unique_id']
            for character in DbQuery.getTable('Characters'):
                if character['unique_id'] == character_id:
                    return character['Background']
            return fields['Character List Current']['Background']

        character_menu.add_action(Action('EntryDialog', Widget('&Background', 'MenuAction'), Widget('', 'TextEdit'),
                                         callback=save_background, data=get_background))
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
        daily_spells3_id_list = []
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
            elif meta_row['Type'] == 'DailySpells3':
                daily_spells3_id_list.append(meta_row['Entry_ID'])
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
        daily_spells3_list = []
        for spell in spells_table:
            if spell['spell_id'] in spellbook_id_list:
                spellbook_list.append(spell)
            if spell['spell_id'] in daily_spells_id_list:
                for _ in range(daily_spells_id_list.count(spell['spell_id'])):
                    daily_spells_list.append(spell)
            if spell['spell_id'] in daily_spells2_id_list:
                for _ in range(daily_spells2_id_list.count(spell['spell_id'])):
                    daily_spells2_list.append(spell)
            if spell['spell_id'] in daily_spells3_id_list:
                for _ in range(daily_spells3_id_list.count(spell['spell_id'])):
                    daily_spells3_list.append(spell)

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
            'Daily Spells 3': daily_spells3_list,
        }

        return fill_dict

    def save_character(self, fields):
        if fields['Character List Current'] is None:
            return {}
        unique_id = fields['Character List Current']['unique_id']
        background = fields['Character List Current']['Background']
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
            background,
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

            for s in fields['Daily Spells 3']:
                data_list = [unique_id, 'DailySpells3', s['spell_id'], '', '']
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
            '',
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

    def level_up_fill(self, level_up_return, fields):
        return level_up_return

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
                        add_xp = int(add_xp * (1 + Decimal(xp_bonus) / Decimal(100)))
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
            attrs = [attr.strip().replace(',', '') for attr in bonus_split if attr.lower().find('and') == -1]
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
                'slots_new_value': '{0:.2f}'.format(self.current_money),
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
                'slots_new_value': '{0:.2f}'.format(self.current_money),
                # 'replace': True,
                'new_display': item['Name'],
            }

    def get_tool_tip(self, item, fields):
        return '{}<br /><b>{}</b>'.format(item['Name'], item['Cost'])


class Campaigns(Manage):
    def __init__(self):

        super().__init__()
        empty_widget = Widget('', 'Empty')
        hr = Widget('hr', 'hr', col_span=4)

        # test = Widget('Test', 'TextLabel', col_span=1, data='Placeholder Text.')
        # self.add_row([test, ])
        # print(self.widget_matrix)
        # button = Widget('Button', 'PushButton', )
        # self.add_row([button, ])
        # self.add_action(Action('CallbackOnly', button, callback=self.push_button))

        campaign_list = Widget('Campaign List_', 'ListBox', col_span=2, row_span=3)
        self.add_action(Action('OnShow', campaign_list, callback=self.get_campaign_table))
        name = Widget('Name', 'LineEdit')
        setting = Widget('Setting', 'LineEdit')
        ingame_date = Widget('In-Game Date', 'LineEdit')
        resource_select = Widget('Resources', 'ResourceSelect', col_span=3, data=self.resource_callback)
        add_res_button = Widget('Add Resource', 'PushButton')
        self.add_action(Action('FileDialog', add_res_button, callback=self.add_resource, data='All Files (*)'))
        remove_res_button = Widget('Remove Resource', 'PushButton')
        self.add_action(Action('FillFields', remove_res_button, callback=self.remove_resource))
        pc_list = Widget('PCs', 'ListBox', col_span=2)
        npc_list = Widget('NPCs', 'ListBox')

        self.add_action(Action('OnShow', campaign_list, callback=self.get_campaign_table))
        self.add_action(Action('FillFields', campaign_list, callback=self.fill_page))

        file_menu = Menu('&File')
        # file_menu.add_action(Action('ListDialog', Widget('&Choose Campaign', 'MenuAction'),
        #                             callback=self.choose_campaign))
        file_menu.add_action(Action('FileDialog', Widget('&Open Adventure', 'MenuAction'),
                                    callback=self.open_adventure, data='Adventure XML (*.xml)'))
        file_menu.add_action(Action('FillFields', Widget('&Save Campaign', 'MenuAction'),
                                    callback=self.save_campaign))
        file_menu.add_action(Action('Wizard', Widget('&Create Campaign', 'MenuAction'), data=CampaignCreator,
                                    callback=self.create_campaign_callback))
        self.add_menu(file_menu)

        tools_menu = Menu('&Tools')
        tools_menu.add_action(Action('Window', Widget('&Server', 'MenuAction'),
                                     callback=self.open_server))
        tools_menu.add_action(Action('Window', Widget('Sound &Board', 'MenuAction'),
                                     callback=self.open_sound_board))
        tools_menu.add_action(Action('Window', Widget('&Encounters', 'MenuAction'),
                                     callback=lambda f: self.Encounters(f)))

        self.add_menu(tools_menu)

        campaign_menu = Menu('&Campaign')
        add_rem_char_data = {
            'fill_avail': self.get_available_characters,
            'add': self.add_character,
            'remove': self.remove_character,
        }
        campaign_menu.add_action(Action('ListDialog', Widget('Add/Remove &PCs', 'MenuAction'), pc_list,
                                        data=add_rem_char_data, callback=self.add_remove_pc_callback))
        campaign_menu.add_action(Action('ListDialog', Widget('Add/Remove &NPCs', 'MenuAction'), npc_list,
                                        data=add_rem_char_data, callback=self.add_remove_npc_callback))

        self.add_menu(campaign_menu)

        # Initialize GUI Layout
        self.add_row([campaign_list, empty_widget, name])
        self.add_row([empty_widget, empty_widget, setting])
        self.add_row([empty_widget, empty_widget, ingame_date, ])
        self.add_row(([resource_select, ]))
        self.add_row([add_res_button, remove_res_button])
        self.add_row([pc_list, empty_widget, npc_list])

    def get_campaign_table(self, fields):
        return {'Campaign List': DbQuery.getTable('Campaigns')}

    def push_button(self, fields):
        print(fields)

    def open_adventure(self, filename, fields):
        print(filename)
        return {}

    def open_server(self, fields):
        adventure_window = self.AdventureServer(fields)
        return adventure_window

    def open_sound_board(self, fields):
        sound_board_window = self.SoundBoard(fields)
        return sound_board_window

    def create_campaign_callback(self, campaign, fields):
        data_list = [campaign['unique_id'],
                     campaign['Name'],
                     campaign['Setting'],
                     campaign['In-Game_Date']]

        DbQuery.begin()
        DbQuery.insertRow('Campaigns', data_list)

        for meta_row in campaign['Campaigns_meta']:
            data_list = [meta_row['campaign_id'],
                         meta_row['Type'],
                         meta_row['Entry_ID'],
                         meta_row['Data'],
                         meta_row['Notes']]
            DbQuery.insertRow('Campaigns_meta', data_list)

        DbQuery.commit()

        campaign_table = DbQuery.getTable('Campaigns')
        return {'Campaign List': campaign_table}

    def save_campaign(self, fields):
        current_campaign = fields['Campaign List Current']
        unique_id = current_campaign['unique_id']
        update_list = [
            unique_id,
            fields['Name'],
            fields['Setting'],
            fields['In-Game Date'],
        ]

        DbQuery.begin()
        success = DbQuery.updateRow('Campaigns', 'unique_id', unique_id, update_list)
        if success:
            DbQuery.deleteRow('Campaigns_meta', 'campaign_id', unique_id)
            for res in fields['Resources']:
                data_list = [
                    unique_id,
                    res['Type'],
                    res['Entry_ID'],
                    res['Data'],
                    '',
                ]
                DbQuery.insertRow('Campaigns_meta', data_list)
            for pc in fields['PCs']:
                data_list = [
                    unique_id,
                    'pc',
                    pc['unique_id'],
                    '',
                    '',
                ]
                DbQuery.insertRow('Campaigns_meta', data_list)
            for npc in fields['NPCs']:
                data_list = [
                    unique_id,
                    'npc',
                    npc['unique_id'],
                    '',
                    '',
                ]
                DbQuery.insertRow('Campaigns_meta', data_list)
        DbQuery.commit()
        return self.get_campaign_table(fields)

    def fill_page(self, fields):
        current_campaign = fields['Campaign List Current']
        if current_campaign is None:
            return {}

        char_table = DbQuery.getTable('Characters')

        def get_char_record(char):
            for record in char_table:
                if record['unique_id'] == char['Entry_ID']:
                    return record

        res_list = [(res['Entry_ID'], res) for res in current_campaign['Campaigns_meta']
                    if res['Type'] == 'image' or res['Type'] == 'audio' or res['Type'] == 'font']
        pc_list = [get_char_record(pc) for pc in current_campaign['Campaigns_meta']
                   if pc['Type'] == 'pc']
        npc_list = [get_char_record(npc) for npc in current_campaign['Campaigns_meta']
                    if npc['Type'] == 'npc']
        return {'Name': current_campaign['Name'],
                'Setting': current_campaign['Setting'],
                'In-Game Date': current_campaign['In-Game_Date'],
                'Resources': res_list,
                'PCs': pc_list,
                'NPCs': npc_list}

    def resource_callback(self, resource, fields):
        res_type = resource['Type']
        res_data = resource['Data']
        return res_type, res_data

    def add_resource(self, filename, fields):
        mime_type, _ = mimetypes.guess_type(filename)
        mime_cat, mime_spec = mime_type.split('/')
        if mime_cat == 'application' and 'font' in mime_spec:
            mime_cat = 'font'
        with open(filename, 'rb') as resource_file:
            data = base64.b64encode(resource_file.read())

        entry_id = os.path.basename(filename)
        return {'Resources': (entry_id, {'Data': data.decode(), 'Type': mime_cat, 'Entry_ID': entry_id})}

    def remove_resource(self, fields):
        return {'Resources': ()}

    # def build_char_meta(self, char):
    #     return {
    #         'Entry_ID': char['unique_id'],
    #     }

    def get_available_characters(self, owned_items, fields):
        character_table = DbQuery.getTable('Characters')
        return [char for char in character_table if char not in owned_items]

    def add_character(self, item, fields):
        return {'valid': True, 'remove': True}

    def remove_character(self, item, fields):
        return {'valid': True, 'replace': True}

    def add_remove_pc_callback(self, chosen_pcs, fields):
        return {'PCs': chosen_pcs}

    def add_remove_npc_callback(self, chosen_npcs, fields):
        return {'NPCs': chosen_npcs}

    class AdventureServer(Manage):
        def __init__(self, fields):

            super().__init__(modality='unblock')
            empty = Widget('', 'Empty')
            hr = Widget('hr', 'hr', col_span=4)
            # test = Widget('Test', 'TextLabel', data='Adventure Server', align='Center', col_span=3)
            # self.add_row([test, ])

            adventure_title = Widget('Title', 'LineEdit', col_span=3)
            title_background = Widget('Title Background', 'PushButton')
            self.add_action(Action('FileDialog', title_background, callback=self.title_background_callback))
            clear_title_bg = Widget('Clear Title BG', 'PushButton')
            self.add_action(Action('FillFields', clear_title_bg, callback=lambda f: {'Title BG Preview': ''}))
            title_bg_preview = Widget('Title BG Preview_', 'Image', data=None, row_span=3)
            background_color = Widget('Background Color', 'PushButton')
            self.add_action(Action('ColorDialog', background_color, callback=self.color_dialog_callback))
            background_color_preview = Widget('Background Color Preview_', 'Image', data='#ffffff|50|20')
            chosen_color = Widget('Chosen Color_', 'LineEdit', data='#ffffff', enable_edit=False, stretch=False)
            font_radio_button = Widget('Font Radio Button', 'RadioButton', data=['Built-In Font', 'Custom Font'],
                                       row_span=2)
            built_in_fonts = Widget('BuiltIn Fonts_', 'ComboBox',
                                    data=['Times', 'Helvetica', 'Arial', 'Georgia', 'Courier New', 'Monaco'],
                                    col_span=2)
            custom_font_list = [res['Entry_ID'] for res in fields['Resources'] if res['Type'] == 'font']
            custom_fonts = Widget('Custom Fonts_', 'Combobox',
                                  data=custom_font_list,
                                  col_span=2)
            handout_text = Widget('Handout Text', 'TextLabel', data='Handouts')
            # self.add_row([handout_text, ])
            # self.resources = {}
            # for res in fields['Resources']:
            #    entry_id = res['Entry_ID'], background_color_preview
            #    self.resources[entry_id] = res
            #    r = Widget(entry_id, 'Checkbox')
            #    self.add_action(Action('CallbackOnly', r, callback=callback_factory_1param(self.checkbox_callback, r)))
            #    self.add_row([r, ])
            image_resources_data = {'fill_avail': self.fill_image_resources,
                                    'add': self.add_image_resource,
                                    'remove': self.remove_image_resource}
            image_resources = Widget('Image Resources', 'DualList', data=image_resources_data, col_span=3, row_span=2)
            change_handouts_background = Widget('Change Handouts Background', 'PushButton')
            self.add_action(Action('FileDialog', change_handouts_background,
                                   callback=self.change_handouts_background_callback))
            default_handouts_background = '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'
            handouts_background_preview = Widget('Handouts Background Preview', 'Image',
                                                 data=default_handouts_background,
                                                 style='border: 3px inset grey;')
            handouts_background_light_dark = Widget('Handouts Background Light Dark', 'RadioButton',
                                                    data=['Light Image', 'Dark Image'])

            # GUI layout
            self.add_row([adventure_title, empty, empty, title_background, clear_title_bg])
            self.add_row([background_color, background_color_preview, chosen_color, title_bg_preview])
            self.add_row([font_radio_button, built_in_fonts])
            self.add_row([empty, custom_fonts])
            self.add_row([hr, ])
            self.add_row([handout_text, ])
            self.add_row([image_resources, empty, empty, change_handouts_background])
            self.add_row([empty, empty, empty, handouts_background_preview, handouts_background_light_dark])

            # Initialize web server
            from WebApp import adventure
            self.web_server = make_server('', 1234, adventure)
            self.web_server.timeout = 0
            self.web_server.base_environ['Extern'] = fields
            self.web_server.base_environ['Fields'] = {}
            self.add_action(Action('OnShow', empty, callback=lambda x: {'Image Resources': []}))
            self.add_action(Action('Timer', empty, callback=self.handle_request, data=1))
            self.add_action(Action('OnClose', empty, callback=self.on_close))

        def handle_request(self, fields):
            self.web_server.base_environ['Fields'] = fields
            self.web_server.handle_request()
            return {}

        # def checkbox_callback(self, fields, box):
        #     field_name = box.get_field_name()
        #     checked = fields[field_name]
        #     res = self.resources[field_name]
        #     if checked and res['Type'] == 'image':
        #         print(field_name, ':', res['Type'], ':', res['Data'][:20])

        def color_dialog_callback(self, color, fields):
            return {'Chosen Color': color, 'Background Color Preview': f'{color}|50|20'}

        def fill_image_resources(self, owned_items, fields):
            image_resources = []
            for res in self.web_server.base_environ['Extern']['Resources']:
                if res['Type'] == 'image':
                    image_resources.append((res['Entry_ID'], res))
            return image_resources

        def add_image_resource(self, item, fields):
            return {'valid': True, 'remove': True, 'new_display': item['Entry_ID']}

        def remove_image_resource(self, item, fields):
            return {'valid': True, 'replace': True, 'new_display': item['Entry_ID']}

        def change_handouts_background_callback(self, filename, fields):
            with open(filename, 'rb') as bg_file:
                data = base64.b64encode(bg_file.read())
            return {'Handouts Background Preview': data.decode()}

        def title_background_callback(self, filename, fields):
            with open(filename, 'rb') as title_bg:
                data = base64.b64encode(title_bg.read())
            return {'Title BG Preview': data.decode()}

        def on_close(self, _):
            self.web_server.server_close()

    class SoundBoard(Manage):

        def __init__(self, fields):

            super().__init__(modality='unblock')
            empty = Widget('', 'Empty')
            hr = Widget('hr', 'hr', col_span=4)

            sounds = [res for res in fields['Resources'] if res['Type'] == 'audio']
            row = []
            for i, sound in enumerate(sounds):
                button = Widget(sound['Entry_ID'], 'PushButton')
                self.add_action(Action('PlaySound', button,
                                       callback=callback_factory_1param(self.play_sound_callback, sound)))
                if i > 0 and 5 % i == 0:
                    row.append(button)
                    self.add_row(row)
                    row = []
                else:
                    row.append(button)
            if row:
                self.add_row(row)

        def play_sound_callback(self, fields, sound):
            return sound['Data']

    class Encounters(Manage):

        def __init__(self, fields):
            super().__init__(modality='unblock')

            # Define internal functions

            def get_available_characters(owned_items, f):
                # print(owned_items)
                pcs = fields['PCs']
                pc_ids = [pc['unique_id'] for pc in pcs]
                # print(pc_ids)
                pcs = [c for c in DbQuery.getTable('Characters') if c['unique_id'] in pc_ids]
                avail_pcs = []
                for pc in pcs:
                    if pc not in owned_items:
                        avail_pcs.append(pc)
                return avail_pcs

            def add_ally(ally, f):
                return {
                    'valid': True,
                    'remove': True,
                }

            def remove_ally(ally, f):
                return {
                    'valid': True,
                    'replace': True,
                }

            def add_pc_ally_callback(chosen_list, f):
                # print(chosen_list, f)
                return {'PC Team': chosen_list}

            # Define Widgets
            empty = Widget('', 'Empty')

            pc_team = Widget('PC Team', 'ListBox')
            monster_team = Widget('Monster Team', 'ListBox')
            add_pc_ally = Widget('Add PC/Ally', 'PushButton')
            add_pc_ally_data = {
                'fill_avail': get_available_characters,
                'tool_tip': SystemSettings.character_tool_tip,
                'add': add_ally,
                'remove': remove_ally,
            }

            # Add Actions
            self.add_action(Action('ListDialog', add_pc_ally, pc_team,
                                   callback=add_pc_ally_callback, data=add_pc_ally_data))

            # Initialize GUI
            self.add_row([pc_team, empty, monster_team])
            self.add_row([add_pc_ally])


class CampaignCreator(Wizard):

    def __init__(self):
        super().__init__('Create Campaign')

        self.add_wizard_page(CampaignIntro())
        self.add_wizard_page(CampaignResources())

    def accept(self, fields, pages, external_data):
        unique_id = '{}-{}-{}'.format(fields['Name'], fields['Setting'], time.time())
        campaign = {'unique_id': unique_id,
                    'Name': fields['Name'],
                    'Setting': fields['Setting'],
                    'In-Game_Date': fields['In-Game Date'],
                    'Campaigns_meta': []}
        for resource in fields['Resource List']:
            meta_row = {'campaign_id': unique_id,
                        'Type': resource['Type'],
                        'Entry_ID': resource['Entry_ID'],
                        'Data': resource['Data'],
                        'Notes': ''}
            campaign['Campaigns_meta'].append(meta_row)
        return campaign


class CampaignIntro(WizardPage):

    def __init__(self):
        super().__init__(0, 'Create a Campaign')
        self.set_subtitle('Create a new campaign.')

        empty = Widget('Empty', 'Empty')
        self.add_row([empty, ])

        name = Widget('Name', 'LineEdit')
        self.add_row([name, ])
        setting = Widget('Setting', 'LineEdit')
        self.add_row([setting, ])
        date = Widget('In-Game Date', 'LineEdit')
        self.add_row([date, ])

    def is_complete(self, fields, pages, external_data):
        if len(fields['Name']) == 0 or fields['Name'].isspace() \
                or len(fields['Setting']) == 0 or fields['Setting'].isspace():
            return False
        return True


class CampaignResources(WizardPage):

    def __init__(self):
        super().__init__(1, 'Resources')
        self.set_subtitle('Add Resources')

        text = Widget('ResourceText', 'TextLabel', align='Center',
                      data='Add resources such as images or audio.', col_span=2)
        self.add_row([text, ])
        add_button = Widget('Add Resource', 'PushButton', align='Center')
        self.add_action(Action('FileDialog', add_button, callback=self.add_resource, data='All Files (*)'))
        remove_button = Widget('Remove Resource', 'PushButton', align='Center')
        self.add_action(Action('FillFields', remove_button, callback=self.remove_resource))
        self.add_row([add_button, remove_button])
        resource_list = Widget('Resource List_', 'ListBox', col_span=2)
        self.add_row([resource_list, ])

    def add_resource(self, filename, fields, pages, external_data):
        mime_type, _ = mimetypes.guess_type(filename)
        mime_cat, mime_spec = mime_type.split('/')
        if mime_cat == 'application' and 'font' in mime_spec:
            mime_cat = 'font'
        # print(mime_cat, mime_spec)
        with open(filename, 'rb') as resource_file:
            data = base64.b64encode(resource_file.read())

        entry_id = os.path.basename(filename)
        return {'Resource List': (filename, {'Data': data.decode(), 'Type': mime_cat, 'Entry_ID': entry_id})}

    def remove_resource(self, fields, pages, external_data):
        return {'Resource List': ()}


image_data = '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\
0dHX//Z'
