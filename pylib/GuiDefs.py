# -*- coding: utf-8 -*-
import resources
import Dice


class Widget(object):
    # field_name = None
    # widget_type = None
    # enable_edit = True
    # height = None
    # width = None
    # col_span = 1
    # row_span = 1
    # align = None
    # data = None

    def __init__(self, field_name, widget_type, enable_edit=True, height=None, width=None, col_span=1, row_span=1,
                 stretch=True, align=None, direction='Vertical', data=None, style=None, tool_tip=None):
        self.field_name = field_name
        self.widget_type = widget_type
        self.enable_edit = enable_edit
        self.height = height
        self.width = width
        self.col_span = col_span
        self.row_span = row_span
        self.stretch = stretch
        self.align = align
        self.direction = direction
        self.data = data
        self.style = style
        self.tool_tip = tool_tip

    def __str__(self):
        return self.field_name

    def get_field_name(self):
        return self.field_name

    def get_widget_type(self):
        return self.widget_type

    def is_edit_enabled(self):
        return self.enable_edit

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def get_col_span(self):
        return self.col_span

    def get_row_span(self):
        return self.row_span

    def get_stretch(self):
        return self.stretch

    def get_align(self):
        return self.align

    def get_direction(self):
        return self.direction

    def get_data(self):
        return self.data

    def get_style(self):
        return self.style

    def get_tool_tip(self):
        return self.tool_tip


class Action(object):

    def __init__(self, action_type, widget1=None, widget2=None, callback=None, data=None):
        self.action_type = action_type
        self.widget1 = widget1
        self.widget2 = widget2
        self.callback = callback
        self.data = data

    def get_action_type(self):
        return self.action_type

    def get_widget1(self):
        return self.widget1

    def get_widget2(self):
        return self.widget2

    def get_callback(self):
        return self.callback

    def get_data(self):
        return self.data


class Menu(object):

    def __init__(self, menu_name):
        self.menu_name = menu_name
        self.action_list = []

    def get_menu_name(self):
        return self.menu_name

    def add_action(self, action):
        self.action_list.append(action)

    def get_action_list(self):
        return self.action_list


class Window(object):

    def __init__(self, title=None, modality='block'):
        self.title = title
        self.modality = modality
        self.enabled = True
        self.menu_list = []
        self.action_list = []
        self.widget_matrix = []

    def add_menu(self, menu):
        self.menu_list.append(menu)

    def add_action(self, action):
        self.action_list.append(action)

    def add_row(self, widget_list):
        self.widget_matrix.append(widget_list)

    def get_menu_list(self):
        return self.menu_list

    def get_action_list(self):
        return self.action_list

    def get_widget_matrix(self):
        return self.widget_matrix

    def get_title(self):
        return self.title

    def get_modality(self):
        return self.modality


class DiceWindow(Window):
    def __init__(self, modality='unblock'):
        super().__init__(title='Dice', modality=modality)

        # Define Internal Functions
        def roll_dice(fields):
            return {
                'Result': Dice.rollString(fields['Dice String'])
            }

        def roll_percentile(_fields):
            tens = Dice.rollString('1d10-1')
            ones = Dice.rollString('1d10-1')
            if tens == 0 and ones == 0:
                percentile_result = '00'
            else:
                percentile_result = f'{tens or ""}{ones}%'

            return {
                'Result': percentile_result,
            }

        # Define Widgets
        dice_string_entry = Widget('Dice String', 'LineEdit', data='1d6')
        roll_button = Widget('Roll Button', 'PushButton', data='Roll')
        or_text = Widget('Or Text', 'TextLabel', data='<h3>OR</h3>', align='Center', col_span=2)
        roll_percentile_button = Widget('Roll Percentile', 'PushButton', align='Center', col_span=2)
        result = Widget('Result', 'LineEdit', align='Center', col_span=2)

        # Add Actions
        self.add_action(Action('FillFields', roll_button, callback=roll_dice))
        self.add_action(Action('FillFields', roll_percentile_button, callback=roll_percentile))

        # Initialize GUI
        self.add_row([dice_string_entry, roll_button])
        self.add_row([or_text])
        self.add_row([roll_percentile_button])
        self.add_row([result])


class WizardPage(Window):

    def __init__(self, page_id, title, page_type='Standard'):
        super().__init__()
        self.page_id = page_id
        self.title = title
        self.subtitle = ''
        self.page_type = page_type
        self.external_data = None

    def get_page_id(self):
        return self.page_id

    def get_title(self):
        return self.title

    def set_subtitle(self, subtitle):
        self.subtitle = subtitle

    def get_subtitle(self):
        return self.subtitle

    def initialize_page(self, fields, pages, external_data):
        return

    def is_complete(self, fields, pages, external_data):
        return True

    def on_change(self, fields, pages, external_data):
        return {}

    def get_next_page_id(self, fields, pages, external_data):
        return -2


class RollMethodsPage(WizardPage):

    def __init__(self, page_id, page_title, attributes, methods=None):
        super().__init__(page_id, page_title)

        self.set_subtitle('Choose which roll method you would like to use.')

        self.attributes = attributes
        self.attr_dict = None
        note = Widget('Banner', 'TextLabel', col_span=3,
                      data='<b>Note: </b>If the Next button is still disabled roll again or rearrange')
        self.add_row([note, ])
        banner = Widget('Banner', 'Image', row_span=len(attributes) + 2, data=resources.rollBanner_jpg)
        if methods is None:
            methods = ['Classic', 'Classic - Drop Lowest', 'Rearrange', 'Rearrange - Drop Lowest']
        methods = Widget('Methods_', 'ComboBox', align='Center', data=methods)
        self.add_action(Action('DragEnable', methods, callback=self.drag_enable))
        self.add_row([banner, methods])
        empty = Widget('', 'Empty')
        for attr in attributes:
            attr_widget = Widget(attr, 'LineEdit', width=40, stretch=False, align='Center')
            drag_image = Widget('{} Label'.format(attr), 'DragImage', data=(resources.diceSmall_png, attr, False))
            self.add_row([empty, attr_widget, drag_image, ])
        roll_button = Widget('Roll', 'PushButton', align='Center')
        self.add_action(Action('Fillfields', roll_button, callback=self.fill_attribute_fields))
        self.add_row([empty, roll_button, ])

    def drag_enable(self, fields, pages, external_data):
        de_return = {}
        enable = False
        if fields['Methods'].startswith('Rearrange'):
            enable = True
        for attr in self.attributes:
            de_return['{} Label'.format(attr)] = enable

        return de_return

    def fill_attribute_fields(self, fields, pages, external_data):
        self.attr_dict = fill = {}
        for attr in self.attributes:
            if fields['Methods'].endswith('Drop Lowest'):
                rolls = [Dice.rollString('d6') for _ in range(4)]
                # print(rolls)
                rolls.remove(min(rolls))
                # print(rolls)
                fill[attr] = sum(rolls)
            else:
                fill[attr] = Dice.rollString('3d6')

        return fill

    def is_complete(self, fields, pages, external_data):
        for attr in self.attributes:
            attr_field = fields[attr]
            if len(attr_field) == 0 or attr_field.isspace():
                return False
        return True


class Wizard(object):

    def __init__(self, title, modality='block'):
        self.title = title
        self.modality = modality
        self.wizard_pages = []

    def get_title(self):
        return self.title

    def get_modality(self):
        return self.modality

    def get_wizard_pages(self):
        return self.wizard_pages

    def add_wizard_page(self, wizard_page):
        self.wizard_pages.append(wizard_page)

    def accept(self, fields, pages, external_data):
        return
