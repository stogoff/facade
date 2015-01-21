import xlrd

WS_NUM = 2  # порядковый номер листа в книге xls
COL_NAME = 'B'  # столбец "наименование"
COL_PRICE = 'M'  # столбец "цена"
COL_LEN = 'F'  # столбец "длина"
COL_DENSITY = 'G'  # столбец "уд.вес"

K = 1  # увеличение цены поставщиком со времени выхода прайса
NDS = 1.18

profile_ids = {
    1:  # стойка
        ['ТП-50310', 'ЭК-5002', 'ТП-50311', 'ЭК-5006', 'ТП-50312',
         'ТП-50313', 'ТП-50314', 'ТП-50314-01', 'ТП-50314-02'],
    2:  # ригель
        ['ТП-50320', 'ЭК-5003', 'ТП-50321', 'ЭК-5001', 'ТП-50322',
         'ТП-50323', 'ТП-50324', 'ТП-50325', 'ТП-50326', 'ТП-50327',
         'ТП-50327-01'],
    3:  # усилитель
        ['ТП-5013Н', 'ТП-5013-01Н', 'ТП-5013-02Н', 'ТП-5013-03Н',
         'ТП-5013-04Н', 'ТП-5013-05Н', 'ТП-5013-06Н'],
    4:  # сухарь
        ['ТП-5004', 'ТП-5011', 'ТП-50303', 'ТП-50304', 'ТП-5021М'],
    5:  # крышка
        ['ТП-5014М', 'ТП-5015М', 'ТП-5046', 'ТП-50382', 'ТП-50374',
         'ТП-50375', 'ТП-50309'],
    6:  # прижим
        ['ТП-5005М', 'ТП-50358', 'ТП-5045', 'ТП-50308', 'ТП-50305'],
    7:  # адаптер
        ['ТПУ-032-26', ],  # 'ТП-50353', 'ТП-50355', 'ТП-50356', 'ТП-50359М'],
    8:  # резина
        ['ТПУ-6001', 'ТПУ-6002', 'ТПУ-6005', ],
    9:  # ПВХ
        ['ТПУ-010-04', ],
    10:  # подкладка
        ['ТП-5095', ],
}


def gettype(name):
    for j in range(1, 11):
        if name in profile_ids[j]:
            return j
    return None


def col(col_letter):
    return ord(col_letter) - 65


def parse_f(fn, t=1):  # t - назначение профиля

    cnt = 0
    res = {}
    book = xlrd.open_workbook(fn)
    # print ("The number of worksheets is", book.nsheets)
    # print ("Worksheet name(s):", book.sheet_names())
    if t < 8 or t > 9:  # металл
        sh = book.sheet_by_index(WS_NUM - 1)  # так как с 0
        for rx in range(sh.nrows):
            name = sh.cell_value(rx, col(COL_NAME))
            if name in profile_ids[t]:
                price = sh.cell_value(rx, col(COL_PRICE)) * K * NDS
                length = sh.cell_value(rx, col(COL_LEN))
                density = sh.cell_value(rx, col(COL_DENSITY))
                res[name] = [price, length, density]
    else:  # резина и прочее
        for name in profile_ids[t]:
            # print(name)
            for sh_n in range(book.nsheets):
                sh = book.sheet_by_index(sh_n)
                for rx in range(sh.nrows):
                    for cx in range(sh.ncols):
                        if name + " " in str(sh.cell_value(rx, cx)):

                            if sh.cell_value(rx, 2) in ('п.м.', 'п.м',
                                                        'м.', 'м'):
                                length = sh.cell_value(rx, 5)
                            else:
                                length = 0
                            price = sh.cell_value(rx, 7) * K * NDS
                            res[name] = [price, length, 0]
                            cnt += 1
    print("import %d goods of type %d" % (len(res), t))
    return res


if __name__ == '__main__':
    for i in (range(1, 11)):
        print(i, parse_f("../прайс_декабрь2014.xlsx", i))
