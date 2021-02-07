from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import sqlite3
import sys


TYPES = {
    1: 'ground',
    2: 'beans'
}


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.data = self.load_data_from_db()
        self.update_table()

    def load_data_from_db(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        result = cur.execute('''SELECT * FROM coffee JOIN types
                                ON coffee.type = types.id''').fetchall()
        con.close()
        result = list(result)
        for i in range(len(result)):
            result[i] = list(result[i])
            result[i][3] = result[i][-1]
            del result[i][-2:]
            result[i] = tuple(result[i])
        return tuple(result)

    def update_table(self):
        length = len(self.data)
        self.tableWidget.setRowCount(length)
        self.table_length = length
        if self.data:
            self.tableWidget.setColumnCount(len(self.data[0]))
            for i in range(len(self.data[0])):
                self.tableWidget.setColumnWidth(i, 145)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'название сорта', 'степень обжарки', 'молотый/в зернах',
                                                    'описание вкуса', 'цена', 'объем упаковки'])
        for i, elem in enumerate(self.data):
            for j, val in enumerate(elem):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled)
                self.tableWidget.setItem(i, j, item)


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())