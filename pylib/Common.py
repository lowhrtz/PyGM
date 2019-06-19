import os
import Dice
import resources
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QColor, QImage, QPixmap


def find_image(system_path, table_name, unique_id):
    extensions = ['jpg', 'jpeg', 'gif', 'png', ]
    # base_path_name = os.path.join( THIS_DIR, '{}/portraits/{}/{}'.format( system_path, table_name, unique_id ) )
    base_path_name = os.path.join(system_path, 'portraits/{}/{}'.format(table_name, unique_id))
    for ext in extensions:
        full_name = '{}.{}'.format(base_path_name, ext)
        if os.path.isfile(full_name):
            return full_name

    for ext in extensions:
        # default_image = os.path.join( THIS_DIR, '{}/portraits/default.{}'.format( system_path, ext ) )
        default_image = os.path.join(system_path, 'portraits/default.{}'.format(ext))
        if os.path.isfile(default_image):
            return default_image

    system_parent = os.path.abspath(os.path.join(system_path, os.pardir))
    base_dir = os.path.abspath(os.path.join(system_parent, os.pardir))
    return os.path.join(base_dir, 'images/noImage.jpg')


def get_default_pixmap(system_path):
    extensions = ['jpg', 'jpeg', 'gif', 'png', ]
    for ext in extensions:
        default_image = os.path.join(system_path, 'portraits/default.{}'.format(ext))
        if os.path.isfile(default_image):
            return QPixmap(default_image)

    return get_pixmap_from_base64(resources.noImage_jpg)


def get_pixmap_from_base64(base64):
    byte_array = QtCore.QByteArray.fromBase64(base64.encode())
    image = QImage.fromData(byte_array)
    pixmap = QPixmap(image)
    if pixmap.height() > 200 or pixmap.width() > 200:
        pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
    return pixmap


def get_pixmap_from_hex_color(hex_color, width=200, height=200):
    image = QImage(width, height, QImage.Format_RGB888)
    color = QColor(hex_color)
    for y in range(height):
        for x in range(width):
            image.setPixelColor(x, y, color)
    return QPixmap.fromImage(image)


def callback_factory(callback, *args, **kwargs):
    return lambda: callback(*args, **kwargs)


def callback_factory_1param(callback, *args, **kwargs):
    return lambda x: callback(x, *args, **kwargs)


def callback_factory_2param(callback, *args, **kwargs):
    return lambda x, y: callback(x, y, *args, **kwargs)


def remove_item_from_listbox(listbox):
    remove_index = listbox.currentRow()
    if remove_index == -1:
        return
    listbox.takeItem(remove_index)


def add_item_to_listbox(listbox, item, tool_tip=None, fields=None, original_list=None, wizard=None, index=None):
    if type(item).__name__ == 'str':
        list_item = QListWidgetItem()
        list_item.setText(item)
        item_dict = {}
    elif type(item).__name__ == 'dict':
        item_dict = item
        table_name = item['TableName']
        # Import DbQuery now because it will fail on initial loading of this module
        import DbQuery
        display_col = DbQuery.getDisplayCol(table_name)
        display = item[display_col]
        list_item = QListWidgetItem()
        list_item.setText(display)
        list_item.setData(QtCore.Qt.UserRole, item)
    elif type(item).__name__ == 'tuple':
        display = item[0]
        item_dict = item[1]
        list_item = QListWidgetItem()
        list_item.setText(display)
        list_item.setData(QtCore.Qt.UserRole, item_dict)
    else:
        print('Wrong format for item: {}\nExpected str, dict or tuple got {}'.format(item, type(item).__name__))
        return

    if tool_tip:
        if wizard:
            tool_tip_return = tool_tip(item_dict, fields, wizard.wizard_pages, wizard.external_data)
        else:
            tool_tip_return = tool_tip(item_dict, fields)
        list_item.setToolTip(tool_tip_return)

    if original_list:
        list_item.original_list = original_list
    if index is None:
        listbox.addItem(list_item)
    else:
        listbox.item(index).setText(list_item.text())


def fill_listbox(listbox, fill, tool_tip=None, fields=None, original_list=None, wizard=None):
    listbox.clear()
    for item in fill:
        add_item_to_listbox(listbox, item, tool_tip, fields, original_list, wizard)


class Range:
    def __init__(self, start, stop):
        self.range = range(start, stop + 1)

    def __iter__(self):
        return iter(self.range)

    def __getitem__(self, item):
        return self.range[item]


class RollTable:
    def __init__(self, roll_string, matrix):
        self.roll_string = roll_string
        self.matrix = matrix

    def roll(self):
        r = Dice.rollString(self.roll_string)
        for k in self.matrix.keys():
            if r in k:
                v = self.matrix[k]
                if isinstance(v, RollTable):
                    return v.roll()
                else:
                    return v
