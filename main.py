
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtGui import QIcon, QFileSystemModel
from ui import Ui_MainWindow
from functions import speedmult, ispathvalid, config

setting = config()

class speedmult_ui(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        global setting
        QMainWindow.__init__(self,parent)
        self.setupUi(self)
        self.directory = ""
        self.hkannopath = setting.get("hkanno64path")
        self.mbox = QMessageBox(self)
        self.load_dialog = QFileDialog(None)
        self.model = QFileSystemModel()
        self.model.setNameFilters(["*.hkx"])
        self.model.setNameFilterDisables(False)
        self.load_btn.clicked.connect(lambda: self.load())
        self.execute_btn.clicked.connect(lambda:self.execute())
        self.changeDir.clicked.connect(lambda: self.changedir())

        self.setWindowIcon(QIcon('icon\\icon.ico'))
        self.setWindowTitle("Speedmult")
        self.load_btn.setText(setting.get("Load"))
        self.label.setText(setting.get("Speed"))
        self.speed_line.setText("1.5")
        self.execute_btn.setText(setting.get("Execute"))
        self.changeDir.setText(setting.get("changeDir"))

    def changedir(self):
        temp = self.hkannopath
        self.hkannopath = self.load_dialog.getExistingDirectory(None, setting.get("Select Folder"))
        if not ispathvalid(self.hkannopath):
            self.mbox.warning(self, setting.get("Warning"), setting.get("No hkanno64"))
            self.hkannopath = temp
        else:
            setting.edit("hkanno64path",self.hkannopath)

    def load(self):
        self.directory = self.load_dialog.getExistingDirectory(None, setting.get("Select Folder"))
        if self.directory != "":
            self.model.setRootPath(self.directory)
            self.treeView.setModel(self.model)
            self.treeView.setRootIndex(self.model.index(self.directory))
            self.treeView.hideColumn(1)
            self.treeView.hideColumn(2)
            self.treeView.hideColumn(3)

    def execute(self):
        if self.directory == "":
            self.mbox = QMessageBox.warning(self.mbox,setting.get("Warning"), setting.get("No rootpath"))
            return None

        if not ispathvalid(self.hkannopath):
            self.mbox.warning(self,setting.get("Warning"),setting.get("No hkanno64"))
            return None

        multiple = float(self.speed_line.text())

        update = (self.mbox.question(
            self,
            setting.get("Message"),
            setting.get("Ask Update"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
                    == QMessageBox.StandardButton.Yes)

        if update:
            delete = (self.mbox.question(
                self,
                setting.get("Message"),
                setting.get("Ask Delete"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
                    == QMessageBox.StandardButton.Yes)
        else:
            delete = False

        result = speedmult(self.directory,multiple,update,delete,self.hkannopath)
        if result:
            self.mbox.information(self, setting.get("Message"), setting.get("Notification"))
            self.treeView.setModel(None)
            self.directory = ""

        return None

    def closeEvent(self, event):
        setting.dump()
        event.accept()

def main():
    app = QApplication(sys.argv)
    UI = speedmult_ui()
    UI.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
