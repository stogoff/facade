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
import BinPacking 

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

            self.fl = 0
            self.fh = {}
            try:
                rate, curr_code = get_euro_rate()
                self.label_rate.setText("1 %s =" % curr_code)
                self.edit_rate.setText("%7.4f" % rate)
            except:
                rate = 999999
                self.label_rate.setText("1 EUR =")
                self.edit_rate.setText("???")

            for i,f in ((1,'pillars'), (2, 'headers')):
                price[i] = parse_f("../прайс_декабрь2014.xlsx", i)
                ### Combobox:
                cb = eval("self.comboBox_%d" % i)
                cb.addItem("Выберите:")
                for name in sorted(price[i]):
                    cb.addItem(name)
                cb.activated[str].connect(eval("self.calc_%s" % f))
                cb.setEnabled(False)


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
                res = 0
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
            self.h = self.get_number_field (self.edit_height)
            if self.h:
                self.comboBox_1.setEnabled(True)
            else:
                self.comboBox_1.setEnabled(False)
            if self.h > 3:
                self.fl, ok = MyDialog1Class.getRes(msg="Число перекрытий:")
            if not self.fl: #нет перекрытий
                pass
            else:
                for f in range(self.fl):
                    self.fh[f], ok =  \
                        MyDialog2Class.getRes(msg= \
                        "Высота %d-го перекрытия"% (f+1))
                    if self.fh[f]>1000:
                        self.fh[f] /=1000
                print(self.fl, self.fh)


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
            if not self.fl:  #нет перекрытий
                st_len = price[1][item][1]
                price_m = price[1][item][0]
                self.label_20.setText("%.2f"%price_m)
                if self.h > st_len:
                    num = int(self.h // st_len) # число целых профилей
                    print(num)
                    sum1 = np * num * price_m # стоимость целых профилей
                    self.label_21.setText("%.2f"%sum1)
                    tail = self.h % st_len # длина остатка
                    print ("tail=%d"%tail)
                    d = st_len // tail # сколько остатков получится из 1 проф
                    sum2 = np / d * price_m # стоимость остатков
                    self.label_22.setText("%.2f"%sum2)
                    
                    
                    #aList =  np * [tail]
                    #bins = BinPacking.pack(aList, st_len)
                    #print ('Solution using', len(bins), 'bins:')
                    #for bin in bins:
                    #    print (bin)
                        






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
            #self.ww = self.spinBox.value()

        @staticmethod
        def getRes(parent = None, msg = ""):
            print (msg)
            dialog = MyDialog1Class(parent)
            if msg:
                dialog.label.setText(msg)
            result = dialog.exec_()
            res = dialog.spinBox.value()
            return (res, result == QW.QDialog.Accepted)


    dialog2_class = uic.loadUiType("dialog2.ui")[0]
    class MyDialog2Class(QW.QDialog, dialog2_class):
        def __init__(self, parent=None):
            QW.QDialog.__init__(self, parent)
            self.setupUi(self)

        @staticmethod
        def getRes(parent = None, msg = ""):
            print (msg)
            dialog = MyDialog2Class(parent)
            if msg:
                dialog.label.setText(msg)
            result = dialog.exec_()
            res = dialog.lineEdit.text()
            return (float(res), result == QW.QDialog.Accepted)


    app = QW.QApplication(sys.argv)
    myWindow = MyWindowClass(None)
    myWindow.show()
    app.exec_()
