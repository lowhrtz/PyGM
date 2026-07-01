import os
import sys
from PyQt6 import QtWebEngineWidgets
from PyQt6 import QtCore
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QHBoxLayout, QVBoxLayout,
                             QLabel, QComboBox, QPushButton)
from PyQt6.QtGui import QIcon
from pylib.Common import get_pixmap_from_base64
from pylib.resources import icon_png

THIS_DIR = os.path.dirname(os.path.realpath(__file__))

def get_systems():
    systems = []
    walk = os.walk(os.path.join(THIS_DIR, 'systems'))
    for dir_tup in walk:
        current_dir = dir_tup[0]
        files = dir_tup[2]
        if 'SystemSettings.py' in files:
            ss_path = os.path.join(current_dir, 'SystemSettings.py')
            with open(ss_path) as ss_file:
                for line in ss_file:
                    if 'systemName' in line:
                        #print(line)
                        d = {}
                        exec(line, d, d)
                        systems.append((d['systemName'], current_dir))
                        break
    return systems

class ChooseSystem(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(get_pixmap_from_base64(icon_png)))
        self.setWindowTitle('Choose system')

        text = QLabel('Choose system')
        systems = get_systems()
        self.choose = choose = QComboBox(self)
        for system in systems:
            choose.addItem(*system)

        button_layout = QHBoxLayout()
        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.ok)
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.cancel)
        button_layout.addStretch(1)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout = QVBoxLayout()
        layout.addWidget(text, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(choose, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(button_layout)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(layout)

        self.show()
        self.center()

        self.clearFocus()
        ok_button.setFocus()

    def center(self):
        qt_rectangle = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

#    def get_systems(self):
#        systems = []
#        walk = os.walk(os.path.join(THIS_DIR, 'systems'))
#        for dir_tup in walk:
#            # print( dir_tup )
#            current_dir = dir_tup[0]
#            files = dir_tup[2]
#            if 'SystemSettings.py' in files:
#                # print( 'Bingo' )
#                ss_path = os.path.join(current_dir, 'SystemSettings.py')
#                with open(ss_path) as ss_file:
#                    for line in ss_file:
#                        if 'systemName' in line:
#                            # print( line )
#                            d = {}
#                            exec(line, d, d)
#                            systems.append((d['systemName'], current_dir))
#                            break
#        return systems

    def ok(self):
        self.close()
        system_path = self.choose.currentData()
        sys.path.append(system_path)
        # This is imported here because the class
        # needs system_path to be on the python path
        from pylib import Windows
        self.w = Windows.MainWindow(system_path)

    def cancel(self):
        self.close()

def open_from_argv(argv):
    argv_system = sys.argv[1]
    systems = get_systems()
    #print(argv_system)
    #print(systems)
    system_found = False
    for s in systems:
        if s[0] == argv_system:
            system_found = True
            system_path = s[1]
            sys.path.append(system_path)
            # This is imported here because the class
            # needs system_path to be on the python path
            from pylib import Windows
            w = Windows.MainWindow(system_path)
    if not system_found:
        print(f'System {argv_system} not recognized')
        sys.exit(1)

def main():
    app = QApplication(sys.argv)
    #print(sys.argv)
    app.setApplicationDisplayName('GM')
    if len(sys.argv) > 1:
        open_from_argv(sys.argv)
    else:
        cs = ChooseSystem()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
