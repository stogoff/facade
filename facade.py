#!/usr/bin/python
# Программа расчета себестоимости фасадных конструкций
# Date: 26/11/2014
# Author: rost@stogoff.ru
#
# Requirements:
# Python3   https://www.python.org/downloads/
# PyQt5     http://www.riverbankcomputing.com/software/pyqt/download5
# xlrd      https://pypi.python.org/pypi/xlrd


from PyQt5 import  QtGui as QG, QtCore as QC, QtWidgets as QW, uic, Qt
from cbr import get_euro_rate
from parser import *
from profile import *
from operator import xor


import sys

price = {}


if __name__ == '__main__':
    form_class = uic.loadUiType("main.ui")[0]
    class MyWindowClass(QW.QMainWindow, form_class):
        def __init__(self, parent=None):
            QW.QMainWindow.__init__(self, parent)
            self.setupUi(self)
            self.edit_width.textChanged.connect(self.calc_area)
            self.edit_height.textChanged.connect(self.calc_area)
            self.edit_pillars.textChanged.connect(self.calc_fasteners)
            self.edit_height.textChanged.connect(self.height_changed)

            self.floors = 0
            try:
                rate, curr_code = get_euro_rate()
                self.label_rate.setText("1 %s =" % curr_code)
                self.edit_rate.setText("%7.4f" % rate)
            except:
                rate = 999999
                self.label_rate.setText("1 EUR =")
                self.edit_rate.setText("???")

            for i,f in ((1,'pillars'), (2, 'headers')):
                price[i] = parse_f("../прайс_октябрь_2014.xls", i)
                ### Combobox:
                cb = eval("self.comboBox_%d" % i)
                cb.addItem("Выберите:")
                for name in sorted(price[i]):
                    cb.addItem(name)
                cb.activated[str].connect(eval("self.calc_%s" % f))
                cb.setEnabled(False)
                ### filling the table:
                #tab = eval("self.tableWidget%d" % i)
                #header = tab.horizontalHeader()
                #header.setStretchLastSection(True)
                ##header.setResizeMode(QHeaderView.Stretch)
                #for i in range(len(data)):
                    #tab.insertRow(i)
                    #for j in range(len(data[i])):
                        #value = data[i][j]
                        #if j == 1: #если это цена, пересчитываем в евро + ндс
                            #value = "%5.2f" % (1.18 * value / rate)
                        #elif j > 1:
                            #value = "%5.2f" % value
                        #tab.setItem(i, j, QW.QTableWidgetItem(value))
                        #if j<5:
                            #item = tab.item(i, j)
                            #item.setBackground(QG.QColor(QC.Qt.lightGray))
                            #item.setFlags(xor(tab.item(i, j).flags(),
                                            #QC.Qt.ItemIsEditable))
                    #tab.setItem(i, j+1, QW.QTableWidgetItem("0"))
                #tab.itemChanged.connect(eval("self.calc_%s" % f))


        def calc_area(self):
            try:
                w = float(self.edit_width.text())
            except:
                w = 0
                pass
            try:
                h = float(self.edit_height.text())
            except:
                h = 0

            area = w * h
            self.label_area.setText("%5.3f" % area)
            perimeter = (w + h) * 2
            self.label_per.setText("%5.3f" % perimeter)


        def calc_fasteners(self):
            try:
                p = int(self.edit_pillars.text())
            except:
                p = 0
                #self.edit_pillars.
            f = p * 2
            self.edit_fasteners.setText("%d" % f)


        def get_number_field (self, field):
            try:
                res = float(field.text())
                field.setStyleSheet("QLineEdit{background: white;}")
            except:
                #print("Unexpected error:", sys.exc_info()[0])
                res = 0
                #field.setText("0")
                field.setStyleSheet("QLineEdit{background: red;}")
                field.setToolTip("Введите число!")
                #QW.QMessageBox.question(self, 'Message',
                #        "Введите число в поле %s" % field.objectName(),
                #        QW.QMessageBox.Ok)
            return res


        def get_number_cell (self, cell):
            try:
                res = float(cell.text())
            except:
                res = 0
            return res


        def height_changed(self):
            h = self.get_number_field (self.edit_height)
            if h:
                self.comboBox_1.setEnabled(True)
            else:
                self.comboBox_1.setEnabled(False)
            if h > 3:
                self.floors, ok = MyDialog1Class.getRes()
            if not self.floors: #нет перекрытий
                pass

            #tab = self.tableWidget1
            #for i in range(tab.rowCount()):
                ##print(i)
                ##посчитаем длину профиля:
                #st_len = self.get_number_cell(tab.item(i, 2))
                #p_length = calc_profile_length(h, st_len)
                #tab.setItem(i, 3, QW.QTableWidgetItem("%5.2f"%p_length))
                #item = tab.item(i,3)
                #item.setBackground(QG.QColor(QC.Qt.lightGray))
                #item.setFlags(xor(tab.item(i, 3).flags(),
                                            #QC.Qt.ItemIsEditable))



        def calc_pillars(self, item):
            print(item)
            #s = 0 # сумма
            if item not in price[1].keys():
                return
            np = self.get_number_field(self.edit_pillars) # число стоек
            print ("np=%d"%np)
            if not np:
                QW.QMessageBox.question(self, 'Message',
                        "Укажите число стоек", QW.QMessageBox.Ok)
                self.comboBox_1.setCurrentIndex(0)
                return
            h = self.get_number_field (self.edit_height)
            if not self.floors:  #нет перекрытий
                st_len = price[1][item][1]

            #tab = self.tableWidget1
            #for i in range(tab.rowCount()):
                #p_length = self.get_number_cell(tab.item(i, 3))
                #num_pillars = self.get_number_cell(tab.item(i, 4))
                #p += num_pillars
                #price = self.get_number_cell(tab.item(i, 1))
                #s +=  num_pillars * p_length * price

            ##print ("p=%d"%p)
            #if p > np:
                #pil.setStyleSheet("QLineEdit{background: red;}")
                #pil.setToolTip("Число стоек в таблице превышает общее")
                #color = "red"
            #elif p < np:
                #pil.setStyleSheet("QLineEdit{background: yellow;}")
                #pil.setToolTip("Число стоек в таблице меньше общего")
                #color= "orange"
            #else:
                #pil.setStyleSheet("QLineEdit{background: white;}")
                #pil.setToolTip("")
                #color = "green"
            #self.label_sum1.setText("<b><font color='%s'>%5.2f</font></b>" %
                                    #(color,s))

        def calc_headers(self):
            s = 0
            for i in range(self.tableWidget2.rowCount()):
                price  = float(self.tableWidget2.item(i, 1).text())
                num_headers = int(self.tableWidget2.item(i, 2).text())
                s +=  num_headers * 6 * price
            self.label_sum2.setText("%5.2f" % s)

    dialog1_class = uic.loadUiType("dialog1.ui")[0]
    class MyDialog1Class(QW.QDialog, dialog1_class):
        def __init__(self, parent=None):
            QW.QDialog.__init__(self, parent)
            self.setupUi(self)
            self.ww = self.spinBox.value()

        @staticmethod
        def getRes(parent = None):
            dialog = MyDialog1Class(parent)
            result = dialog.exec_()
            res = dialog.spinBox.value()
            return (res, result == QW.QDialog.Accepted)


    app = QW.QApplication(sys.argv)
    myWindow = MyWindowClass(None)
    myWindow.show()
    app.exec_()
