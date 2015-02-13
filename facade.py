#!/usr/bin/python3
# facade.py
# Программа расчета себестоимости фасадных конструкций
# Date: 26/11/2014
# Author: rost@stogoff.ru
#
# Requirements:
# Python3   https://www.python.org/downloads/
# PyQt5     http://www.riverbankcomputing.com/software/pyqt/download5
# xlrd      https://pypi.python.org/pypi/xlrd
# for windows:
# http://www.lfd.uci.edu/~gohlke/pythonlibs/girnt9fk/cx_Freeze-4.3.3.win-amd64-py3.4.exe


import sys
import math
import configparser

from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtCore import Qt, QRegExp

import price_parser
import bin_packing
import cbr


p_samorez = 0.84
p_bolt = 60.0
p_samorez_okr = 6.0
p_butil_m = 17.0
p_fartuk_m = 50.0
p_krepezh_niz_verh = 375.0 + 70.0
p_krepezh_perekr = 770.0 + 2 * p_bolt

PRICE_FILE = "../прайс_2015_январь.xlsx"
PRICE_CURRENCY = 'USD'  # RUB or USD
price = {}


def get_int_field(field):
    if field.hasAcceptableInput():
        res = int(field.text())
        field.setStyleSheet("QLineEdit{background: white;}")
        field.setToolTip(None)
    else:
        res = 0
        field.setStyleSheet("QLineEdit{background: red;}")
        field.setToolTip("Недопустимое значение!")
    return res


def get_float_field(field):
    try:
        res = float(field.text())
        field.setStyleSheet("QLineEdit{background: white;}")
        field.setToolTip(None)
    except TypeError:
        res = 0
        field.setStyleSheet("QLineEdit{background: red;}")
        field.setToolTip("Недопустимое значение!")
    return res


class FacadeMainClass(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        uic.loadUi("main.ui", self)

        # globals:
        self.h = 0  # высота конструкции
        self.w = 0  # ширина конструкции
        self.area = 0
        self.perimeter = 0
        self.nodes = 0  # число узлов
        self.windowpanes = 0  # число стеклопакетов
        self.np = 0  # число стоек
        self.n_rows = 0  # число рядов ригелей
        self.n_dies = 0  # число сухарей
        self.len_press = 0  # суммарная длина прижимов
        self.fl = 0  # число перекрытий
        self.fh = {}  # высоты перекрытий
        self.profiles = {}  # список профилей "артикул: список длин"
        self.eur_rub = 0
        self.eur_usd = 0
        self.usd_rub = 0

        # validators:
        re = QRegExp("\d{1,2}\.?\d+")
        float_validator = QtGui.QRegExpValidator(re)
        self.edit_width.setValidator(float_validator)
        self.edit_height.setValidator(float_validator)
        self.edit_door_w.setValidator(float_validator)
        self.edit_pillars.setValidator(QtGui.QIntValidator(2, 100, self))
        self.edit_headers.setValidator(QtGui.QIntValidator(2, 100, self))
        self.edit_fl.setValidator(QtGui.QIntValidator(0, 20, self))

        # connecting:
        self.edit_width.textChanged.connect(self.width_changed)
        self.edit_height.textChanged.connect(self.height_changed)
        self.edit_pillars.textChanged.connect(self.pillars_changed)
        self.edit_headers.textChanged.connect(self.headers_changed)
        self.edit_fl.textChanged.connect(self.fl_changed)
        # self.edit_rate.textChanged.connect(self.rate_changed)

        self.actionOpen_pricelist.triggered.connect(self.custom_price_load)
        self.actionExit.triggered.connect(self.close)
        self.pushButton.clicked.connect(self.print_all)
        self.pushButtonF.clicked.connect(self.calc_fasteners)

        # reading config
        try:
            config = configparser.ConfigParser()
            config.read('main.ini')
            if 'h' in config['DEFAULT']:
                self.h = float(config['DEFAULT']['h'])
                self.edit_height.setText("%.3f" % self.h)
            if 'w' in config['DEFAULT']:
                self.w = float(config['DEFAULT']['w'])
                self.edit_width.setText("%.3f" % self.w)
            if 'np' in config['DEFAULT']:
                self.np = int(config['DEFAULT']['np'])
                self.edit_pillars.setText("%d" % self.np)
            if 'n_rows' in config['DEFAULT']:
                self.n_rows = int(config['DEFAULT']['n_rows'])
                self.edit_headers.setText("%d" % self.n_rows)
            self.width_changed()
            self.height_changed()
            self.pillars_changed()
            self.headers_changed()
        except:
            pass
        # currency
        # noinspection PyBroadException
        try:
            self.eur_rub, curr_code = cbr.get_euro_rate()
            self.usd_rub = cbr.get_usd_rate()
            self.eur_usd = self.eur_rub / self.usd_rub
            self.label_rate.setText("1 %s =" % curr_code)
            self.edit_rate.setText("%7.4f" % self.eur_rub)
        except:
            self.eur_rub = 999999
            self.label_rate.setText("1 EUR =")
            self.edit_rate.setText("???")
        self.price_load(PRICE_FILE)

    def r2e(self, amount_rub):
        return amount_rub / self.eur_rub

    def print_all(self):
        for k, v in self.profiles.items():
            print(k)
            print(v)
            s = self.calc_all()
            self.label_total.setText("%.2f" % s)
        return 0

    def calc_all(self):
        s, st_len, price_m, price_p = 0, 0, 0, 0
        for k, prof_list in self.profiles.items():
            p_type = price_parser.gettype(k)
            st_len, price_m, price_p = self.get_data(p_type, k)
            if p_type == 10:
                # окр. до половины хлыста
                bins = bin_packing.pack(prof_list, st_len / 2)
                s += price_p * len(bins) / 2
            else:
                bins = bin_packing.pack(prof_list, st_len)
                s += price_p * len(bins)
                # print(price_p * len(bins))
        s += get_float_field(self.label_sum7)
        s += get_float_field(self.label_sum8)
        s += get_float_field(self.label_sum8_2)
        s += get_float_field(self.label_sum8_3)
        s += get_float_field(self.label_sum8_4)
        return s

    def calc_fasteners(self):
        # 4 самореза на сухарь + 2 на ряд ригелей
        a = (4 * self.n_dies + 2 * self.n_rows) * self.r2e(p_samorez)
        print(a)
        # 2 болта на стойку + 2 на перекрытие
        b = (self.np * 2 + self.fl * 2) * self.r2e(p_bolt)
        print(b)
        # по 1 окр.саморезу на 220 мм планки
        c = self.len_press / 0.22 * self.r2e(p_samorez_okr)
        print(c)
        # бутиловая лента по длине ТПУ-007ММ, формула из calc_rubber()
        d = (self.h * self.np * 2 + self.w * self.n_rows * 2) * self.r2e(p_butil_m)
        print(d)
        # фартук по всей ширине конструкции
        e = self.w * self.r2e(p_fartuk_m)
        print(e)
        # крепеж низ/верх
        f = self.np * 2 * self.r2e(p_krepezh_niz_verh)
        print(f)
        # крепеж к перекрытиям
        g = self.np * self.fl * self.r2e(p_krepezh_perekr)
        print(g)
        sum_fast = a + b + c + d + e + f + g
        self.label_total_f.setText("%.2f" % sum_fast)

    # noinspection PyMethodMayBeStatic
    def price_load(self, fn):
        for i, f in ((1, 'pillars'), (2, 'headers'), (3, 'enhancers'),
                     (4, 'dies'), (5, 'covers'), (6, 'pressings'),
                     (7, 'adapters'), (8, 'rubber'), (9, 'pvc'),
                     (10, 'pads')):
            price[i] = price_parser.parse_f(fn, i)
            if i in (1, 2):
                # Combobox:
                cb = eval("self.comboBox_%d" % i)
                cb.clear()
                cb.addItem("Выберите:")
                for name in sorted(price[i]):
                    cb.addItem(name)
                cb.activated[str].connect(eval("self.calc_%s" % f))
                if not self.h or not self.w or not self.np or not self.n_rows:
                    cb.setEnabled(False)
        return 0

    def custom_price_load(self):
        dia = QtWidgets.QFileDialog()
        file_name, flt = dia.getOpenFileName(self, 'Price list file',
                                             './', '*.xls *.xlsx')
        if file_name:
            print(file_name)
            self.price_load(file_name)
        return 0

    def calc_area(self):
        self.area = self.w * self.h
        self.label_area.setText("%5.3f" % self.area)
        self.perimeter = (self.w + self.h) * 2
        self.label_per.setText("%5.3f" % self.perimeter)
        return 0

    def pillars_changed(self):
        self.np = int(get_int_field(self.edit_pillars))
        # крепеж верх/низ
        f = self.np * 2
        self.label_fasteners.setText("%d" % f)
        # считаем кол-во крепежа к перекрытиям
        if self.fl:
            self.label_16.setEnabled(True)
            self.label_fl_fast.setEnabled(True)
            fl_fast = self.np * self.fl
            self.label_fl_fast.setText("%d" % fl_fast)
        return 0

    def headers_changed(self):
        self.n_rows = int(get_int_field(self.edit_headers))
        self.nodes = self.n_rows * (self.np - 1)
        self.label_nodes.setText("%d" % self.nodes)
        self.windowpanes = (self.n_rows - 1) * (self.np - 1)
        self.label_wp.setText("%d" % self.windowpanes)
        if self.n_rows:
            self.comboBox_2.setEnabled(True)
        else:
            self.comboBox_2.setEnabled(False)
        return 0

    def width_changed(self):
        # при изменении ширины пересчитываем площадь и периметр
        self.w = get_float_field(self.edit_width)
        self.calc_area()
        return 0

    def height_changed(self):
        # при изменении высоты при необходимости запрашиваем число перекрытий
        self.h = get_float_field(self.edit_height)
        if self.h:
            self.comboBox_1.setEnabled(True)
        else:
            self.comboBox_1.setEnabled(False)
        self.calc_area()
        if self.h > 3:
            self.label_fl.setEnabled(True)
            self.edit_fl.setEnabled(True)

    def fl_changed(self):
        self.fl = int(get_int_field(self.edit_fl))
        # self.fl, ok = MyDialog1Class.get_res(msg="Число перекрытий:")
        if self.fl:  # нет перекрытий
            for f in range(self.fl):
                m = "Высота между %d и %d перекрытием" % (f, f + 1)
                d = QtWidgets.QInputDialog()
                self.fh[f], ok = d.getDouble(d, "title", m, 1.0, 0.1, 100.0, 2)
                if self.fh[f] > 1000:
                    self.fh[f] /= 1000
            self.pillars_changed()
        return 0

    def get_data(self, p_type, item):
        st_len = price[p_type][item][1]
        price_m = price[p_type][item][0]  # цена за 1 м в USD
        if PRICE_CURRENCY == 'USD':
            price_m /= self.eur_usd  # пересчитываем в евро
        else:
            price_m /= self.eur_rub  # вариант для прайса в рублях
        price_p = price_m * st_len
        return st_len, price_m, price_p

    def calc_pillars(self, item):
        # очистим список профилей от других стоек (и усилителей):
        pl = list(self.profiles)
        for i in pl:
            # если это стойка или усилитель:
            if price_parser.gettype(i) in (1, 3):
                del self.profiles[i]
                print("%s deleted" % i)
        self.profiles[item] = []
        self.np = int(get_int_field(self.edit_pillars))  # число стоек
        if not self.np:
            mb = QtWidgets.QMessageBox()
            mb.warning(mb, 'Message', "Укажите число стоек",
                       QtWidgets.QMessageBox.Ok)
            self.comboBox_1.setCurrentIndex(0)
            return -1

        st_len, price_m, price_p = self.get_data(1, item)
        self.label_20.setText("%.2f" % price_m)
        self.label_21.setText("%.2f" % price_p)

        if not self.fl:  # нет перекрытий
            if self.h > st_len:  #
                num = int(self.h // st_len)  # число целых профилей на 1 стойку
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
            bins = bin_packing.pack(plist, st_len)
            print('Solution using', len(bins), 'bins:')
            # for bin in bins:
            # print (bin)
            sum1 = price_p * len(bins)
            self.label_sum1.setText("%.2f" % sum1)
        self.calc_enhancers()
        self.calc_covers(1)
        self.calc_dies()
        self.calc_pads()
        return 0

    def calc_headers(self, item):
        # очистим список профилей от других ригелей:
        sw = 0
        pl = list(self.profiles)
        for i in pl:
            if price_parser.gettype(i) == 2:  # то есть это ригель
                del self.profiles[i]
                print("%s deleted" % i)
        self.profiles[item] = []
        st_len, price_m, price_p = self.get_data(2, item)
        self.label_23.setText("%.2f" % price_m)
        self.label_24.setText("%.2f" % price_p)
        h_list = []

        if not self.n_rows:
            mb = QtWidgets.QMessageBox()
            mb.warning(mb, 'Error', "Укажите число рядов ригелей",
                       QtWidgets.QMessageBox.Ok)
            self.comboBox_2.setCurrentIndex(0)
            return -1
        self.np = int(get_int_field(self.edit_pillars))
        for i in range(self.np - 1):
            m = "Расстояние между %d и %d стойками" % (i + 1, i + 2)
            d = QtWidgets.QInputDialog()
            lh, ok = d.getDouble(d, "title", m, 1.0, 0.1, 100.0, 2)
            # value=1.0, min=0.1, max=100.0, decimals=2)
            if ok:
                sw += lh
            else:
                self.comboBox_2.setCurrentIndex(0)

                return -1

            if sw > self.w:
                print(sw, self.w)
                mb = QtWidgets.QMessageBox()
                mb.warning(mb, 'Error', "Превышена общая ширина",
                           QtWidgets.QMessageBox.Ok)
                self.comboBox_2.setCurrentIndex(0)
                return -1
            if lh < st_len:
                h_list += [lh]
            else:
                l = lh
                while l > st_len:
                    h_list += [st_len]
                    l -= st_len
                h_list += [l]
        if abs(sw - self.w) > 0.01:
            print(sw, self.w)
            mb = QtWidgets.QMessageBox()
            mb.warning(mb, 'Error', "Суммарное расстояние меньше общей ширины",
                       QtWidgets.QMessageBox.Ok)
            self.comboBox_2.setCurrentIndex(0)
            return -1
        all_h_list = self.n_rows * h_list
        self.profiles[item] += all_h_list
        bins = bin_packing.pack(all_h_list, st_len)
        print('Solution using', len(bins), 'bins:')
        # for bin in bins:
        # print (bin)
        sum1 = price_p * len(bins)
        self.label_sum2.setText("%.2f" % sum1)
        self.calc_covers(2)
        self.calc_dies()
        self.calc_adapters()
        self.calc_rubber()
        self.calc_pvc()
        return 0

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
        pillars = list(self.profiles)
        for art in pillars:
            if art in dict_enh.keys():
                ls = self.profiles[art]
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
                    mb = QtWidgets.QMessageBox()
                    mb.warning(mb, 'Message',
                               "В прайсе отсутствует усилитель %s" % item,
                               QtWidgets.QMessageBox.Ok)
                    self.comboBox_1.setCurrentIndex(0)
                    return -1
                self.label_29.setText(item)
                st_len, price_m, price_p = self.get_data(3, item)
                self.label_25.setText("%.2f" % price_m)
                self.label_26.setText("%.2f" % price_p)
                bins = bin_packing.pack(e_list, st_len)
                print('Solution using', len(bins), 'bins')
                sum1 = price_p * len(bins)
                self.label_sum3.setText("%.2f" % sum1)
                self.profiles[item] = e_list
        return 0

    def calc_dies(self):  # сухари #4
        item = 'ТП-5004'
        self.profiles[item] = []
        length = 0.084  # !!! CHECK it!!!
        self.label_30.setText(item)
        st_len, price_m, price_p = self.get_data(4, item)
        self.label_49.setText("%.2f" % price_m)
        self.label_50.setText("%.2f" % price_p)
        self.n_dies = self.nodes * 2
        die_list = self.n_dies * [length]
        bins = bin_packing.pack(die_list, st_len)
        print('Solution using', len(bins), 'bins:')
        sum1 = price_p * len(bins)
        self.label_sum4.setText("%.2f" % sum1)
        self.profiles[item] = die_list
        return 0

    def calc_covers(self, subtype):  # 5
        if subtype == 1:
            dict_cov = {
                'ТП-50310': 'ТП-5015М',  # pillars
                'ЭК-5002': 'ТП-5015М',
                'ТП-50311': 'ТП-5015М',
                'ЭК-5006': 'ТП-5015М',
                'ТП-50312': 'ТП-5015М',
                'ТП-50313': 'ТП-5015М',
                'ТП-50314': 'ТП-5015М',
                'ТП-50314-01': 'ТП-5015М',
                'ТП-50314-02': 'ТП-5015М'
            }
        else:
            dict_cov = {
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
        sum1 = 0
        plist = list(self.profiles)
        # перебираем все профиля и удаляем крышки этого подтипа
        for art in plist:
            print("art:%s" % art)
            if art in dict_cov.values():
                del self.profiles[art]
                print("%s deleted" % art)
        # перебираем все профиля
        for art in plist:
            if art in dict_cov.keys():
                c_list = self.profiles[art]
                item = dict_cov[art]
                print("added %s" % item)
                if item not in price[5].keys():
                    mb = QtWidgets.QMessageBox()
                    mb.warning(mb, 'Message',
                               "В прайсе отсутствует крышка %s" % item,
                               QtWidgets.QMessageBox.Ok)
                    cb = eval("self.comboBox_%d" % subtype)
                    cb.setCurrentIndex(0)
                    return -1
                st_len, price_m, price_p = self.get_data(5, item)
                bins = bin_packing.pack(c_list, st_len)
                print('Solution using', len(bins), 'bins')
                sum1 += price_p * len(bins)

                self.profiles[item] = c_list
                if subtype == 1:
                    self.label_33.setText(item)
                    self.label_34.setText("%.2f" % price_m)
                    self.label_32.setText("%.2f" % price_p)
                    self.label_sum5.setText("%.2f" % sum1)
                else:
                    self.label_36.setText(item)
                    self.label_35.setText("%.2f" % price_m)
                    self.label_39.setText("%.2f" % price_p)
                    self.label_sum5_2.setText("%.2f" % sum1)
        self.calc_pressings()
        return 0

    def calc_pressings(self):  # 6
        item = 'ТП-5005М'
        self.profiles[item] = []
        sum1 = 0
        press_list = []
        self.len_press = 0
        if item not in price[6].keys():
            mb = QtWidgets.QMessageBox()
            mb.warning(mb, 'Message',
                       "В прайсе отсутствует прижим %s" % item,
                       QtWidgets.QMessageBox.Ok)
            return -1
        self.label_45.setText(item)
        st_len, price_m, price_p = self.get_data(6, item)
        self.label_42.setText("%.2f" % price_m)
        self.label_43.setText("%.2f" % price_p)
        # из длин стоечных и ригельных крышек составляем
        # список требуемых прижимов
        for k, prof_list in self.profiles.items():
            if price_parser.gettype(k) == 5:
                press_list += prof_list
        self.len_press = sum(press_list)
        bins = bin_packing.pack(press_list, st_len)
        print('Solution using', len(bins), 'bins:')
        sum1 += price_p * len(bins)
        self.label_sum6.setText("%.2f" % sum1)
        self.profiles[item] = press_list
        return 0

    def calc_adapters(self):  # 7
        item = 'ТПУ-032-26'  # по периметру
        self.label_61.setText(item)
        st_len, price_m, price_p = self.get_data(7, item)
        self.label_41.setText("%.2f" % price_m)
        length = self.perimeter
        sum1 = price_m * length
        self.label_sum7.setText("%.2f" % sum1)
        return 0

    def calc_rubber(self):  # 8
        item = 'ТПУ-6002'  # по длине стоек *2
        self.label_60.setText(item)
        st_len, price_m, price_p = self.get_data(8, item)
        self.label_46.setText("%.2f" % price_m)
        length = self.h * self.np * 2
        sum1 = price_m * length
        self.label_sum8.setText("%.2f" % sum1)

        item = 'ТПУ-6001'  # по длине ригелей *2
        self.label_64.setText(item)
        st_len, price_m, price_p = self.get_data(8, item)
        self.label_65.setText("%.2f" % price_m)
        length = self.w * self.n_rows * 2
        sum1 = price_m * length
        self.label_sum8_2.setText("%.2f" % sum1)

        item = 'ТПУ-6005'  # в узлах по 110 мм
        self.label_70.setText(item)
        st_len, price_m, price_p = self.get_data(8, item)
        self.label_69.setText("%.2f" % price_m)
        length = self.nodes * 0.11
        sum1 = price_m * length
        self.label_sum8_3.setText("%.2f" % sum1)

        item = 'ТПУ-007ММ'
        self.label_68.setText(item)
        st_len, price_m, price_p = self.get_data(8, item)
        self.label_75.setText("%.2f" % price_m)
        length = self.h * self.np * 2 + self.w * self.n_rows * 2
        sum1 = price_m * length
        self.label_sum8_4.setText("%.2f" % sum1)

        return 0

    def calc_pvc(self):  # 9
        item = 'ТПУ-010-04'
        self.profiles[item] = []
        self.label_62.setText(item)
        st_len, price_m, price_p = self.get_data(9, item)
        self.label_58.setText("%.2f" % price_m)
        self.label_59.setText("%.2f" % price_p)
        sum_length = self.h * self.np + self.w * self.n_rows
        n = math.ceil(sum_length / st_len)
        sum1 = price_p * n
        self.label_sum9.setText("%.2f" % sum1)
        self.profiles[item] = n * [st_len]
        return 0

    def calc_pads(self):  # 10
        item = 'ТП-5095'
        self.profiles[item] = []
        length = 0.1
        self.label_63.setText(item)
        st_len, price_m, price_p = self.get_data(10, item)
        self.label_56.setText("%.2f" % price_m)
        self.label_57.setText("%.2f" % price_p)
        pad_list = self.windowpanes * 2 * [length]
        bins = bin_packing.pack(pad_list, st_len / 2)  # окр. до половины хлыста
        print('Solution using', len(bins), 'bins:')
        sum1 = price_p * len(bins) / 2
        self.label_sum10.setText("%.2f" % sum1)
        self.profiles[item] = pad_list
        return 0


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    desktop = app.desktop()
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap("img.png"))
    splash.showMessage("Loading... ",
                       Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
    splash.show()
    QtWidgets.qApp.processEvents()
    window = FacadeMainClass(None)
    if desktop.width() > 2000:
        x = (1680 - window.width()) // 2
    else:
        x = (desktop.width() - window.width()) // 2
    y = (desktop.height() - window.height()) // 2
    window.move(x, y)
    window.show()
    splash.finish(window)
    sys.exit(app.exec_())
