import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (QDialog, QFileDialog, QDialogButtonBox, QLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTextEdit, QSpinBox, QPushButton, QListWidget,
                             QFrame, QTabWidget, QProgressDialog)
from PyQt5.QtGui import QPixmap, QIcon
from Common import get_pixmap_from_base64, add_item_to_listbox, fill_listbox
import resources


class YesNoDialog(QDialog):

    def __init__(self, title, message, parent):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        message_label = QLabel(message, self)
        yes_button = QPushButton('Yes', self)
        no_button = QPushButton('No', self)
        button_frame = QDialogButtonBox(self)
        layout.addWidget(message_label)
        yes_button.setDefault(True)
        button_frame.addButton(yes_button, QDialogButtonBox.AcceptRole)
        button_frame.addButton(no_button, QDialogButtonBox.RejectRole)
        button_frame.accepted.connect(self.accept)
        button_frame.rejected.connect(self.reject)
        layout.addWidget(button_frame)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)


class PopupDialog(QDialog):

    def __init__(self, title, message, parent):
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        message_label = QLabel(message, self)
        ok_button = QPushButton('OK', self)
        button_frame = QDialogButtonBox(self)
        layout.addWidget(message_label)
        ok_button.setDefault(True)
        button_frame.addButton(ok_button, QDialogButtonBox.AcceptRole)
        button_frame.accepted.connect(self.accept)
        layout.addWidget(button_frame)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)


class EntryDialog(QDialog):

    LINE_EDIT, TEXT_EDIT, SPIN_BOX, IMAGE = range(4)

    def __init__(self, title, entry_type, value, parent, image_data=None):
        super().__init__(parent)

        self.value = value
        self.entry_type = entry_type

        self.setWindowTitle(title)

        layout = QVBoxLayout()

        if entry_type == self.LINE_EDIT:
            self.entry_widget = QLineEdit(self)
        elif entry_type == self.TEXT_EDIT:
            self.entry_widget = QTextEdit(self)
        elif entry_type == self.SPIN_BOX:
            self.entry_widget = QSpinBox(self)
            self.entry_widget.setRange(-1000000000, 1000000000)
        elif entry_type == self.IMAGE:
            self.filename = None
            image_button = QPushButton('Choose Image', self)
            image_button.clicked.connect(self.open_image_file)
            self.entry_widget = QLabel(self)
            pixmap = get_pixmap_from_base64(image_data)
            self.entry_widget.setPixmap(pixmap)
            layout.addWidget(image_button)

        layout.addWidget(self.entry_widget, 0, QtCore.Qt.AlignCenter)

        button_frame = QDialogButtonBox(self)
        ok_button = QPushButton('OK', self)
        cancel_button = QPushButton('Cancel', self)
        ok_button.setDefault(True)
        button_frame.addButton(ok_button, QDialogButtonBox.AcceptRole)
        button_frame.addButton(cancel_button, QDialogButtonBox.RejectRole)
        button_frame.accepted.connect(self.ok_pressed)
        button_frame.rejected.connect(self.cancel_pressed)

        layout.addWidget(button_frame)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

    def open_image_file(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', QtCore.QDir.homePath())
        if self.filename is not None:
            self.entry_widget.setPixmap(QPixmap(self.filename).scaledToHeight(200))

    def ok_pressed(self):
        if self.entry_type == self.LINE_EDIT:
            self.value[0] = self.entry_widget.text()
        elif self.entry_type == self.TEXT_EDIT:
            self.value[0] = self.entry_widget.toPlainText()
        elif self.entry_type == self.SPIN_BOX:
            self.value[0] = self.entry_widget.value()
        elif self.entry_type == self.IMAGE:
            self.value[0] = self.filename

        self.accept()

    def cancel_pressed(self):
        self.value[0] = None
        self.reject()


class DualListDialog(QDialog):

    def __init__(self, title, owned_items, action_data, fields, parent):
        super().__init__(parent)
        self.fields = fields
        self.setWindowTitle(title)
        layout = QVBoxLayout()
        # Dual List Stuff
        self.tabbed_avail_lists = tabbed_avail_lists = QTabWidget(parent)
        tabbed_avail_lists.tabBar().setStyleSheet('font: bold 8pt;')

        self.chosen_list = chosen_list = QListWidget(parent)

        tabbed_chosen_list = QTabWidget(parent)
        tabbed_chosen_list.addTab(self.chosen_list, '')
        tabbed_chosen_list.tabBar().hide()

        fill_avail = action_data.get('fill_avail')
        slots = action_data.get('slots')
        self.slots_name = slots_name = action_data.get('slots_name')
        self.category_field = category_field = action_data.get('category_field')
        self.category_callback = category_callback = action_data.get('category_callback')
        self.tool_tip = tool_tip = action_data.get('tool_tip')
        self.add = add = action_data.get('add')
        self.remove = remove = action_data.get('remove')

        if fill_avail:
            avail_items = fill_avail(owned_items, fields)
        else:
            avail_items = []

        if category_field:
            category_hash = {}
            for avail_item in avail_items:
                if type(avail_item).__name__ == 'dict':
                    avail_item_dict = avail_item
                elif type(avail_item).__name__ == 'tuple':
                    avail_item_dict = avail_item[1]
                else:
                    continue
                category = avail_item_dict[category_field]
                if category_callback:
                    category = category_callback(category, self.get_fields())
                if category not in list(category_hash.keys()):
                    category_hash[category] = QListWidget( self )
                    tabbed_avail_lists.addTab(category_hash[category], category)
                add_item_to_listbox(category_hash[category], avail_item, tool_tip, fields)
        else:
            avail_list = QListWidget(self)
            tabbed_avail_lists.addTab(avail_list, 'Avail')
            tabbed_avail_lists.tabBar().hide()
            fill_listbox(avail_list, avail_items, tool_tip, fields)
            if avail_list.count() > 0:
                avail_list.setCurrentRow(0)

        fill_listbox(chosen_list, owned_items, tool_tip, fields)
        if chosen_list.count() > 0:
            chosen_list.setCurrentRow(0)

        slots_return = slots(fields)

        add_button = QPushButton('Add', self)
        remove_button = QPushButton('Remove', self)

        self.slots_label = QLabel('<b>{}:</b>{}'.format(slots_name, slots_return), self)
        layout.addWidget(self.slots_label, 1, QtCore.Qt.AlignCenter)

        list_layout = QHBoxLayout()
        button_layout = QVBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)

        list_layout.addWidget(tabbed_avail_lists)
        list_layout.addLayout(button_layout)
        list_layout.addWidget(tabbed_chosen_list)
        layout.addLayout(list_layout)

        add_button.pressed.connect(self.add_pressed)
        remove_button.pressed.connect(self.remove_pressed)

        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        button_frame = QDialogButtonBox(self)
        ok_button = QPushButton('OK', self)
        cancel_button = QPushButton('Cancel', self)
        button_frame.addButton(ok_button, QDialogButtonBox.AcceptRole)
        button_frame.addButton(cancel_button, QDialogButtonBox.RejectRole)

        button_frame.accepted.connect(self.accept)
        button_frame.rejected.connect(self.reject)

        layout.addWidget(button_frame)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.setLayout(layout)

    def add_pressed(self):
        #print( 'add_pressed' )
        current_list = self.tabbed_avail_lists.currentWidget()
        if current_list.currentRow() == -1:
            return
        current_item = current_list.currentItem()
        current_data = current_item.data(QtCore.Qt.UserRole)
        add_return = self.add(current_item.data(QtCore.Qt.UserRole), self.fields)
        valid = add_return.get('valid')
        slots_new_value = add_return.get('slots_new_value')
        remove = add_return.get('remove')
        new_display = add_return.get('new_display')
        if valid is not True:
            return
        self.slots_label.setText('<b>{}:</b>{}'.format(self.slots_name, str(slots_new_value)))
        if remove is True:
            current_list.takeItem(current_list.currentRow())
        replace_index = None
        add_item = current_data
        if type(new_display).__name__ == 'tuple':
            replace_index = new_display[0]
            new_display = new_display[1]
            add_item = (new_display, current_data)
        elif type(new_display).__name__ == 'str':
            add_item = (new_display, current_data)
        add_item_to_listbox(self.chosen_list, add_item, self.tool_tip, self.fields, current_list, index=replace_index)

    def remove_pressed(self):
        # print( 'remove_pressed' )
        if self.chosen_list.currentRow() == -1:
            return
        current_item = self.chosen_list.currentItem()
        current_data = current_item.data(QtCore.Qt.UserRole)
        remove_return = self.remove(current_data, self.fields)
        valid = remove_return.get('valid')
        slots_new_value = remove_return.get('slots_new_value')
        replace = remove_return.get('replace')
        new_display = remove_return.get('new_display')
        if valid is not True:
            return
        self.slots_label.setText('<b>{}:</b>{}'.format(self.slots_name, str(slots_new_value)))
        if type(new_display).__name__ == 'tuple':
            replace_index = new_display[0]
            new_display = new_display[1]
            remove_item = (new_display, current_data)
            add_item_to_listbox(self.chosen_list, remove_item, self.tool_tip, self.get_fields(), index=replace_index)
            return
        if replace is True:
            try:
                original_list = current_item.original_list
            except AttributeError:
                if self.category_field:
                    category = str(current_data[self.category_field])
                    if self.category_callback:
                        category = self.category_callback(category, self.get_fields())
                        if category in self.category_hash.keys():
                            original_list = self.category_hash[category]
                        else:
                            self.category_hash[category] = original_list = QListWidget(self.parent)
                            self.tabbed_avail_lists.addTab(self.category_hash[category], category)
                else:
                    original_list = self.tabbed_avail_lists.getCurrentWidget()
            add_item_to_listbox(original_list, current_data, self.tool_tip, self.fields, original_list)
        self.chosen_list.takeItem(self.chosen_list.currentRow())

    def get_item_list(self):
        item_list = []
        for i in range(self.chosen_list.count()):
            item = self.chosen_list.item(i)
            item_data = item.data(QtCore.Qt.UserRole)
            item_list.append(item_data)
        return item_list


class ProgressDialog(QProgressDialog):

    def __init__(self, title, message, value_range, generator, parent):
        super().__init__(title, None, *value_range, parent)

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(get_pixmap_from_base64(resources.icon_png)))

        self.message = message
        self.generator = generator

    def start_generator(self):
        i = 0
        for yield_return in self.generator():
            i += 1
            self.setValue(i)
            self.setLabelText('{}\n{}'.format(self.message, yield_return))
