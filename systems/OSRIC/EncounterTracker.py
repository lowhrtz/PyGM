import Dice
import SystemSettings
import DbQuery
from GuiDefs import *


class EncounterTrackerWizard(Wizard):

    def __init__(self):
        super().__init__('Encounter Tracker')

        self.add_wizard_page(EncounterIntro())
        self.add_wizard_page(SurprisePage())


class EncounterIntro(WizardPage):
    def __init__(self):
        super().__init__(0, 'Encounter Tracker')
        self.set_subtitle('Encounter Wizard')

        # Define internal functions

        # Define Widgets
        info = '''The encounter is about to begin. Remember the order of events:<ol><li>Determine Surprise</li>
<li>Declare Spells and General Actions</li><li>Determine Initiative</li>
<li>Party with initiative acts first and results take effect</li>
<li>Party that lost initiative acts and results take effect</li>
<li>The round is complete (start the next round on step 2)</li></ol>'''
        intro_text = Widget('Intro Text', 'TextLabel', align='Center', data=info)

        # Add Actions

        # Initialize GUI
        self.add_row([intro_text])


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

        # Define Widgets
        pc_team_surprise = Widget('PC Team Surprise', 'SpinBox')
        pc_team = Widget('PC Team', 'ListBox', tool_tip=pc_tool_tip)
        monster_team_surprise = Widget('Monster Team Surprise', 'SpinBox')
        monster_team = Widget('Monster Team', 'ListBox', tool_tip=enemy_tool_tip)

        # Add Actions

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
