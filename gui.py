import os, sys, json
from PySide6.QtWidgets import QApplication, QMainWindow, QSlider, QCheckBox, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QListWidget, QAbstractItemView, QListWidgetItem
from PySide6.QtCore import Qt, Slot, QStandardPaths
from main import get_maps, get_clues, get_suspects, get_map_data, prettify_map_name, uglify_map_name, gen_map_data, TAB

MAPS = get_maps()

class UpdateType: Map=0; Clue=1

CONF_DIR = os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation).replace("/",os.path.sep),"PylessDetective")

FOUND_SETTINGS = {}
if not os.path.exists(CONF_DIR):
    try:
        os.mkdir(CONF_DIR)
    except Exception as e:
        print(e)
try:
    with open(os.path.join(CONF_DIR,"config.json"),"r") as f:
        FOUND_SETTINGS = json.load(f)
except Exception as e:
    print(e)

class MainWindow(QMainWindow):
    global FOUND_SETTINGS
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PylessDetective GUI")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        if FOUND_SETTINGS.get("window_frameless"):
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint,True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if FOUND_SETTINGS.get("window_geometry"):
            print(CONF_DIR)
            self.setGeometry(*FOUND_SETTINGS["window_geometry"])

        self.cwidget = QSplitter(Qt.Orientation.Horizontal)
        self.cwidget.setHandleWidth(8)
        self.setCentralWidget(self.cwidget)

        self.leftpane = QWidget()
        self.rightpane = QWidget()
        self.cwidget.addWidget(self.leftpane)
        self.cwidget.addWidget(self.rightpane)
        
        self.cwlayout = QVBoxLayout()
        self.cwlayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.leftpane.setLayout(self.cwlayout)

        self.toplayout = QHBoxLayout()
        self.toplayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.cwlayout.addLayout(self.toplayout)

        self.crlayout = QVBoxLayout()
        self.rightpane.setLayout(self.crlayout)

        self.toplayout.addWidget(QLabel("Map:"))
        self.mapSwitcher = QComboBox(self.cwidget)
        self.mapSwitcher.addItems([prettify_map_name(x) for x in MAPS])
        self.mapSwitcher.currentTextChanged.connect(lambda: self.update(UpdateType.Map))
        self.toplayout.addWidget(self.mapSwitcher)

        self.suspects = QListWidget()
        self.suspects.setToolTip("Potential suspects based on map and found/not present evidence\n#XX is the their number in the post-level lineup (out of /XX total people)")
        self.suspects.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.crlayout.addWidget(self.suspects)

        self.clues = CheckList()
        self.clues.setToolTip(f"Clue:\n{TAB}Left Click: Toggle mark as found/to-be-found\n{TAB}Right Click: Toggle mark as not present\nBackground:\n{TAB}Right Click: Clear selection")
        self.clues.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.clues.itemSelectionChanged.connect(self.onCheckItemSelected)
        self.clues.itemChanged.connect(self.onCheckItemChanged)
        self.cwlayout.addWidget(self.clues)

        self.deco = QCheckBox("Frameless Window")
        self.deco.setToolTip("Toggle hiding window title/borders")
        self.deco.setCheckState(Qt.CheckState.Unchecked)
        self.deco.checkStateChanged.connect(self.setFrameless)
        self.cwlayout.addWidget(self.deco)
        
        self.save = QCheckBox("Save Window Info")
        self.save.setToolTip("Save window position, opacity, and titlebar/border visibility\nWhen closed while toggle off, settings will be wiped")
        self.save.setCheckState(Qt.CheckState.Checked)
        self.cwlayout.addWidget(self.save)

        self.oplayout = QHBoxLayout()
        self.oplayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.cwlayout.addLayout(self.oplayout)

        self.oplayout.addWidget(QLabel("Inactive Opacity:"))

        self.opacity = QSlider()
        self.opacity.setOrientation(Qt.Orientation.Horizontal)
        self.opacity.setRange(0,100)
        self.opacity.setValue(FOUND_SETTINGS.get("window_opacity") or 70)
        self.opacity.setToolTip(f"Inactive Opacity: {self.opacity.value()}%")
        self.opacity.valueChanged.connect(self.opacityChanged)
        self.oplayout.addWidget(self.opacity)
        
        self.update(UpdateType.Map)
    
    def closeEvent(self, event):
        if self.save.checkState() == Qt.CheckState.Checked:
            print("Saving settings...")
            FOUND_SETTINGS["window_geometry"] = self.geometry().getRect()
            FOUND_SETTINGS["window_opacity"] = self.opacity.value()
            FOUND_SETTINGS["window_frameless"] = self.windowFlags() & Qt.WindowType.FramelessWindowHint
        else:
            print("Resetting settings...")
            FOUND_SETTINGS.clear()
        return super().closeEvent(event)
    
    def setFrameless(self):
        self.hide()
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint,self.deco.checkState() == Qt.CheckState.Checked)
        self.show()

    def opacityChanged(self):
        self.opacity.setToolTip(f"Inactive Opacity: {self.opacity.value()}%")

    @Slot("QWidget*", "QWidget*")
    def onFocusChanged(self, oldWidget, newWidget):
        if newWidget is None:
            self.setWindowOpacity(self.opacity.value()/100)
        elif oldWidget is None and newWidget is not None:
            self.setWindowOpacity(1)
    
    def getMAP(self):
        return MAPS[self.mapSwitcher.currentIndex()]
    
    def onCheckItemSelected(self):
        for i in range(self.clues.count()):
            item = self.clues.item(i)
            if item.checkState() == Qt.CheckState.PartiallyChecked:
                item.setSelected(False)
                continue
            item.setCheckState(Qt.CheckState.Checked if item.isSelected() else Qt.CheckState.Unchecked)
        self.update()

    def onCheckItemChanged(self):
        for i in range(self.clues.count()):
            item = self.clues.item(i)
            item.setSelected(item.checkState() == Qt.CheckState.Checked)
        self.update()

    def getClues(self):
        x = {}
        for i in range(self.clues.count()):
            item = self.clues.item(i)
            if item.checkState() == Qt.CheckState.Unchecked: continue
            x[uglify_map_name(item.text())] = item.checkState() == Qt.CheckState.Checked
        return x

    def update(self, mode:UpdateType=UpdateType.Clue):
        map = self.getMAP()

        if mode < 1:
            gen_map_data(map)
            self.clues.clear()
            for x in get_clues(map):
                x = prettify_map_name(x)
                item = CheckListItem(x)
                self.clues.addItem(item)
        self.suspects.clear()
        map_data = get_map_data(map)
        self.suspects.addItems([f"(#{list(map_data.keys()).index(x)+1}/{len(list(map_data.keys()))}) {x}" for x in get_suspects(map,self.getClues())])

class CheckList(QListWidget):
    def __init__(self):
        super().__init__()
    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            item.setSelected(False)
            if item.checkState() != Qt.CheckState.PartiallyChecked:
                item.setCheckState(Qt.CheckState.PartiallyChecked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
        else:
            for i in range(self.count()):
                item = self.item(i)
                item.setCheckState(Qt.CheckState.Unchecked)
        return super().contextMenuEvent(event)

class CheckListItem(QListWidgetItem):
    def __init__(self,text):
        super().__init__(text)
        self.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.setCheckState(Qt.CheckState.Unchecked)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    app.focusChanged.connect(win.onFocusChanged)
    win.show()
    exitCode = app.exec()
    try:
        with open(os.path.join(CONF_DIR,"config.json"),"w") as f:
            json.dump(FOUND_SETTINGS,f)
    except Exception as e:
        print(e)
    sys.exit(exitCode)