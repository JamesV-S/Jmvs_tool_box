

'''
this is my geo_db.py: `import maya.cmds as cmds
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

import sys
import importlib
import os.path

from databases.geo_databases import database_schema_001
importlib.reload(database_schema_001)

# For the time being, use this file to simply call the 'modular_char_ui.py'
maya_main_wndwPtr = OpenMayaUI.MQtUtil.mainWindow()
main_window = wrapInstance(int(maya_main_wndwPtr), QWidget)

def delete_existing_ui(ui_name):
    if cmds.window(ui_name, exists=True):
        cmds.deleteUI(ui_name, window=True)

class GeoDatabase(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeoDatabase, self).__init__(parent)
        version = "001"
        ui_object_name = f"JmvsGeoDatabase_{version}"
        ui_window_name = f"Jmvs_geo_database_{version}"
        delete_existing_ui(ui_object_name)
        self.setObjectName(ui_object_name)

        # Set flags & dimensions
        self.setParent(main_window)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(ui_window_name)
        self.resize(400, 550)
        
        print("GeoDatabase class defined")

        self.UI()

    def UI(self):
        # Build the ui buttons and layout here
        
        #self.geoDB_label = QtWidgets.QLabel("GeoDB_WIP")
        #main_layout.addWidget(self.geoDB_label)
        main_Vlayout = QtWidgets.QVBoxLayout(self)

        # 4 layouts within the main_Vlayout

        # 2: Tab layout Database selector
        ''' I want this to work a lot like the "layer" tab in ngskinTools! with this tab on the left  '''
        example_database_list = ["DB_geo_mech", "DB_geo_arm", "DB_geo_other"]
        # create layer ui for this and put into this layout:
        db_selector_layout = QtWidgets.QVBoxLayout()
        # this button will create a new database. 
        cr_database_btn = QtWidgets.QPushButton("+")

        # 1: Tab layout Database visualisation
        ''' I want this to work a lot like the "influences" tab in ngskinTools! with this tab on the right next to the `db_selector_layout` '''
        db_list_layout = QtWidgets.QVBoxLayout()
        
        # 3: tab layout for buttons that add joints or geometry to the database

        
        self.setLayout(main_Vlayout)
    
    def create_database(self):
        database_schema_001.CreateDatabase(mdl_name="geo_mech")

def geoDB_main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    ui = GeoDatabase()
    ui.show()
    app.exec()
    return ui` that and I'm working on to create a desired ui. 
There's about 4 layout's within the main ui that I want to create, and 
I thingk two should be a window add to the main one becuase they're more 
complex than just buttons. the first two I want is layout (2) to work 
like ngskintools' layers tab and to be on the top left of the main window. 
Then (1) tab to work like the 'influences' tab in ngskin tools, as this 
window will be to visualise data from my database 'class CreateDatabase():
    def __init__(self, name):
        db_name = f'DB_{name}.db'
        try:
            with sqlite3.connect(db_name) as conn:
                # interasct with datsabase
                self.add_table(conn)
                print(f"name `{name}` has connected to database {db_name}")
                
        except sqlite3.Error as e:
            print(e)
    ''' 
    """CREATE TABLE IF NOT EXISTS db_name (
        db_row_id INTEGER PRIMARY KEY,
        name text NOT NULL
    );""", 
    '''
    def add_table(self, conn): 
        sql_cr_table_state = [
        """CREATE TABLE IF NOT EXISTS uuid_data (
            db_row_id INTEGER PRIMARY KEY,
            joint_name text NOT NULL,
            joint_uuid text NOT Null,
            geo_name text NOT NULL,
            geo_uuid text NOT Null
        );"""
        ]
        cursor = conn.cursor()
        for state in sql_cr_table_state:
            cursor.execute(state)
        conn.commit()
' and since the data 
has the uuid of the joints and geo, be able to select from the window, 
positioned top right of the main window. Just below the window (2) I 
want to have a layout for buttons called Bind and Unbind.Then below all these 
tabs/window will be buttons for updating the database. The main thing I 
need help with is the windows that mimic the ones from ngskintools. 
Let me know if you understand the ui I'm referring to as the only 
documentation i can find for the layers of ngskintools is this: 'https://github.com/BigMacchia/ngSkinTools/blob/master/ngSkinTools/python/ngSkinTools/ui/tabLayers.py'

`from maya import cmds, mel,OpenMaya as om
from ngSkinTools.ui.basetab import BaseTab
from ngSkinTools.utils import Utils
from ngSkinTools.ui.uiWrappers import FloatField, FormLayout, CheckBoxField,\
    TextLabel, TextEdit
from ngSkinTools.ui.constants import Constants
from ngSkinTools.ui.layerDataModel import LayerDataModel
from ngSkinTools.ui.events import LayerEvents, MayaEvents

class LayerProperties:
    def __init__(self,data):
        self.data = data
        class Controls:
            pass
        self.controls = Controls()
        
    
    def layerNameChanged(self):
        currLayer = self.data.getCurrentLayer()
        if currLayer is not None:
            name = self.controls.layerName.getValue().strip()
            cmds.ngSkinLayer(e=True,id=currLayer,name=name)
            LayerEvents.nameChanged.emit()


    def layerOpacityChanged(self):
        currLayer = self.data.getCurrentLayer()
        if currLayer is not None:
            value = self.controls.layerOpacity.getValue()
            cmds.ngSkinLayer(e=True,id=currLayer,opacity=value)
            cmds.floatSlider(self.controls.sliderIntensity,e=True,value=value)
        
    def layerOpacitySliderChanged(self,*args):
        self.controls.layerOpacity.setValue(cmds.floatSlider(self.controls.sliderIntensity,q=True,value=True))
        self.layerOpacityChanged()
        
    def createUI(self,tab,parent):
        LayerEvents.currentLayerChanged.addHandler(self.update,parent)
        LayerEvents.layerListUpdated.addHandler(self.update,parent)
        MayaEvents.undoRedoExecuted.addHandler(self.update,parent)

        group = tab.createUIGroup(parent, "Layer Properties")
        cmds.setParent(group)
        
        cmds.rowLayout(parent=group,nc=2,adjustableColumn=2,columnWidth2=[Constants.MARGIN_COLUMN2,50], columnAttach2=["both","left"],columnAlign2=["right","left"])
        TextLabel('Layer name:')
        self.controls.layerName = TextEdit()
        self.controls.layerName.changeCommand.addHandler(self.layerNameChanged)

        cmds.rowLayout(parent=group,adjustableColumn=3,nc=3,columnWidth3=[Constants.MARGIN_COLUMN2,50,100], columnAttach3=["both","left","both"],columnAlign3=["right","left","center"])
        TextLabel('Opacity:')
        self.controls.layerOpacity = FloatField(None, minValue=0.0, maxValue=1.0, step=0.1, defaultValue=1.0, annotation="overall intensity of this layer")
        self.controls.layerOpacity.changeCommand.addHandler(self.layerOpacityChanged)
        self.controls.sliderIntensity = cmds.floatSlider(min=0, max=1, step=0.05, value=1.0,cc=self.layerOpacitySliderChanged,dc=self.layerOpacitySliderChanged,annotation='Drag slider to change layer opacity' )
        
    def update(self):
        if not self.data.layerDataAvailable:
            return
        
        currLayer = self.data.getCurrentLayer()
        if currLayer is not None and currLayer>0:
            # looks like python version of command does not supply querying with parameters
            name = mel.eval('ngSkinLayer -id %d -q -name' % currLayer)
            self.controls.layerName.setValue(name)
            opacity = mel.eval('ngSkinLayer -id %d -q -opacity' % currLayer)
            self.controls.layerOpacity.setValue(opacity)
            cmds.floatSlider(self.controls.sliderIntensity,e=True,value=opacity)
        
        
class TabLayers(BaseTab):
    # prefix for environment variables for this tab
    VAR_LAYERS_PREFIX = 'ngSkinToolsLayersTab_'
    
    def __init__(self):
        BaseTab.__init__(self)
        self.layerDataModel = LayerDataModel.getInstance()
    
    def execAddWeightsLayer(self,*args):
        self.layerDataModel.addLayer('New Layer')

    def execRemoveLayer(self,*params):
        id = self.layerDataModel.getCurrentLayer()
        if id is None:
            return
        self.layerDataModel.removeLayer(id)
        
    def createManageLayersGroup(self,parent):
        group = self.createUIGroup(parent, "Manager Layers")
        buttonForm = FormLayout(parent=group,numberOfDivisions=100,height=Constants.BUTTON_HEIGHT)
        buttons = []
        buttons.append(cmds.button(label="Add Layer",command=self.execAddWeightsLayer))
        buttons.append(cmds.button(label="Del Layer",command=self.execRemoveLayer))
        self.layoutButtonForm(buttonForm, buttons)
        
    def createLayerOrderGroup(self,parent):
        group = self.createUIGroup(parent, "Layer Ordering")
        buttonForm = FormLayout(parent=group,numberOfDivisions=100,height=Constants.BUTTON_HEIGHT)
        buttons = []
        buttons.append(cmds.button(label="Move Up",command=self.moveLayerUp))
        buttons.append(cmds.button(label="Move Down",command=self.moveLayerDown))
        self.layoutButtonForm(buttonForm, buttons)
        
    def layersAvailableHandler(self):
        cmds.layout(self.baseLayout,e=True,enable=LayerDataModel.getInstance().layerDataAvailable)
        
    def moveLayer(self,up=True):
        newIndex = cmds.ngSkinLayer(q=True,layerIndex=True)+(1 if up else -1)
        if newIndex<0:
            newIndex=0
        cmds.ngSkinLayer(layerIndex=newIndex)
        LayerEvents.layerListModified.emit()
        
    def moveLayerUp(self,*args):
        self.moveLayer(True)
        
    def moveLayerDown(self,*args):
        self.moveLayer(False)
    
    def createUI(self,parent):
        self.setTitle('Layers')
        LayerEvents.layerAvailabilityChanged.addHandler(self.layersAvailableHandler,parent)
        result = self.baseLayout = self.createScrollLayout(parent)
        layout = cmds.columnLayout(adjustableColumn=1)
        #self.createManageLayersGroup(layout)
        self.layerPropertiesUI = LayerProperties(self.layerDataModel)
        self.layerPropertiesUI.createUI(self,layout)
        #self.createLayerOrderGroup(layout)
        self.layerPropertiesUI.update()
        return result
        `
        '''