#!/usr/bin/python3
import os
import sys
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget,
                             QDesktopWidget,
                             QHBoxLayout, QVBoxLayout,
                             QLabel, QComboBox, QPushButton)
from PyQt5.QtGui import QIcon


THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(THIS_DIR, 'pylib'))
from Common import get_pixmap_from_base64
from resources import icon_png


class ChooseSystem(QMainWindow):

    def __init__(self):
        super().__init__()

        self.system_path = None

        # self.setWindowIcon( QIcon( 'images/icon.png' ) )
        self.setWindowIcon(QIcon(get_pixmap_from_base64(icon_png)))
        self.setWindowTitle('Choose system')

        text = QLabel('Choose system')
        systems = self.get_systems()
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
        layout.addWidget(text, alignment=QtCore.Qt.AlignCenter)
        layout.addWidget(choose, alignment=QtCore.Qt.AlignCenter)
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
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

    def get_systems(self):
        systems = []
        walk = os.walk(os.path.join(THIS_DIR, 'systems'))
        for dir_tup in walk:
            # print( dir_tup )
            current_dir = dir_tup[0]
            files = dir_tup[2]
            if 'SystemSettings.py' in files:
                # print( 'Bingo' )
                ss_path = os.path.join(current_dir, 'SystemSettings.py')
                with open(ss_path) as ss_file:
                    for line in ss_file:
                        if 'systemName' in line:
                            # print( line )
                            d = {}
                            exec(line, d, d)
                            # print( d['systemName'] )
                            systems.append((d['systemName'], current_dir))
                            break
        return systems

    def get_system_path(self):
        return self.system_path

    def set_system_path(self, system_path):
        self.system_path = system_path

    def ok(self):
        self.close()
        system_path = self.choose.currentData()
        # self.w = MainWindow( system_path )
        #sys.path.append(os.path.join(THIS_DIR, 'pylib'))
        sys.path.append(system_path)
        import Windows
        self.w = Windows.MainWindow(system_path)

    def cancel(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    cs = ChooseSystem()
    # system_path = cs.get_system_path()
    # print( system_path )
    # if system_path is not None:
    #     sys.path.append( os.path.join( THIS_DIR, 'pylib' ) )
    #     sys.path.append( system_path )
    #     import Windows
    #     mw = Windows.MainWindow()
    sys.exit(app.exec_())
