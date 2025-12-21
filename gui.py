import os, sys, json, webbrowser, requests
from enum import Enum, auto
from lastversion import lastversion
from PySide6.QtWidgets import QApplication, QMainWindow, QSlider, QCheckBox, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QListWidget, QAbstractItemView, QListWidgetItem, QMessageBox, QErrorMessage, QPushButton, QMenuBar, QFileDialog
from PySide6.QtCore import Qt, Slot, QStandardPaths
from pathlib import Path
import main as LOGIC

def get__file__():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        return __file__

def cleanup_old_bin():
    if os.path.exists(os.path.join(os.path.dirname(get__file__()),os.path.basename(get__file__())+".old")):
        os.remove(os.path.join(os.path.dirname(get__file__()),os.path.basename(get__file__())+".old"))

cleanup_old_bin()

VERSION_TAG = "0.4"
BINARY_EXT = {
    "win32": ".exe",
    "linux": "",
    "darwin": ".zip"
}
def get_download_url(tag:str) -> str:
    bname = "PylessDetectiveGui"+(BINARY_EXT.get(sys.platform) or "")
    if not bname: return None
    return f"https://github.com/DatBogie/PylessDetective/releases/download/v{tag}/{bname}"

MAPS = LOGIC.get_maps()

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

class UpdateResult(Enum):
    UpdateFail = -1
    NoUpdate = auto()
    UpdateSuccess = auto()

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

        # Updater
        if FOUND_SETTINGS.get("updater_enabled") != False:
            self.check_upd(True)

        menubar = QMenuBar()
        fmenu = menubar.addMenu("File")
        fmenu.addAction("Load Map Directory...",self.loadMapDir)
        fmenu.addAction("Reset Map Directory",self.resetMapDir)
        fmenu.addAction("Exit",self.close)
        emenu = menubar.addMenu("Edit")
        emenu.addAction("Clear Selected Clues",lambda: [self.clues.item(i).setCheckState(Qt.CheckState.Unchecked) for i in range(self.clues.count())])
        # emenu.addAction("Open Preferences...",self.showPrefWin)
        hmenu = menubar.addMenu("Help")
        hmenu.addAction("Check for Updates...",self.check_upd)
        hmenu.addAction("Open GitHub Repo...",lambda: webbrowser.open("https://github.com/DatBogie/PylessDetective"))
        self.setMenuBar(menubar)

        self.prefwin = QWidget()
        self.prefwin.setWindowTitle("Preferences - PylessDetective")
        self.prefwin.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.prefwin.setGeometry(self.geometry())

        self.prefwinlay = QVBoxLayout()
        self.prefwin.setLayout(self.prefwinlay)

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
        self.mapSwitcher.addItems([LOGIC.prettify_map_name(x) for x in MAPS])
        self.mapSwitcher.currentTextChanged.connect(lambda: self.update(UpdateType.Map))
        self.toplayout.addWidget(self.mapSwitcher)

        self.suspects = QListWidget()
        self.suspects.setToolTip("Potential suspects based on map and found/not present evidence\n#XX is the their number in the post-level lineup (out of /XX total people)")
        self.suspects.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.crlayout.addWidget(self.suspects)

        self.clues = CheckList()
        self.clues.setToolTip(f"Clue:\n{LOGIC.TAB}Left Click: Toggle mark as found/to-be-found\n{LOGIC.TAB}Right Click: Toggle mark as not present\nBackground:\n{LOGIC.TAB}Right Click: Clear selection")
        self.clues.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.clues.itemSelectionChanged.connect(self.onCheckItemSelected)
        self.clues.itemChanged.connect(self.onCheckItemChanged)
        self.cwlayout.addWidget(self.clues)

        self.decolay = QHBoxLayout()

        self.deco = QCheckBox("Frameless Window")
        self.deco.setToolTip("Toggle hiding window title/borders")
        self.deco.setCheckState(Qt.CheckState.Checked if FOUND_SETTINGS.get("window_frameless") else Qt.CheckState.Unchecked)
        self.deco.checkStateChanged.connect(self.setFrameless)
        self.decolay.addWidget(self.deco)

        close = QPushButton("Close")
        close.clicked.connect(self.close)
        self.decolay.addWidget(close)

        self.cwlayout.addLayout(self.decolay)
        
        self.savelay = QHBoxLayout()

        self.save = QCheckBox("Save Window Data")
        self.save.setToolTip("Save window size/position\nWhen closed while toggled off, saved window position will be wiped")
        self.save.setCheckState(Qt.CheckState.Checked if FOUND_SETTINGS.get("window_geometry") != False else Qt.CheckState.Unchecked)
        self.savelay.addWidget(self.save)

        self.updater = QCheckBox("Run Updater on Launch")
        self.updater.setToolTip("Check for PylessDetective updates from GitHub on launch")
        self.updater.setCheckState(Qt.CheckState.Checked if FOUND_SETTINGS.get("updater_enabled") != False else Qt.CheckState.Unchecked)
        self.savelay.addWidget(self.updater)

        self.cwlayout.addLayout(self.savelay)

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
    
    def showPrefWin(self):
        geo = self.geometry()
        width = geo.width()//2
        height = geo.height()//2
        self.prefwin.setGeometry(geo.x() + width//2,geo.y() + height//2,width,height)
        self.prefwin.show()
        self.prefwin.raise_()
    
    def check_upd(self,silent_fail:bool=False):
        print("Checking for updates...")
        result = None
        new_version = lastversion.has_update("DatBogie/PylessDetective",VERSION_TAG)
        if new_version:
            update_msg = QMessageBox(QMessageBox.Icon.Information,"Updater - PylessDetective",f"A new version of PylessDetective is available!\nCurrent: {VERSION_TAG}\nLatest: {new_version}",parent=self)
            update_msg.addButton("Update",QMessageBox.ButtonRole.AcceptRole)
            update_msg.setStandardButtons(QMessageBox.StandardButton.Ignore)
            if update_msg.exec() == 2:
                dl_url = get_download_url(new_version)
                if dl_url is None:
                    if QMessageBox.critical(self,"Updater - PylessDetective","Pre-built binaries are not available for your platform on this version.\nPlease visit the GitHub page to learn how to build them yourself!",QMessageBox.StandardButton.Open|QMessageBox.StandardButton.Abort) == QMessageBox.StandardButton.Open:
                        webbrowser.open("https://github.com/DatBogie/PylessDetective")
                else:
                    try:
                        response = requests.get(dl_url,stream=True)
                        response.raise_for_status()
                        output_path = os.path.join(os.path.dirname(get__file__()),f"PylessDetectiveGui{BINARY_EXT[sys.platform]}")
                        cleanup_old_bin()
                        os.rename(get__file__(),os.path.basename(get__file__())+".old")
                        with open(output_path,"wb") as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        if sys.platform != "darwin":
                            QMessageBox.information(self,"Updater - PylessDetective","Download complete! PylessDetective will now close.",QMessageBox.StandardButton.Close)
                            result = UpdateResult.UpdateSuccess
                        else:
                            QMessageBox.information(self,"Updater - PylessDetective",f"Download complete! Please extract the downloaded zip ({output_path}) and replace the existing application.",QMessageBox.StandardButton.Ok)
                            result = UpdateResult.UpdateSuccess
                    except Exception as e:
                        QErrorMessage(self).showMessage(str(e))
        else:
            result = UpdateResult.NoUpdate
        
        if result == UpdateResult.UpdateSuccess and sys.platform != "darwin":
            self.close()
        
        if not silent_fail and result == UpdateResult.NoUpdate:
            QMessageBox.information(self,"Updater - PylessDetective","You are already running the latest version of PylessDetective!",QMessageBox.StandardButton.Ok)
    
    def closeEvent(self, event):
        print("Saving settings...")
        FOUND_SETTINGS["window_opacity"] = self.opacity.value()
        FOUND_SETTINGS["window_frameless"] = self.windowFlags() & Qt.WindowType.FramelessWindowHint
        FOUND_SETTINGS["updater_enabled"] = self.updater.checkState() == Qt.CheckState.Checked
        if self.save.checkState() == Qt.CheckState.Checked:
            FOUND_SETTINGS["window_geometry"] = self.geometry().getRect()
        else:
            print("Resetting geometry...")
            FOUND_SETTINGS.pop("window_geometry")
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
            x[LOGIC.uglify_map_name(item.text())] = item.checkState() == Qt.CheckState.Checked
        return x

    def update(self, mode:UpdateType=UpdateType.Clue):
        map = self.getMAP()

        if mode < 1:
            LOGIC.gen_map_data(map)
            self.clues.clear()
            for x in LOGIC.get_clues(map):
                x = LOGIC.prettify_map_name(x)
                item = CheckListItem(x)
                self.clues.addItem(item)
        self.suspects.clear()
        map_data = LOGIC.get_map_data(map)
        self.suspects.addItems([f"(#{list(map_data.keys()).index(x)+1}/{len(list(map_data.keys()))}) {x}" for x in LOGIC.get_suspects(map,self.getClues())])
    
    def loadMapDir(self,dir=False):
        global MAPS
        LOGIC.MAP_DIR = dir if dir != False else Path(QFileDialog.getExistingDirectory(self,"Choose Map Directory",QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadLocation)))
        LOGIC.gen_map_dict()
        MAPS = LOGIC.get_maps()
        self.mapSwitcher.clear()
        self.mapSwitcher.addItems([LOGIC.prettify_map_name(x) for x in MAPS])
        self.mapSwitcher.setCurrentIndex(0)
        self.update(UpdateType.Map)

    def resetMapDir(self):
        self.loadMapDir(None)

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