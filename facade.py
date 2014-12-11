#!/usr/bin/python
# facade.py
# Программа расчета себестоимости фасадных конструкций
# Date: 26/11/2014
# Author: rost@stogoff.ru
#
# Requirements:
# Python3   https://www.python.org/downloads/
# PyQt5     http://www.riverbankcomputing.com/software/pyqt/download5
# xlrd      https://pypi.python.org/pypi/xlrd


import sys
import math

from PyQt5 import QtWidgets as QWi, uic

import BinPacking
import cbr
import parser

PRICE_FILE = "../прайс_декабрь2014.xlsx"
price = {}


def get_number_field(field):
    try:
        res = float(field.text())
        field.setStyleSheet("QLineEdit{background: white;}")
    except ValueError:
        res = 0
        field.setStyleSheet("QLineEdit{background: red;}")
        field.setToolTip("Введите число!")
        # QW.QMessageBox.question(self, 'Message',
        # "Введите число в поле %s" % field.objectName(),
        # QW.QMessageBox.Ok)
    return res


def get_number_cell(cell):
    try:
        res = float(cell.text())
    except ValueError:
        res = 0
    return res


class MyMainWindowClass(QWi.QMainWindow):
    def __init__(self, parent=None):
        QWi.QMainWindow.__init__(self, parent)
        uic.loadUi("main.ui", self)
        self.edit_width.textChanged.connect(self.calc_area)
        self.edit_height.textChanged.connect(self.calc_area)
        self.edit_pillars.textChanged.connect(self.calc_fasteners)
        self.edit_height.textChanged.connect(self.height_changed)
        self.h = 0  # высота конструкции
        self.fl = 0  # число перекрытий
        self.fh = {}  # высоты перекрытий
        self.profiles = {}  # список профилей "артикул: список длин"
        self.eur_rub = 0
        self.eur_usd = 0
        self.usd_rub = 0
        if 1:  # try:
            self.eur_rub, curr_code = cbr.get_euro_rate()
            self.usd_rub = cbr.get_usd_rate()
            self.eur_usd = self.eur_rub / self.usd_rub
            self.label_rate.setText("1 %s =" % curr_code)
            self.edit_rate.setText("%7.4f" % self.eur_rub)
        else:  # except:
            self.eur_rub = 999999
            self.label_rate.setText("1 EUR =")
            self.edit_rate.setText("???")

        for i, f in ((1, 'pillars'), (2, 'headers')):
            price[i] = parser.parse_f(PRICE_FILE, i)
            # Combobox:
            cb = eval("self.comboBox_%d" % i)
            cb.addItem("Выберите:")
            for name in sorted(price[i]):
                cb.addItem(name)
            cb.activated[str].connect(eval("self.calc_%s" % f))
            cb.setEnabled(False)

    def calc_area(self):
        try:
            w = float(self.edit_width.text())
        except ValueError:
            w = 0
            pass
        try:
            h = float(self.edit_height.text())
        except ValueError:
            h = 0

        area = w * h
        self.label_area.setText("%5.3f" % area)
        perimeter = (w + h) * 2
        self.label_per.setText("%5.3f" % perimeter)

    def calc_fasteners(self):
        try:
            p = int(self.edit_pillars.text())
        except ValueError:
            p = 0
            # self.edit_pillars.
        f = p * 2
        self.edit_fasteners.setText("%d" % f)
        if p:
            self.comboBox_2.setEnabled(True)
        else:
            self.comboBox_2.setEnabled(False)

    def height_changed(self):
        self.h = get_number_field(self.edit_height)
        if self.h:
            self.comboBox_1.setEnabled(True)
        else:
            self.comboBox_1.setEnabled(False)
        if self.h > 3:
            self.fl, ok = MyDialog1Class.getres(msg="Число перекрытий:")
        if not self.fl:  # нет перекрытий
            pass
        else:
            for f in range(self.fl):
                m = "Высота между %d и %d перекрытием" % (f, f + 1)
                self.fh[f], ok = MyDialog2Class.getres(msg=m)
                if self.fh[f] > 1000:
                    self.fh[f] /= 1000
            print(self.fl, self.fh)

    def calc_pillars(self, item):
        print(item)
        # s = 0 # сумма
        if item not in price[1].keys():
            return
        if item not in self.profiles.keys():
            self.profiles[item] = []
        np = int(get_number_field(self.edit_pillars))  # число стоек
        print("np=%s" % np)
        if not np:
            mb = QWi.QMessageBox()
            mb.question(mb, 'Message',
                        "Укажите число стоек", QWi.QMessageBox.Ok)
            self.comboBox_1.setCurrentIndex(0)
            return
        st_len = price[1][item][1]
        price_m = price[1][item][0]  # цена за 1 м в USD
        price_m /= self.eur_usd  # пересчитываем в евро
        # price_m /= self.eur_rub    # вариант для прайса в рублях
        price_p = price_m * st_len
        self.label_20.setText("%.2f" % price_m)
        self.label_21.setText("%.2f" % price_p)

        if not self.fl:  # нет перекрытий
            if self.h > st_len:  #
                num = int(self.h // st_len)  # число целых профилей на 1 ст
                print(num)
                self.profiles[item] += np * num * [st_len]
                sum1 = np * num * price_p  # стоимость целых профилей
                tail = self.h % st_len  # длина нецелого
                self.profiles[item] += np * [tail]
                print("tail=%d" % tail)
                d = st_len // tail  # сколько нецелых получится из 1 проф
                sum2 = np / d * price_p  # стоимость остатков
                self.label_sum1.setText("%.2f" % (sum1 + sum2))
            else:  # общая высота меньше длины профиля
                n = int(st_len // self.h)
                self.profiles[item] += np * [self.h]
                sum1 = math.ceil(np / n) * price_p
                self.label_sum1.setText("%.2f" % sum1)

        else:  # есть перекрытия, стыки будем делать на них
            sh = 0  # sum of heights
            plist = []

            for i in range(self.fl):
                sh += self.fh[i]
                if self.fh[i] <= st_len:
                    plist += np * [self.fh[i]]
                else:
                    print("ERROR")
            # теперь остаток от самого верхнего перекрытия до верха:
            plist += np * [self.h - sh]
            self.profiles[item] += plist
            bins = BinPacking.pack(plist, st_len)
            print('Solution using', len(bins), 'bins:')
            # for bin in bins:
            # print (bin)
            sum1 = price_p * len(bins)
            self.label_sum1.setText("%.2f" % sum1)

    def calc_headers(self, item):
        if item not in price[2].keys():
            return
        if item not in self.profiles.keys():
            self.profiles[item] = []
        np = int(get_number_field(self.edit_pillars))  # число стоек
        st_len = price[2][item][1]
        price_m = price[2][item][0]  # цена за 1 м в USD
        price_m /= self.eur_usd  # пересчитываем в евро
        # price_m /= self.eur_rub    # вариант для прайса в рублях
        price_p = price_m * st_len
        self.label_23.setText("%.2f" % price_m)
        self.label_24.setText("%.2f" % price_p)
        hlist = []
        nrows = int(get_number_field(self.edit_headers))
        for i in range(np - 1):
            m = "Расстояние между %d и %d стойками" % (i + 1, i + 2)
            lh, ok = MyDialog2Class.getres(msg=m)
            if lh < st_len:
                hlist += [lh]
            else:
                l = lh
                while l > st_len:
                    hlist += [st_len]
                    l -= st_len
                hlist += [l]
        allhlist = nrows * hlist
        self.profiles[item] += allhlist
        bins = BinPacking.pack(allhlist, st_len)
        print('Solution using', len(bins), 'bins:')
        # for bin in bins:
        # print (bin)
        sum1 = price_p * len(bins)
        self.label_sum2.setText("%.2f" % sum1)


class MyDialog1Class(QWi.QDialog):
    def __init__(self, parent=None):
        QWi.QDialog.__init__(self, parent)
        uic.loadUi("dialog1.ui", self)

    @staticmethod
    def getres(parent=None, msg=""):
        print(msg)
        dialog = MyDialog1Class(parent)
        if msg:
            dialog.label.setText(msg)
        result = dialog.exec_()
        res = dialog.spinBox.value()
        return res, result == QWi.QDialog.Accepted


class MyDialog2Class(QWi.QDialog):
    def __init__(self, parent=None):
        QWi.QDialog.__init__(self, parent)
        uic.loadUi("dialog2.ui", self)

    @staticmethod
    def getres(parent=None, msg=""):
        print(msg)
        dialog = MyDialog2Class(parent)
        if msg:
            dialog.label.setText(msg)
        dialog.lineEdit.setFocus()
        result = dialog.exec_()
        res = dialog.lineEdit.text()
        return float(res), result == QWi.QDialog.Accepted


if __name__ == '__main__':
    app = QWi.QApplication(sys.argv)
    myWindow = MyMainWindowClass(None)
    myWindow.show()
    print("test0")
    r = app.exec_()
    print(r)
