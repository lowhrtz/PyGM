import DbQuery
import SystemSettings
from GuiDefs import *
from ManageDefs import Manage


class ClientsWindow(Manage):
    
    def __init__(self):
        super().__init__('Client Manager', modality='unblock')

        characters = DbQuery.getTable('Characters')
        characters_indexed = {c['unique_id']: c for c in characters}

        # Define Internal Functions
        def fill_client_list(_fields):
            webapp = DbQuery.getTable('WebApp')
            cl_list = [(c['remote_addr'], c) for c in webapp]
            return {'Client List': cl_list}

        def client_tool_tip(item, _fields):
            character_id = item['character_id']
            character = characters_indexed[character_id]
            tt_ml = f'''\
<b>{character['Name']}</b><br />
<img height="200" src=data:image;base64,{character['Portrait']} />'''

            return tt_ml

        def remove_client(fields):
            current_client = fields['Client List Current']
            DbQuery.deleteRow('WebApp', 'remote_addr', current_client['remote_addr'])
            DbQuery.commit()
            web_app = DbQuery.getTable('WebApp')
            return {
                'Client List': [(i['remote_addr'], i) for i in web_app]
            }

        def select_character(fields):
            current_character = fields['Choose Character Data']
            character_class = SystemSettings.get_class_names(current_character)
            return {
                'Character Info': f'''\
<b>{current_character['Name']}</b><br />
Level {current_character['Level']} {character_class}<br />
<img height=200 src=data:image;base64,{current_character['Portrait']} />'''
            }

        def change_character(fields):
            current_character = fields['Choose Character Data']
            character_id = current_character['unique_id']
            current_client = fields['Client List Current']
            if current_client is None:
                return {}
            remote_addr = current_client['remote_addr']
            DbQuery.updateRow('WebApp', 'remote_addr', remote_addr, (remote_addr, character_id))
            DbQuery.commit()
            return {
                'Client List': DbQuery.getTable('WebApp')
            }

        # Define Widgets
        empty = Widget('', 'Empty')

        client_list = Widget('Client List', 'ListBox', col_span=2, row_span=2, tool_tip=client_tool_tip)
        remove_button = Widget('Remove Client', 'PushButton')
        change_button = Widget('Change Character', 'PushButton', tool_tip='Set current character to selected client.')
        character_chooser = Widget('Choose Character', 'ComboBox', align='Top', data=DbQuery.getTable('Characters'))
        character_info = Widget('Character Info', 'TextLabel', align='Center')

        # Add Actions
        self.add_action(Action('OnShow', empty, callback=fill_client_list))
        self.add_action(Action('OnShow', empty, callback=select_character))
        self.add_action(Action('FillFields', remove_button, callback=remove_client))
        self.add_action(Action('FillFields', character_chooser, callback=select_character))
        self.add_action(Action('FillFields', change_button, callback=change_character))

        # Initialize GUI
        self.add_row([client_list, empty, character_chooser])
        self.add_row([empty, empty, character_info])
        self.add_row([remove_button, change_button])
