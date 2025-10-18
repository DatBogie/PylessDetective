import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QSlider, QCheckBox, QComboBox, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QListWidget, QAbstractItemView, QListWidgetItem
from PySide6.QtCore import Qt, Slot
from main import get_maps, get_clues, get_suspects, get_map_data, prettify_map_name, uglify_map_name, gen_map_data, CLUES

MAPS = get_maps()

class UpdateType: Map=0; Clue=1

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PylessDetective GUI")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
        self.suspects.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.crlayout.addWidget(self.suspects)

        self.clues = QListWidget()
        self.clues.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.clues.itemSelectionChanged.connect(self.onCheckItemSelected)
        self.clues.itemChanged.connect(self.onCheckItemChanged)
        self.cwlayout.addWidget(self.clues)

        self.deco = QCheckBox("Frameless Window")
        self.deco.setCheckState(Qt.CheckState.Unchecked)
        self.deco.checkStateChanged.connect(self.setFrameless)
        self.cwlayout.addWidget(self.deco)

        self.oplayout = QHBoxLayout()
        self.oplayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.cwlayout.addLayout(self.oplayout)

        self.oplayout.addWidget(QLabel("Inactive Opacity:"))

        self.opacity = QSlider()
        self.opacity.setOrientation(Qt.Orientation.Horizontal)
        self.opacity.setRange(0,100)
        self.opacity.setValue(70)
        self.setToolTip(f"Inactive Opacity: {self.opacity.value()}%")
        self.opacity.valueChanged.connect(self.opacityChanged)
        self.oplayout.addWidget(self.opacity)
        
        self.update(UpdateType.Map)
    
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
            item.setCheckState(Qt.CheckState.Checked if item.isSelected() else Qt.CheckState.Unchecked)
        self.update()

    def onCheckItemChanged(self):
        for i in range(self.clues.count()):
            item = self.clues.item(i)
            item.setSelected(item.checkState() == Qt.CheckState.Checked)
        self.update()

    def getClues(self):
        x = []
        for i in range(self.clues.count()):
            item = self.clues.item(i)
            if not item.isSelected(): continue
            x.append(uglify_map_name(item.text()))
        return x

    def update(self, mode:UpdateType=UpdateType.Clue):
        map = self.getMAP()

        if mode < 1:
            gen_map_data(map)
            self.clues.clear()
            for x in get_clues(map):
                x = prettify_map_name(x)
                item = QListWidgetItem(x)
                item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.clues.addItem(item)
        self.suspects.clear()
        map_data = get_map_data(map)
        self.suspects.addItems([f"(#{list(map_data.keys()).index(x)+1}/{len(list(map_data.keys()))}) {x}" for x in get_suspects(map,self.getClues())])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    app.focusChanged.connect(win.onFocusChanged)
    win.show()
    sys.exit(app.exec())