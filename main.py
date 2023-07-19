import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QListView, QComboBox, QDateTimeEdit, QVBoxLayout, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5 import uic


class Dialog(QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        uic.loadUi('dialog.ui', self)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)

        self.buttonOpenDialog.clicked.connect(self.openDialog)
        self.model = QStandardItemModel()
        self.listView.setModel(self.model)

    def openDialog(self):
        dialog = Dialog(self)
        if dialog.exec_() == QDialog.Accepted:
            combo_text = dialog.comboBox.currentText()
            datetime = dialog.dateTimeEdit.dateTime().toString()
            self.updateListView(combo_text, datetime)

    def updateListView(self, combo_text, datetime):
        item = QStandardItem(f'Combo: {combo_text}, Datetime: {datetime}')
        self.model.insertRow(0, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
