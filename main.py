from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
import sqlite3
import sys

from UI.mainUi import Ui_MainWindow
from UI.addEditCoffeeForm import Ui_Form


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.db_filename = 'data\\coffee.sqlite'
        self.data = self.load_data_from_db()
        self.initUI()
        self.update_table()

    def initUI(self):
        self.addButton.clicked.connect(self.add_element_input)
        self.editButton.clicked.connect(self.edit_element_input)
        self.deleteButton.clicked.connect(self.remove_element)

    def load_data_from_db(self):
        con = sqlite3.connect(self.db_filename)
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
        return result

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

    def add_element_input(self):
        self.stateLabel.setText('')
        self.add_item_window = EditWindow(self)
        self.add_item_window.show()

    def edit_element_input(self):
        row_index = self.tableWidget.currentRow()
        if row_index != -1:
            self.stateLabel.setText('')
            row = list(self.data[row_index])
            self.edit_item_window = EditWindow(self,
                                          index=row_index,
                                          row=tuple(row))
            self.edit_item_window.show()
        else:
            self.stateLabel.setText('Выберите запись!')

    def remove_element(self):
        row_index = self.tableWidget.currentRow()
        if row_index != -1:
            self.stateLabel.setText('')
            item_id = self.data[row_index][0]
            del self.data[row_index]
            con = sqlite3.connect(self.db_filename)
            cur = con.cursor()
            cur.execute(f'''DELETE FROM coffee
                            WHERE id = ?''', (item_id,))
            con.commit()
            con.close()
            self.update_table()
        else:
            self.stateLabel.setText('Выберите запись!')

    def add_or_edit_item(self, sort, roast_degree, coffee_type,
                         taste_description, price, packing_volume, index):
        if index is None:
            # Добавление записи
            row_id = max([row[0] for row in self.data]) + 1
            self.data.append((row_id, sort, roast_degree, coffee_type, taste_description, price, packing_volume))
            self.update_table()
            coffee_type_id = 1 if coffee_type == 'Молотый' else 2
            con = sqlite3.connect(self.db_filename)
            cur = con.cursor()
            cur.execute('''INSERT INTO coffee
                           VALUES (?, ?, ?, ?, ?, ?, ?)''', (row_id, sort, roast_degree, coffee_type_id,
                                                             taste_description, price, packing_volume))
            con.commit()
            con.close()
        else:
            # Редактирование записи
            row_id = self.data[index][0]
            self.data[index] = (row_id, sort, roast_degree, coffee_type, taste_description, price, packing_volume)
            self.update_table()
            coffee_type_id = 1 if coffee_type == 'Молотый' else 2
            con = sqlite3.connect(self.db_filename)
            cur = con.cursor()
            cur.execute('''UPDATE coffee
                           SET id = ?, sort = ?, roast_degree = ?, type = ?,
                           taste_description = ?, price = ?, packing_volume = ?
                           WHERE id = ?''', (row_id, sort, roast_degree, coffee_type_id,
                                             taste_description, price, packing_volume, row_id))
            con.commit()
            con.close()


class EditWindow(QWidget, Ui_Form):
    def __init__(self, main_window_class, index=None, row=None):
        super().__init__()
        self.setupUi(self)
        self.main_window_class = main_window_class
        self.row_index = index
        self.row = row
        self.initUI()
        if row is not None:
            self.coffee_type = row[3]
        else:
            self.coffee_type = 'ground'

    def initUI(self):
        self.acceptButton.clicked.connect(self.accept)
        self.typeComboBox.activated.connect(self.change_type)
        if self.row:
            self.sortEdit.setText(str(self.row[1]))
            self.roastDegreeSpinBox.setValue(self.row[2])
            self.typeComboBox.setCurrentText(self.row[3])
            self.tasteDescriptionEdit.setText(str(self.row[4]))
            self.priceSpinBox.setValue(self.row[5])
            self.packingVolumeSpinBox.setValue(self.row[6])
            self.acceptButton.setText('Отредактировать')
            self.setWindowTitle('Редактирование')

    def change_type(self, coffee_type):
        self.coffee_type = 'ground' if coffee_type == 0 else 'beans'

    def accept(self):
        try:
            sort = self.sortEdit.text()
            roast_degree = self.roastDegreeSpinBox.value()
            taste_description = self.tasteDescriptionEdit.toPlainText()
            price = self.priceSpinBox.value()
            packaging_volume = self.packingVolumeSpinBox.value()
            self.main_window_class.add_or_edit_item(sort, roast_degree, self.coffee_type,
                                                    taste_description, price, packaging_volume, self.row_index)
            self.close()
        except Exception:
            self.stateLabel.setText('Неверно заполнена форма')


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())