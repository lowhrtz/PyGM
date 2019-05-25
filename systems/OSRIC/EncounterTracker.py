import Dice
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

        # Define internal functions

        # Define Widgets
        pc_team_surprise = Widget('PC Team Surprise', 'SpinBox')
        pc_team = Widget('PC Team', 'ListBox')
        monster_team_surprise = Widget('Monster Team Surprise', 'SpinBox')
        monster_team = Widget('Monster Team', 'ListBox')

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
