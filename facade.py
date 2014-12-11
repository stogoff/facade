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
PRICE_CURRENCY = 'USD'  # RUB or USD
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
        self.np = 0  # число стоек
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

        for i, f in ((1, 'pillars'), (2, 'headers'), (3, 'enhancers'),
                     (5, 'covers'), ):
            price[i] = parser.parse_f(PRICE_FILE, i)
            if i in (1, 2):
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
            self.fl, ok = MyDialog1Class.get_res(msg="Число перекрытий:")
        if not self.fl:  # нет перекрытий
            pass
        else:
            for f in range(self.fl):
                m = "Высота между %d и %d перекрытием" % (f, f + 1)
                self.fh[f], ok = MyDialog2Class.get_res(msg=m)
                if self.fh[f] > 1000:
                    self.fh[f] /= 1000

    def calc_pillars(self, item):
        if item not in price[1].keys():
            return
        if item not in self.profiles.keys():
            self.profiles[item] = []
        self.np = int(get_number_field(self.edit_pillars))  # число стоек
        print("np=%s" % self.np)
        if not self.np:
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
                self.profiles[item] += self.np * num * [st_len]
                sum1 = self.np * num * price_p  # стоимость целых профилей
                tail = self.h % st_len  # длина нецелого
                self.profiles[item] += self.np * [tail]
                d = st_len // tail  # сколько нецелых получится из 1 проф
                sum2 = self.np / d * price_p  # стоимость остатков
                self.label_sum1.setText("%.2f" % (sum1 + sum2))
            else:  # общая высота меньше длины профиля
                n = int(st_len // self.h)
                self.profiles[item] += self.np * [self.h]
                sum1 = math.ceil(self.np / n) * price_p
                self.label_sum1.setText("%.2f" % sum1)
        else:  # есть перекрытия, стыки будем делать на них
            sh = 0  # sum of heights
            plist = []
            for i in range(self.fl):
                sh += self.fh[i]
                if self.fh[i] <= st_len:
                    plist += self.np * [self.fh[i]]
                else:
                    print("ERROR")
            # теперь остаток от самого верхнего перекрытия до верха:
            plist += self.np * [self.h - sh]
            self.profiles[item] += plist
            bins = BinPacking.pack(plist, st_len)
            print('Solution using', len(bins), 'bins:')
            # for bin in bins:
            # print (bin)
            sum1 = price_p * len(bins)
            self.label_sum1.setText("%.2f" % sum1)
        self.calc_enhancers()
        return

    def calc_headers(self, item):
        if item not in price[2].keys():
            return
        if item not in self.profiles.keys():
            self.profiles[item] = []
        st_len = price[2][item][1]
        price_m = price[2][item][0]  # цена за 1 м в USD
        if PRICE_CURRENCY == 'USD':
            price_m /= self.eur_usd  # пересчитываем в евро
        else:
            price_m /= self.eur_rub  # вариант для прайса в рублях
        price_p = price_m * st_len
        self.label_23.setText("%.2f" % price_m)
        self.label_24.setText("%.2f" % price_p)
        h_list = []
        n_rows = int(get_number_field(self.edit_headers))
        for i in range(self.np - 1):
            m = "Расстояние между %d и %d стойками" % (i + 1, i + 2)
            lh, ok = MyDialog2Class.get_res(msg=m)
            if lh < st_len:
                h_list += [lh]
            else:
                l = lh
                while l > st_len:
                    h_list += [st_len]
                    l -= st_len
                h_list += [l]
        all_h_list = n_rows * h_list
        self.profiles[item] += all_h_list
        bins = BinPacking.pack(all_h_list, st_len)
        print('Solution using', len(bins), 'bins:')
        # for bin in bins:
        # print (bin)
        sum1 = price_p * len(bins)
        self.label_sum2.setText("%.2f" % sum1)

    def calc_enhancers(self):
        dict_enh = {
            'ТП-50310': 'ТП-5013-01Н',
            'ЭК-5002': 'ТП-5013Н',
            'ТП-50311': 'ТП-5013Н',
            'ЭК-5006': 'ТП-5013-02Н',
            'ТП-50312': 'ТП-5013-02Н',
            'ТП-50313': 'ТП-5013-03Н',
            'ТП-50314': 'ТП-5013-04Н',
            'ТП-50314-01': 'ТП-5013-05Н',
            'ТП-50314-02': 'ТП-5013-06Н'
        }
        for art, ls in self.profiles.items():
            print(art)
            if art in dict_enh.keys():
                if len(ls) > self.np:
                    # считаем число услилителей
                    e250 = self.np * (len(ls) // self.np + 1)
                else:
                    e250 = self.np * 2
                if self.fl > 0:
                    e800 = self.np * self.fl
                else:
                    e800 = 0
                e_list = e250 * [0.25] + e800 * [0.8]
                item = dict_enh[art]
                if item not in price[3].keys():
                    mb = QWi.QMessageBox()
                    mb.information(mb, 'Message',
                                   "В прайсе отсутствует усилитель %s" % item,
                                   QWi.QMessageBox.Ok)
                    return -1
                self.label_29.setText(item)
                st_len = price[3][item][1]
                price_m = price[3][item][0]  # цена за 1 м в USD
                if PRICE_CURRENCY == 'USD':
                    price_m /= self.eur_usd  # пересчитываем в евро
                else:
                    price_m /= self.eur_rub  # вариант для прайса в рублях
                price_p = price_m * st_len
                self.label_25.setText("%.2f" % price_m)
                self.label_26.setText("%.2f" % price_p)
                bins = BinPacking.pack(e_list, st_len)
                print('Solution using', len(bins), 'bins:')
                sum1 = price_p * len(bins)
                self.label_sum3.setText("%.2f" % sum1)

        return

    def calc_covers(self):
        dict_cov = {
            'ТП-50310': 'ТП-5015М',  # pillars
            'ЭК-5002': 'ТП-5015М',
            'ТП-50311': 'ТП-5015М',
            'ЭК-5006': 'ТП-5015М',
            'ТП-50312': 'ТП-5015М',
            'ТП-50313': 'ТП-5015М',
            'ТП-50314': 'ТП-5015М',
            'ТП-50314-01': 'ТП-5015М',
            'ТП-50314-02': 'ТП-5015М',
            'ТП-50320': 'ТП-5014М',  # headers
            'ЭК-5003': 'ТП-5014М',
            'ТП-50321': 'ТП-5014М',
            'ЭК-5001': 'ТП-5014М',
            'ТП-50322': 'ТП-5014М',
            'ТП-50323': 'ТП-5014М',
            'ТП-50324': 'ТП-5014М',
            'ТП-50325': 'ТП-5014М',
            'ТП-50326': 'ТП-5014М',
            'ТП-50327': 'ТП-5014М',
            'ТП-50327-01': 'ТП-5014М'
        }
        for art, ls in self.profiles.items():
            print(art)
            if art in dict_cov.keys():
                c_list = ls
                item = dict_cov[art]
                self.label_33.setText(item)
                st_len = price[5][item][1]
                price_m = price[5][item][0]  # цена за 1 м в USD
                if PRICE_CURRENCY == 'USD':
                    price_m /= self.eur_usd  # пересчитываем в евро
                else:
                    price_m /= self.eur_rub  # вариант для прайса в рублях
                price_p = price_m * st_len
                self.label_34.setText("%.2f" % price_m)
                self.label_32.setText("%.2f" % price_p)
                bins = BinPacking.pack(c_list, st_len)
                print('Solution using', len(bins), 'bins:')
                sum1 = price_p * len(bins)
                self.label_sum3.setText("%.2f" % sum1)


class MyDialog1Class(QWi.QDialog):
    def __init__(self, parent=None):
        QWi.QDialog.__init__(self, parent)
        uic.loadUi("dialog1.ui", self)

    @staticmethod
    def get_res(parent=None, msg=""):
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
    def get_res(parent=None, msg=""):
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
    app.exec_()
