import inspect
import os
import PyQt5.QtCore as QtCore
from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import (QMainWindow, QAction, QWidget, QTabWidget,
                             QDesktopWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
                             QScrollArea, QWizard, QWizardPage, QPushButton, QCheckBox,
                             QLabel, QListWidget, QListWidgetItem, QLineEdit, QTextEdit,
                             QFrame, QComboBox, QSpinBox, QRadioButton, QButtonGroup,
                             QFileDialog, QColorDialog
                             )
from PyQt5.QtGui import QIcon, QPixmap, QFont, QTextDocument, QDrag
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
import DbDefs
import SystemSettings
import Db
import DbLayout
import DbQuery
import Manage
import ManageDefs
import resources
from Common import (find_image, get_pixmap_from_base64, get_default_pixmap, callback_factory,
                    fill_listbox, add_item_to_listbox, remove_item_from_listbox, get_pixmap_from_hex_color)
from Dialogs import YesNoDialog, EntryDialog, DualListDialog, ProgressDialog


SYSTEM_PATH = None


class CenterableWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

    def center(self):
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())


class MainWindow(CenterableWindow):

    def __init__(self, system_path):
        super().__init__()

        self.system_path = system_path
        global SYSTEM_PATH
        SYSTEM_PATH = system_path
        SystemSettings.init_system_path(system_path)

        # exitAct = QAction( QIcon( 'exit.png' ), 'Exit', self )
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)

        DbQuery.initDB(os.path.join(system_path, 'db'))
        database_menu = menubar.addMenu('&Database')
        for db in DbLayout.db_order:
            db_action = QAction(db, self)
            db_action.setStatusTip('Open the {} Database'.format(db))
            db_action.triggered.connect(callback_factory(self.open_db_window, db))
            database_menu.addAction(db_action)
        database_menu.addSeparator()
        reset_db_action = QAction('Reset Database', self)
        reset_db_action.setStatusTip('Reset the database to the default')
        reset_db_action.triggered.connect(self.reset_db)
        database_menu.addAction(reset_db_action)

        manage_menu = menubar.addMenu('&Manage')
        for manage in self.get_manages():
            manage_action = QAction(manage.__class__.__name__, self)
            manage_action.setStatusTip('Open the {} Manage Window'.format( manage.__class__.__name__))
            manage_action.triggered.connect(callback_factory(self.open_manage_window, manage))
            manage_menu.addAction(manage_action)

        self.statusBar()

        # system_parent = os.path.abspath( os.path.join( system_path, os.pardir ) )
        # base_bath = os.path.abspath( os.path.join( system_parent, os.pardir ) )
        # icon_path = os.path.join( base_bath, 'images/icon.png' )
        # print( icon_path )
        # self.setWindowIcon( QIcon( icon_path ) )
        self.setWindowIcon(QIcon(get_pixmap_from_base64(resources.icon_png)))
        self.setWindowTitle(SystemSettings.systemName)
        self.show()
        self.center()

    def open_db_window(self, table_name):
        DbWindow(table_name, self)

    def reset_db(self):
        dialog = YesNoDialog('Reset Database', 'Are you sure you want to reset the database?', self)
        accepted = dialog.exec_()
        # print( accepted )
        if accepted:
            table_count = 0
            for k, v in Db.__dict__.items():
                if inspect.isclass(v) and issubclass(v, DbDefs.Table) and v.table_name != DbDefs.Table.table_name:
                    table_count += 1
            value_range = 0, table_count
            progress = ProgressDialog('Resetting Database',
                                      'Please wait while the database is being reset.',
                                      value_range, DbQuery.resetDB, self)
            progress.forceShow()
            progress.setWindowModality(QtCore.Qt.WindowModal)
            progress.setValue(0)
            progress.start_generator()
            # reset_db is a generator so it must be iterated over
            # for _ in DbQuery.resetDB():
            #     pass

    def get_manages(self):
        manages = []

        manage_dict = Manage.__dict__
        for k,v in manage_dict.items():
            if inspect.isclass(v) and issubclass(v, ManageDefs.Manage) and v is not ManageDefs.Manage:
                # print( v )
                manage = v()
                manages.append(manage)
        return manages

    def open_manage_window(self, manage):
        ManageWindow(manage, self)


class DbWindow(CenterableWindow):

    def __init__(self, table_name, parent):
        super().__init__(parent)
        
        self.widget_registry = {}
        self.table_name = table_name
        self.parent = parent

        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.table = DbQuery.getTable(table_name)
        cols = DbQuery.getCols(table_name)

        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        self.portrait = portrait = QLabel(self)
        # pixmap = QPixmap( find_image( parent.system_path, table_name, '$dummy$' ) )
        pixmap = get_pixmap_from_base64(resources.noImage_jpg)
        portrait.setPixmap(pixmap)
        left_layout.addWidget(portrait, alignment=QtCore.Qt.AlignCenter)

        self.listbox = listbox = QListWidget(self)
        listbox.currentRowChanged.connect(self.fill_fields)
        display_col = DbQuery.getDisplayCol(table_name)
        for row in self.table:
            item = QListWidgetItem()
            item.setText(row[display_col])
            item.setData(QtCore.Qt.UserRole, row)
            listbox.addItem(item)
        left_layout.addWidget(listbox)
        layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        scrollable = QScrollArea(self)
        scroll_widget = QWidget(scrollable)
        scroll_layout = QVBoxLayout(scrollable)
        scroll_widget.setLayout(scroll_layout)
        for col in cols:
            widget = None
            widget_layout = QHBoxLayout()
            widget_layout.addWidget(QLabel(col[0]))
            if 'TEXT' in col[1]:
                widget = QTextEdit(self)
            else:
                widget = QLineEdit(self)
            self.widget_registry[col[0]] = widget
            widget_layout.addWidget(widget)
            scroll_layout.addLayout(widget_layout)
        scrollable.setWidget(scroll_widget)
        right_layout.addWidget(scrollable)
        layout.addLayout(right_layout)
        
        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setLayout(layout)

        self.setWindowTitle(table_name)
        self.show()
        self.center()

    def fill_fields(self, row_index):
        item = self.listbox.item(row_index)
        row = item.data(QtCore.Qt.UserRole)
        for field_name, widget in self.widget_registry.items():
            widget.setText(str(row[field_name]))

        unique_col = DbQuery.parse_schema(DbQuery.getSchema(self.table_name), 'UNIQUE')
        base64_image_col = DbQuery.getBase64Col(self.table_name)
        if base64_image_col is None:
            image_path = find_image(self.parent.system_path, self.table_name, row[unique_col])
            pixmap = QPixmap(image_path)
            if pixmap.height() > 200 or pixmap.width() > 200:
                pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
        else:
            base64 = row[base64_image_col]
            pixmap = get_pixmap_from_base64(base64)

        self.portrait.setPixmap(pixmap)


class WidgetRegistry(dict):
    text_widgets = ['lineedit', 'textedit', 'textlabel']

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def register_widget(self, widget, gui_wizard_page=None):
        field_name = widget.get_field_name()
        hide_field = False
        if field_name.endswith('_'):
            hide_field = True
            field_name = field_name[:-1]
        widget_type = widget.get_widget_type()
        widget_width = widget.get_width()
        is_enabled = widget.is_edit_enabled()
        stretch = widget.get_stretch()
        widget_data = widget.get_data()
        widget_style = widget.get_style()
        widget_tool_tip = widget.get_tool_tip()

        widget_layout = None
        qt_widget = None

        disabled_stylesheet = ':disabled { color: black }'
        if widget_type.lower() == 'checkbox':
            widget_layout = QHBoxLayout()
            if widget_data:
                text = widget_data
            elif hide_field:
                text = ''
            else:
                text = field_name
            qt_widget = QCheckBox(text)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            widget_layout.addWidget(qt_widget)
            if gui_wizard_page:
                qt_widget.clicked.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'textedit':
            widget_layout = QVBoxLayout()
            qt_widget = QTextEdit()
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            if not hide_field:
                widget_layout.addWidget(QLabel(field_name))
            widget_layout.addWidget(qt_widget)
            if gui_wizard_page:
                qt_widget.textChanged.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'lineedit':
            widget_layout = QHBoxLayout()
            if widget_data:
                prefill = widget_data
            else:
                prefill = ''
            qt_widget = QLineEdit(prefill)
            if widget_width:
                qt_widget.setFixedWidth(widget_width)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            if not hide_field:
                if not stretch:
                    widget_layout.addWidget(QLabel(field_name), 1, QtCore.Qt.AlignRight)
                else:
                    widget_layout.addWidget(QLabel(field_name))
            if not stretch:
                widget_layout.addWidget(qt_widget, 1, QtCore.Qt.AlignLeft)
            else:
                widget_layout.addWidget(qt_widget)
            if gui_wizard_page:
                qt_widget.textChanged.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'spinbox':
            widget_layout = QHBoxLayout()
            qt_widget = QSpinBox()
            if widget_data:
                qt_widget.setValue(widget_data)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            qt_widget.setRange(-1000000000, 1000000000)
            if not hide_field:
                widget_layout.addWidget(QLabel(field_name))
            widget_layout.addWidget(qt_widget)
            if gui_wizard_page:
                qt_widget.valueChanged.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'pushbutton':
            widget_layout = QHBoxLayout()
            if widget_data:
                button_text = widget_data
            elif not hide_field:
                button_text = field_name
            else:
                button_text = ''
            qt_widget = QPushButton(button_text)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            widget_layout.addWidget(qt_widget)

        elif widget_type.lower() == 'radiobutton':
            direction = widget.get_direction()
            if direction.lower() == 'vertical':
                widget_layout = QVBoxLayout()
            else:
                widget_layout = QHBoxLayout()
            qt_widget = QButtonGroup()
            for i, radio in enumerate(widget_data):
                if hide_field:
                    radio_button = QRadioButton('')
                else:
                    radio_button = QRadioButton(radio)
                radio_button.setEnabled(is_enabled)
                radio_button.setStyleSheet(disabled_stylesheet)
                if not callable(widget_tool_tip):
                    radio_button.setToolTip(widget_tool_tip)
                qt_widget.addButton(radio_button)
                qt_widget.setId(radio_button, i)
                if i == 0:
                    radio_button.setChecked(True)
                widget_layout.addWidget(radio_button)
            if gui_wizard_page:
                    qt_widget.buttonToggled.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'combobox':
            widget_layout = QHBoxLayout()
            qt_widget = QComboBox()
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            if widget_data:
                for item in widget_data:
                    qt_widget.addItem(item)
            if not hide_field:
                widget_layout.addWidget(QLabel(field_name))
            widget_layout.addWidget(qt_widget)
            if gui_wizard_page:
                qt_widget.currentIndexChanged.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'listbox':
            widget_layout = QVBoxLayout()
            qt_widget = QListWidget()
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            if widget_data:
                fill_listbox(qt_widget, widget_data)
            if not hide_field:
                widget_layout.addWidget(QLabel(field_name))
            widget_layout.addWidget(qt_widget)
            qt_widget.gui_wizard_page = gui_wizard_page
            if gui_wizard_page:
                qt_widget.currentRowChanged.connect(lambda: gui_wizard_page.completeChanged.emit())

        elif widget_type.lower() == 'duallist':
            widget_layout = QVBoxLayout()
            tabbed_avail_lists = QTabWidget(self.parent)
            tabbed_avail_lists.tabBar().setStyleSheet('font: bold 8pt;')

            qt_widget = chosen_list = QListWidget(self.parent)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if gui_wizard_page:
                model = chosen_list.model()
                model.rowsInserted.connect(lambda: gui_wizard_page.completeChanged.emit())
                model.rowsRemoved.connect(lambda: gui_wizard_page.completeChanged.emit())
                chosen_list.itemChanged.connect(lambda: gui_wizard_page.completeChanged.emit())

            tabbed_chosen_list = QTabWidget(self.parent)
            tabbed_chosen_list.addTab(chosen_list, '')
            tabbed_chosen_list.tabBar().hide()

            fill_avail = widget_data.get('fill_avail')
            slots = widget_data.get('slots')
            slots_name = widget_data.get('slots_name')
            category_field = widget_data.get('category_field')
            category_callback = widget_data.get('category_callback')
            tool_tip = widget_data.get('tool_tip')
            add = widget_data.get('add')
            remove = widget_data.get('remove')

            #if fill_avail:
            #    avail_items = fill_avail( owned_items, fields )
            #else:
            #    avail_items = []

            #if category_field:
            #    category_hash = {}
            #    for avail_item in avail_items:
            #        if type( avail_item ).__name__ == 'dict':
            #            avail_item_dict = avail_item
            #        elif type( avail_item ).__name__ == 'tuple':
            #            avail_item_dict = avail_item[1]
            #        else:
            #            continue
            #        category = avail_item_dict[category_field]
            #        if category not in list( category_hash.keys() ):
            #            category_hash[category] = QListWidget( self )
            #            tabbed_avail_lists.addTab( category_hash[category], category )
            #        add_item_to_listbox( category_hash[category], avail_item, tool_tip, fields )
            #else:
            #    avail_list = QListWidget( self )
            #    tabbed_avail_lists.addTab( avail_list, 'Avail' )
            #    tabbed_avail_lists.tabBar().hide()
            #    fill_listbox( avail_list, avail_items, tool_tip, fields )
            #    if avail_list.count() > 0:
            #        avail_list.setCurrentRow( 0 )

            # fill_listbox( chosen_list, owned_items, tool_tip, fields )
            qt_widget.tabbed_avail_lists = tabbed_avail_lists
            qt_widget.chosen_list = chosen_list
            qt_widget.fill_avail = fill_avail
            qt_widget.category_field = category_field
            qt_widget.category_callback = category_callback
            qt_widget.gui_wizard_page = gui_wizard_page
            qt_widget.slots = slots
            qt_widget.slots_name = slots_name
            qt_widget.tool_tip = tool_tip
            qt_widget.category_hash = category_hash = {}

            if chosen_list.count() > 0:
                chosen_list.setCurrentRow(0)

            add_button = QPushButton('Add', self.parent)
            remove_button = QPushButton('Remove', self.parent)

            # slots_label = QLabel( '<b>{}:</b>{}'.format( slots_name, slots_return ), self.parent )
            slots_label = QLabel('', self.parent)
            qt_widget.slots_label = slots_label
            widget_layout.addWidget(slots_label, 1, QtCore.Qt.AlignCenter)

            list_layout = QHBoxLayout()
            button_layout = QVBoxLayout()
            button_layout.addWidget(add_button)
            button_layout.addWidget(remove_button)

            list_layout.addWidget(tabbed_avail_lists)
            list_layout.addLayout(button_layout)
            list_layout.addWidget(tabbed_chosen_list)
            widget_layout.addLayout(list_layout)

            def add_pressed():
                current_list = tabbed_avail_lists.currentWidget()
                if current_list.currentRow() == -1:
                    return
                current_item = current_list.currentItem()
                current_data = current_item.data(QtCore.Qt.UserRole)
                if gui_wizard_page:
                    add_return = add(current_data, self.get_fields(),
                                     gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                else:
                    add_return = add(current_data, self.get_fields())
                valid = add_return.get('valid')
                slots_new_value = add_return.get('slots_new_value')
                remove = add_return.get('remove')
                new_display = add_return.get('new_display')
                if valid is not True:
                    return
                # if type( slots_new_value ).__name__ == 'str':
                if slots:
                    slots_label.setText('<b>{}: </b>{}'.format(slots_name, str(slots_new_value)))
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
                add_item_to_listbox(chosen_list, add_item, tool_tip, self.get_fields(), current_list, wizard=gui_wizard_page, index=replace_index)

            def remove_pressed():
                if chosen_list.currentRow() == -1:
                    return
                current_item = chosen_list.currentItem()
                current_data = current_item.data(QtCore.Qt.UserRole)
                if gui_wizard_page:
                    remove_return = remove(current_data, self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                else:
                    remove_return = remove(current_data, self.get_fields())
                valid = remove_return.get('valid')
                slots_new_value = remove_return.get('slots_new_value')
                replace = remove_return.get('replace')
                new_display = remove_return.get('new_display')
                if valid is not True:
                    return
                if slots:
                    slots_label.setText('<b>{}: </b>{}'.format(slots_name, str(slots_new_value)))
                # print(slots_new_value)
                if type(new_display).__name__ == 'tuple':
                    replace_index = new_display[0]
                    new_display = new_display[1]
                    remove_item = (new_display, current_data)
                    add_item_to_listbox(chosen_list, remove_item, tool_tip, self.get_fields(), wizard=gui_wizard_page, index=replace_index)
                    return
                # elif type(new_display).__name__ == 'str':
                #     remove_item = (new_display, current_data)
                if replace is True:
                    try:
                        original_list = current_item.original_list
                    except AttributeError:
                        if category_field:
                            # print( category_hash )
                            category = str(current_data[category_field])
                            if qt_widget.category_callback:
                                if gui_wizard_page:
                                    category = category_callback(category, self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                                else:
                                    category = category_callback(category, self.get_fields())
                            if category in qt_widget.category_hash.keys():
                                original_list = qt_widget.category_hash[category]
                            else:
                                qt_widget.category_hash[category] = original_list = QListWidget(self.parent)
                                tabbed_avail_lists.addTab(qt_widget.category_hash[category], category)
                        else:
                            # original_list = tabbed_avail_lists.getCurrentWidget()
                            original_list = tabbed_avail_lists.currentWidget()
                    replace_item = current_data
                    if new_display and type(new_display).__name__ == 'str':
                        replace_item = new_display, current_data
                    add_item_to_listbox(original_list, replace_item, tool_tip, self.get_fields(), original_list, wizard=gui_wizard_page)
                chosen_list.takeItem(chosen_list.currentRow())

            add_button.pressed.connect(add_pressed)
            remove_button.pressed.connect(remove_pressed)

        elif widget_type.lower() == 'textlabel':
            widget_layout = QHBoxLayout()
            qt_widget = QLabel(widget_data)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setStyleSheet(disabled_stylesheet)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            widget_layout.addWidget(qt_widget)

        elif widget_type.lower() == 'image':
            widget_layout = QVBoxLayout()
            widget_base64 = widget_data or ''
            if widget_base64.startswith('#') and len(widget_base64) < 8:
                pixmap = get_pixmap_from_hex_color(widget_base64)
            elif widget_base64.find('|') > -1:
                hex_color, width, height = widget_base64.split('|')
                pixmap = get_pixmap_from_hex_color(hex_color, int(width), int(height))
            else:
                pixmap = get_pixmap_from_base64(widget_base64)
            qt_widget = QLabel()
            qt_widget.setPixmap(pixmap)
            qt_widget.base64 = widget_data or ''
            qt_widget.setEnabled(is_enabled)
            if widget_style:
                widget_style = widget_style
                qt_widget.setStyleSheet(widget_style)
            if not callable(widget_tool_tip):
                qt_widget.setToolTip(widget_tool_tip)
            widget_layout.addWidget(qt_widget)

        elif widget_type.lower() == 'dragimage':
            image_data = widget_data[0]
            fieldname = widget_data[1]
            initial_state = widget_data[2]
            widget_layout = QVBoxLayout()
            qt_widget = DragImage(image_data, fieldname, self.get_fields, self.fill_fields)
            qt_widget.setEnabled(is_enabled)
            qt_widget.setAcceptDrops(initial_state)
            widget_layout.addWidget(qt_widget)

        elif widget_type.lower() == 'resourceselect':
            widget_layout = QVBoxLayout()
            if not hide_field:
                widget_layout.addWidget(QLabel(field_name))
            list_layout = QHBoxLayout()
            qt_widget = QListWidget()
            qt_widget.setEnabled(is_enabled)
            list_layout.addWidget(qt_widget)
            res_view = QLabel()
            res_view.setObjectName('res_view')
            res_view.setPixmap(get_default_pixmap(SYSTEM_PATH))
            list_layout.addWidget(res_view)
            widget_layout.addLayout(list_layout)

            def select_resource():
                current_item = qt_widget.currentItem()
                resource = current_item.data(QtCore.Qt.UserRole)
                res_type, res_data = widget.data(resource, self.get_fields())
                if res_type.lower() == 'image':
                    res_view.setPixmap(get_pixmap_from_base64(res_data))
                elif res_type.lower() == 'font':
                    res_view.setPixmap(get_pixmap_from_base64(resources.font_png))
                elif res_type.lower() == 'audio':
                    res_view.setPixmap(get_pixmap_from_base64(resources.volume_png))
                    player = QMediaPlayer(qt_widget)
                    self.byte_array = QtCore.QByteArray.fromBase64(res_data.encode())
                    self.buffer = QtCore.QBuffer()
                    self.buffer.setData(self.byte_array)
                    self.buffer.open(QtCore.QIODevice.ReadOnly)
                    player.setMedia(QMediaContent(), self.buffer)
                    player.play()
            qt_widget.clicked.connect(select_resource)
            qt_widget.itemSelectionChanged.connect(select_resource)

        elif widget_type.lower() == 'hr':
            widget_layout = QHBoxLayout()
            hr = QFrame(self.parent)
            # hr.setGeometry( QtCore.QRect( 0, 0, 20, 1 ) )
            hr.setFrameShape(QFrame.HLine)
            hr.setFrameShadow(QFrame.Sunken)
            hr.setLineWidth(2)
            hr.setMidLineWidth(1)
            widget_layout.addWidget(hr)

        elif widget_type.lower() == 'empty':
            widget_layout = QHBoxLayout()
            empty = QLabel('')
            widget_layout.addWidget(empty)

        else:
            print('This widget contains an unknown type: {}'.format(widget_type))

        if qt_widget is not None:
            widget.qt_widget = qt_widget
            self[field_name] = widget
        return widget_layout

    # def fill_listbox(self, listbox, fill):
    #     listbox.clear()
    #     for item in fill:
    #         if type(item).__name__ == 'str':
    #             listbox.addItem(item)
    #         elif type(item).__name__ == 'dict':
    #             table_name = item['TableName']
    #             display_col = DbQuery.getDisplayCol(table_name)
    #             display = item[display_col]
    #             list_item = QListWidgetItem()
    #             list_item.setText(display)
    #             list_item.setData(QtCore.Qt.UserRole, item)
    #             listbox.addItem(list_item)
    #         elif type(item).__name__ == 'tuple':
    #             display = item[0]
    #             item_dict = item[1]
    #             list_item = QListWidgetItem()
    #             list_item.setText(display)
    #             list_item.setData(QtCore.Qt.UserRole, item_dict)
    #             listbox.addItem(list_item)

    # def remove_item_from_listbox(self, listbox):
    #     remove_index = listbox.currentRow()
    #     if remove_index == -1:
    #         return
    #     listbox.takeItem(remove_index)

    def get_fields(self):
        fields = {}
        for k, v in list(self.items()):
            widget_type = v.get_widget_type()
            widget = v.qt_widget
            if widget_type.lower() in self.text_widgets:
                if widget_type.lower() == 'textedit':
                    fields[k] = widget.toPlainText()
                else:
                    fields[k] = widget.text()
            elif widget_type.lower() == 'checkbox':
                fields[k] = widget.isChecked()
            elif widget_type.lower() == 'spinbox':
                fields[k] = widget.value()
            elif widget_type.lower() == 'radiobutton':
                fields[k] = widget.checkedId()
            elif widget_type.lower() == 'combobox':
                fields[k] = widget.currentText()
            elif widget_type.lower() == 'listbox' or widget_type.lower() == 'duallist':
                item_list = []
                for i in range(widget.count()):
                    item = widget.item(i)
                    item_list.append(item.data(QtCore.Qt.UserRole))
                fields[k] = item_list
                current_item = widget.currentItem()
                data = None
                if current_item:
                    data = current_item.data(QtCore.Qt.UserRole)
                    if data is None:
                        data = current_item.text()
                fields['{} Current'.format(k)] = data
            elif widget_type.lower() == 'image':
                fields[k] = widget.base64
            elif widget_type.lower() == 'resourceselect':
                item_list = []
                for i in range(widget.count()):
                    item = widget.item(i)
                    item_list.append(item.data(QtCore.Qt.UserRole))
                fields[k] = item_list
        return fields

    def fill_fields(self, fields):
        for k, v in fields.items():
            widget_type = self[k].get_widget_type()
            widget = self[k].qt_widget
            if widget_type.lower() in self.text_widgets:
                widget.setText(str(v))
            elif widget_type.lower() == 'checkbox':
                widget.setChecked(v)
            elif widget_type.lower() == 'spinbox':
                widget.setValue(v)
            elif widget_type.lower() == 'radiobutton':
                for i, radio_button in enumerate(widget.button()):
                    radio_button.setText(v[i])
            elif widget_type.lower() == 'combobox':
                if type(v).__name__ == 'str':
                    new_index = widget.findText(v)
                    widget.setCurrentIndex(new_index)
                else:
                    widget.clear()
                    widget.addItems(v)
            elif widget_type.lower() == 'listbox':
                tool_tip = self[k].get_tool_tip()
                if not callable(tool_tip):
                    tool_tip = None
                if isinstance(v, list):
                    fill_listbox(widget, v, tool_tip=tool_tip, wizard=widget.gui_wizard_page)
                elif isinstance(v, tuple) and len(v) == 0:
                    remove_item_from_listbox(widget)
                else:
                    add_item_to_listbox(widget, v, tool_tip=tool_tip, wizard=widget.gui_wizard_page)
            elif widget_type.lower() == 'image':
                widget.base64 = v or ''
                if widget.base64.startswith('#') and len(widget.base64) < 8:
                    pixmap = get_pixmap_from_hex_color(widget.base64)
                elif widget.base64.find('|') > -1:
                    hex_color, width, height = widget.base64.split('|')
                    pixmap = get_pixmap_from_hex_color(hex_color, int(width), int(height))
                else:
                    pixmap = get_pixmap_from_base64(widget.base64)
                widget.setPixmap(pixmap)
            elif widget_type.lower() == 'resourceselect':
                if isinstance(v, list):
                    fill_listbox(widget, v)
                elif isinstance(v, tuple) and len(v) == 0:
                    remove_item_from_listbox(widget)
                else:
                    add_item_to_listbox(widget, v)
                res_view = widget.parent().findChild(QLabel, 'res_view')
                res_view.setPixmap(get_default_pixmap(SYSTEM_PATH))
            elif widget_type.lower() == 'duallist':
                gui_wizard_page = widget.gui_wizard_page
                slots = widget.slots
                slots_name = widget.slots_name
                slots_label = widget.slots_label
                tool_tip = widget.tool_tip
                tabbed_avail_lists = widget.tabbed_avail_lists
                chosen_list = widget.chosen_list
                fill_avail = widget.fill_avail
                category_field = widget.category_field
                category_callback = widget.category_callback
                category_hash = widget.category_hash = {}
                owned_items = v

                if slots:
                    if gui_wizard_page:
                        slots_return = slots(self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                    else:
                        slots_return = slots(self.get_fields())
                    slots_label.setText('<b>{}: </b>{}'.format(slots_name, slots_return))
                if fill_avail:
                    if gui_wizard_page:
                        avail_items = fill_avail(owned_items, self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                    else:
                        avail_items = fill_avail(owned_items, self.get_fields())
                else:
                    avail_items = []

                tabbed_avail_lists.clear()
                if category_field:
                    # category_hash = {}
                    for avail_item in avail_items:
                        if type(avail_item).__name__ == 'dict':
                            avail_item_dict = avail_item
                        elif type(avail_item).__name__ == 'tuple':
                            avail_item_dict = avail_item[1]
                        else:
                            continue
                        category = str(avail_item_dict[category_field])
                        if category_callback:
                            if gui_wizard_page:
                                category = category_callback(category, self.get_fields(), gui_wizard_page.wizard_pages,
                                                             gui_wizard_page.external_data)
                            else:
                                category = category_callback(category, self.get_fields())
                        if category not in list(category_hash.keys()):
                            category_hash[category] = QListWidget(self.parent)
                            tabbed_avail_lists.addTab(category_hash[category], category)
                        add_item_to_listbox(category_hash[category], avail_item, tool_tip, fields,
                                            wizard=gui_wizard_page)
                else:
                    avail_list = QListWidget(self.parent)
                    tabbed_avail_lists.addTab(avail_list, 'Avail')
                    tabbed_avail_lists.tabBar().hide()
                    fill_listbox(avail_list, avail_items, tool_tip, self.get_fields(), wizard=gui_wizard_page)
                    if avail_list.count() > 0:
                        avail_list.setCurrentRow(0)

                fill_listbox(chosen_list, owned_items, tool_tip, fields, wizard=gui_wizard_page)

    def process_action(self, action, gui_wizard_page=None):
        fields = self.get_fields()
        action_type = action.get_action_type()
        callback = action.get_callback()
        data = action.get_data()
        widget1 = action.get_widget1()
        widget1_field_name = widget1.get_field_name()
        widget2 = action.get_widget2()
        widget2_field_name = ''
        widget2_widget_type = ''
        if widget2 is not None:
            widget2_field_name = widget2.get_field_name()
            if widget2_field_name.endswith('_'):
                widget2_field_name = widget2_field_name[:-1]
            widget2_widget_type = widget2.get_widget_type()

        if action_type.lower() == 'fillfields':
            if callback is not None:
                if gui_wizard_page:
                    callback_return = callback(fields, gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                else:
                    callback_return = callback(fields)
                self.fill_fields(callback_return)

        elif action_type.lower() == 'savepdf' or action_type.lower() == 'printpreview':
            if callback is not None:
                if gui_wizard_page:
                    callback_return = callback(fields, gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                else:
                    callback_return = callback(fields)
                if type(callback_return).__name__ != 'tuple' or len(callback_return) == 0:
                    return
                default_filename = callback_return[0]
                pdf_markup = callback_return[1]
                # print( pdf_markup )
                font = QFont('Times New Roman', 10, QFont.Normal)
                document = QTextDocument()
                document.setDefaultFont(font)
                document.setHtml(pdf_markup)
                printer = QPrinter(QPrinter.PrinterResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setPaperSize(QPrinter.A4)
                printer.setOutputFileName(default_filename)
                printer.setPageMargins(15, 15, 15, 15, QPrinter.Point)
                printer.setColorMode(QPrinter.Color)
                document.setPageSize(QtCore.QSizeF(printer.pageRect().size()))  # This disables printing the page number
                if action_type.lower() == 'savepdf':
                    # print( 'savepdf' )
                    filename, _ = QFileDialog.getSaveFileName(self.parent, 'Save', default_filename,
                                                              'PDF Files (*.pdf)')
                    if filename is None:
                        return
                    printer.setOutputFileName(filename)
                    document.print(printer)
                else:
                    preview_dialog = QPrintPreviewDialog(printer)
                    preview_dialog.paintRequested.connect(lambda prntr: document.print(prntr))
                    preview_dialog.exec_()

        elif action_type.lower() == 'entrydialog':
            # print( 'entrydialog' )
            value = [None]
            if widget1.get_widget_type().lower() == 'menuaction':
                title = widget1_field_name.replace('&', '')
            elif widget1.get_data():
                title = widget1.get_data()
            else:
                title = widget1_field_name
            # title = widget1_field_name
            # if title.startswith('&'):
            #     title = title[1:]
            if widget2_field_name in self.keys():
                parent = self[widget2_field_name].qt_widget.parent()
            elif len(self.keys()) > 0:
                parent = self[list(self.keys())[0]].qt_widget.parent()
            else:
                parent = None

            data_return = None
            if callable(data):
                data_return = data(fields)
            elif data:
                data_return = data

            if widget2_widget_type.lower() == 'lineedit':
                dialog = EntryDialog(title, EntryDialog.LINE_EDIT, value, parent, prefill_text=data_return)
            elif widget2_widget_type.lower() == 'textedit':
                dialog = EntryDialog(title, EntryDialog.TEXT_EDIT, value, parent, prefill_text=data_return)
            elif widget2_widget_type.lower() == 'spinbox':
                dialog = EntryDialog(title, EntryDialog.SPIN_BOX, value, parent)
            elif widget2_widget_type.lower() == 'image':
                image_widget = self[widget2_field_name].qt_widget
                image_data = image_widget.base64
                dialog = EntryDialog(title, EntryDialog.IMAGE, value, parent, image_data)
            accepted = dialog.exec_()
            if accepted and callback:
                callback_return = callback(value[0], fields)
                self.fill_fields(callback_return)

        elif action_type.lower() == 'listdialog':
            if widget1.get_widget_type().lower() == 'menuaction':
                title = widget1_field_name.replace('&', '')
            else:
                title = widget1_field_name
            # if title.startswith('&'):
            #     title = title[1:]
            parent = self[widget2_field_name].qt_widget.parent()
            listbox = self[widget2_field_name].qt_widget
            owned_items = []
            for i in range(listbox.count()):
                item_data = listbox.item(i).data(QtCore.Qt.UserRole)
                owned_items.append(item_data)
            dialog = DualListDialog(title, owned_items, action.get_data(), fields, parent)
            accepted = dialog.exec_()
            if accepted and callback:
                callback_return = callback(dialog.get_item_list(), fields)
                self.fill_fields(callback_return)

        elif action_type.lower() == 'filedialog':
            file_type = 'Image Files (*.jpg *.jpeg *.gif *.png)'
            if data is not None:
                file_type = data
            filename, _ = QFileDialog.getOpenFileName(self.parent, 'Open', os.path.expanduser('~'), file_type)
            if filename and callback:
                if gui_wizard_page:
                    callback_return = callback(filename, self.get_fields(), gui_wizard_page.wizard_pages,
                                               gui_wizard_page.external_data)
                else:
                    callback_return = callback(filename, self.get_fields())
                self.fill_fields(callback_return)

        elif action_type.lower() == 'colordialog':
            title = 'Choose Color'
            if data is not None:
                title = data
            color = QColorDialog.getColor(parent=self.parent, title=title, options=QColorDialog.DontUseNativeDialog)
            if color.isValid():
                hex_color = color.name()
                if gui_wizard_page:
                    callback_return = callback(hex_color, self.get_fields(), gui_wizard_page.wizard_pages,
                                               gui_wizard_page.external_data)
                else:
                    callback_return = callback(hex_color, self.get_fields())
                self.fill_fields(callback_return)

        elif action_type.lower() == 'wizard':
            wizard = data()
            # parent = self[ widget2_field_name ].qt_widget.parent()
            gui_wizard = GuiWizard(wizard, self.get_fields(), self.parent)
            if gui_wizard.exec_():
                accept_return = gui_wizard.get_accept_return()
                if callback:
                    callback_return = callback(accept_return, self.get_fields())
                    if callback_return:
                        self.fill_fields(callback_return)

        elif action_type.lower() == 'dragenable':
            if gui_wizard_page:
                drag_callback_return = callback(self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
            else:
                drag_callback_return = callback(self.get_fields())
            for k, v in drag_callback_return.items():
                drag_image = self[k].qt_widget
                drag_image.setAcceptDrops(v)

        elif action_type.lower() == 'window':
            if callback:
                if gui_wizard_page:
                    manage = callback(self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
                else:
                    manage = callback(self.get_fields())
                if manage:
                    ManageWindow(manage, self.parent)

        elif action_type.lower() == 'playsound':
            if gui_wizard_page:
                playsound_callback_return = callback(self.get_fields(), gui_wizard_page.wizard_pages, gui_wizard_page.external_data)
            else:
                playsound_callback_return = callback(self.get_fields())
            player = QMediaPlayer(widget1.qt_widget)
            self.byte_array = QtCore.QByteArray.fromBase64(playsound_callback_return.encode())
            self.buffer = QtCore.QBuffer()
            self.buffer.setData(self.byte_array)
            self.buffer.open(QtCore.QIODevice.ReadOnly)
            player.setMedia(QMediaContent(), self.buffer)
            player.play()

        elif action_type.lower() == 'callbackonly':
            if callback:
                callback(self.get_fields())

    def fill_menu_bar(self, menu_bar, menu_list, parent):
        for menu in menu_list:
            menu_name = menu.get_menu_name()
            qt_menu = menu_bar.addMenu(menu_name)
            menu_action_list = menu.get_action_list()
            for menu_action in menu_action_list:
                menu_widget1 = menu_action.get_widget1()
                menu_widget1_field_name = menu_widget1.get_field_name()
                qt_menu_action = QAction(menu_widget1_field_name, parent)
                qt_menu.addAction(qt_menu_action)
                qt_menu_action.triggered.connect(callback_factory(self.process_action, menu_action))


class ManageWindow(CenterableWindow):

    onshow = pyqtSignal()

    def __init__(self, manage, parent):
        super().__init__(parent)

        self.manage = manage
        self.parent = parent
        self.widget_registry = WidgetRegistry(self)
        self.close_callback = lambda x: x

        class_name = type(manage).__name__
        if manage.get_title():
            title = manage.get_title()
        else:
            title = class_name

        layout = QGridLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        widget_matrix = manage.get_widget_matrix()
        for i, row in enumerate(widget_matrix):
            for j, widget in enumerate(row):
                widget_layout = self.widget_registry.register_widget(widget)
                if widget.get_align() is None:
                    align = QtCore.Qt.AlignLeft
                elif widget.get_align().lower() == 'center':
                    align = QtCore.Qt.AlignCenter
                elif widget.get_align().lower() == 'left':
                    align = QtCore.Qt.AlignLeft
                elif widget.get_align().lower() == 'right':
                    align = QtCore.Qt.AlignRight
                elif widget.get_align().lower() == 'top':
                    align = QtCore.Qt.AlignTop
                elif widget.get_align().lower() == 'bottom':
                    align = QtCore.Qt.AlignBottom
                else:
                    align = QtCore.Qt.AlignLeft

                if widget_layout is not None:
                    layout.addLayout(widget_layout, i, j, widget.get_row_span(), widget.get_col_span(), align)

        actions = manage.get_action_list()
        for action in actions:
            action_type = action.get_action_type()
            widget1 = action.get_widget1()
            widget1_type = widget1.get_widget_type()
            widget1_field_name = widget1.get_field_name()
            if widget1_field_name.endswith('_'):
                widget1_field_name = widget1_field_name[:-1]
            callback = action.get_callback()
            data = action.get_data()
            if action_type.lower() == 'onshow':
                self.onshow.connect(callback_factory(self.on_show, callback))
            elif action_type.lower() == 'onclose':
                self.close_callback = callback
            elif action_type.lower() == 'timer':
                self.timer = QTimer()
                self.timer.timeout.connect(callback_factory(self.on_timeout, callback))
                self.timer.start(data)
            elif widget1_type.lower() == 'pushbutton' or widget1_type.lower() == 'checkbox':
                qt_widget = self.widget_registry[widget1_field_name].qt_widget
                qt_widget.clicked.connect(callback_factory(self.widget_registry.process_action, action))
            elif widget1_type.lower() == 'listbox':
                qt_widget = self.widget_registry[widget1_field_name].qt_widget
                qt_widget.currentRowChanged.connect(callback_factory(self.widget_registry.process_action, action))

        menu_list = manage.get_menu_list()
        self.widget_registry.fill_menu_bar(self.menuBar(), menu_list, self)

        if manage.get_modality() == 'block':
            self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle(title)
        self.onshow.emit()
        self.show()
        self.center()

    def on_show(self, callback):
        # print( 'on_show' )
        fields = self.widget_registry.get_fields()
        # print( fields )
        callback_return = callback(fields)
        self.widget_registry.fill_fields(callback_return)

    def on_timeout(self, callback):
        fields = self.widget_registry.get_fields()
        callback_return = callback(fields)
        self.widget_registry.fill_fields(callback_return)

    def closeEvent(self, event):
        self.close_callback(self.widget_registry.get_fields())
        try:
            self.timer.stop()
        except AttributeError:
            pass
        super().closeEvent(event)


class GuiWizard(QWizard):

    def __init__(self, wizard, external_data, parent):
        super().__init__(parent)
        self.widget_registry = widget_registry = WidgetRegistry(self)
        wizard_pages = wizard.get_wizard_pages()
        title = wizard.get_title()
        self.external_data = external_data
        self.accept_method = wizard.accept
        self.accept_return = None
        self.setWizardStyle(QWizard.ClassicStyle)
        self.setWindowTitle(title)
        self.pages = pages = {}
        for page in wizard_pages:
            page_title = page.get_title()
            pages[page_title] = page
            gui_wizard_page = GuiWizardPage(page, pages, external_data, widget_registry, self)
            self.setPage(gui_wizard_page.get_page_id(), gui_wizard_page)

    def get_widget_registry(self):
        return self.widget_registry        

    def get_accept_return(self):
        return self.accept_return

    def accept(self):
        self.accept_return = self.accept_method(self.widget_registry.get_fields(), self.pages, self.external_data)
        # QDialog.accept()
        super().accept()


class GuiWizardPage(QWizardPage):

    def __init__(self, wizard_page, wizard_pages, external_data, widget_registry, parent):
        super().__init__(parent)
        # print( widget_registry )
        self.wizard_page = wizard_page
        self.wizard_pages = wizard_pages
        self.external_data = external_data
        self.widget_registry = widget_registry
        self.page_id = page_id = wizard_page.get_page_id()
        title = wizard_page.get_title()
        subtitle = wizard_page.get_subtitle()
        widget_matrix = wizard_page.get_widget_matrix()
        self.setTitle(title)
        self.setSubTitle(subtitle)
        grid_layout = QGridLayout()
        for i, row in enumerate(widget_matrix):
            for j, widget in enumerate(row):
                widget_layout = widget_registry.register_widget(widget, gui_wizard_page=self)
                if widget.get_align() is None:
                    align = QtCore.Qt.AlignLeft
                elif widget.get_align().lower() == 'center':
                    align = QtCore.Qt.AlignCenter
                elif widget.get_align().lower() == 'left':
                    align = QtCore.Qt.AlignLeft
                elif widget.get_align().lower() == 'right':
                    align = QtCore.Qt.AlignRight
                elif widget.get_align().lower() == 'top':
                    align = QtCore.Qt.AlignTop
                elif widget.get_align().lower() == 'bottom':
                    align = QtCore.Qt.AlignBottom
                else:
                    align = QtCore.Qt.AlignLeft
                if widget_layout is not None:
                    grid_layout.addLayout(widget_layout, i, j, widget.get_row_span(), widget.get_col_span(), align)
        self.setLayout(grid_layout)

        actions = wizard_page.get_action_list()
        for action in actions:
            action_type = action.get_action_type()
            widget1 = action.get_widget1()
            widget1_type = widget1.get_widget_type()
            widget1_field_name = widget1.get_field_name()
            if widget1_field_name.endswith('_'):
                widget1_field_name = widget1_field_name[:-1]
            callback = action.get_callback()
            # data = action.get_data()
            if action_type.lower() == 'onshow':
                self.onshow.connect(callback_factory(self.on_show, callback))
            elif widget1_type.lower() == 'pushbutton':
                qt_widget = self.widget_registry[widget1_field_name].qt_widget
                qt_widget.clicked.connect(callback_factory(self.widget_registry.process_action, action, self))
            elif widget1_type.lower() == 'listbox':
                qt_widget = self.widget_registry[widget1_field_name].qt_widget
                qt_widget.currentRowChanged.connect(callback_factory(self.widget_registry.process_action, action, self))
            elif widget1_type.lower() == 'combobox':
                qt_widget = self.widget_registry[widget1_field_name].qt_widget
                qt_widget.currentIndexChanged.connect(callback_factory(self.widget_registry.process_action, action, self))

    def get_page_id(self):
        return self.page_id

    def initializePage(self):
        # print( self.widget_registry )
        initialize_page_return = self.wizard_page.initialize_page(self.widget_registry.get_fields(),
                                                                  self.wizard_pages, self.external_data)
        self.setSubTitle(self.wizard_page.get_subtitle())
        if initialize_page_return:
            self.widget_registry.fill_fields(initialize_page_return)

    def isComplete(self):
        is_complete_return = self.wizard_page.is_complete(self.widget_registry.get_fields(),
                                                          self.wizard_pages, self.external_data)
        return is_complete_return

    def nextId(self):
        next_page_id = self.wizard_page.get_next_page_id(self.widget_registry.get_fields(),
                                                         self.wizard_pages, self.external_data)
        if next_page_id == -2:
            found_current_page = False
            for page_id in self.wizard().pageIds():
                if page_id == self.page_id:
                    found_current_page = True
                elif found_current_page:
                    return page_id
            return -1
        return next_page_id


class DragImage(QLabel):

    def __init__(self, image_data, fieldname, get_fields_callback, set_fields_callback):
        super().__init__()
        self.fieldname = fieldname
        self.get_fields_callback = get_fields_callback
        self.set_fields_callback = set_fields_callback
        self.image_data = image_data
        self.setPixmap(get_pixmap_from_base64(image_data))

    def get_fieldname(self):
        return self.fieldname

    def dropEvent(self, drop_event):
        # print('drop_event')
        source_fieldname = drop_event.mimeData().property('fieldname')
        source_value = drop_event.mimeData().property('value')
        dest_fieldname = self.fieldname
        dest_value = self.get_fields_callback()[self.fieldname]
        self.set_fields_callback({dest_fieldname: source_value, source_fieldname: dest_value})

    def dragMoveEvent(self, drag_event):
        # print('move_event')
        drag_event.accept()

    def dragEnterEvent(self, drag_event):
        # print('drag_event')
        drag_event.acceptProposedAction()

    def mousePressEvent(self, mouse_event):
        # print('mouse_event')
        if mouse_event.button() != QtCore.Qt.LeftButton:
            return
        drag = QDrag(self)
        mime_data = QtCore.QMimeData()
        field_value = self.get_fields_callback()[self.fieldname]
        if len(field_value) == 0 or field_value.isspace():
            return
        mime_data.setProperty('fieldname', self.fieldname)
        mime_data.setProperty('value', field_value)
        drag.setMimeData(mime_data)
        drag.setPixmap(get_pixmap_from_base64(self.image_data))
        drag.exec_()
