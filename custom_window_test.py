

import maya.cmds as cmds
from maya import OpenMayaUI

try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import (QWidget)
    from shiboken6 import wrapInstance
except ModuleNotFoundError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtCore import Qt
    from PySide2.QtGui import QIcon
    from PySide2.QtWidgets import (QWidget)
    from shiboken2 import wrapInstance

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class CustomWindow(QtWidgets.QWidget):
    def __init__(self):
        super(CustomWindow, self).__init__()
        version = "001"
        ui_object_name = f"JmvsToolBox_{version}"
        ui_window_name = f"Jmvs ToolBox {version}"

        # Remove the window frame
        #self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint) # 
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setWindowTitle(ui_window_name)
        self.resize(600, 400)

        # title bar
        self.title_bar = QtWidgets.QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444;") # grey
        self.title_bar.setFixedHeight(30)
        
        # title label aka 'window title name'
        self.title_label = QtWidgets.QPushButton(ui_window_name, self.title_bar)
        self.title_label.setStyleSheet("color: white; padding-left: 10px;")
        
        # close button
        self.close_button = QtWidgets.QPushButton("X", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: #f00;") # black
        
        # self.close_button.click.connect(self.close_func)

        # layout for title bar
        title_layout = QtWidgets.QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        # add the title label
        title_layout.addWidget(self.title_label)
        title_layout.addStretch() # spacer?
        title_layout.addWidget(self.close_button)

        # main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.title_bar)
        
        # central widget
        central_widget = QtWidgets.QWidget(self)
        central_widget.setStyleSheet("background-color: #09004c;") # white
        main_layout.addWidget(central_widget)
        
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.title_bar.underMouse():
            self.old_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.old_pos and event.buttons() == QtCore.Qt.LeftButton:
            delta = event.pos() - self.old_pos
            self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        self.old_pos = None


def custom_window_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    print("WHAAAAAAAAT")
    ui = CustomWindow()
    ui.setParent(main_window, QtCore.Qt.Window)
    ui.show()
    app.exec()
    return ui
            
            
