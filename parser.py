import xlrd

WS_NUM = 3              # порядковый номер листа в книге xls
COL_NAME = 'B'          # столбец "наименование"
COL_PRICE_RUB = 'L'     # столбец "цена"
COL_LEN = 'E'           # столбец "длина"
COL_DENSITY = 'F'       # столбец "уд.вес"

K = 1.2                 # увеличение цены поставщиком со времени выхода прайса


def col(col_letter):
    return ord(col_letter)-65


def parse_f(fn, t=1): # t - назначение профиля
    profile_ids = {
                1: 
                    ['ТП-50310', 'ЭК-5002', 'ТП-50311', 'ЭК-5006', 'ТП-50312',
                    'ТП-50313', 'ТП-50314', 'ТП-50314-01', 'ТП-50314-02'],
                2:
                    ['ТП-50320', 'ЭК-5003', 'ТП-50321', 'ЭК-5001', 'ТП-50322',
                    'ТП-50323', 'ТП-50324', 'ТП-50325', 'ТП-50326', 'ТП-50327',
                    'ТП-50327-01']
                    }
    res = []
    book = xlrd.open_workbook(fn)
    #print ("The number of worksheets is", book.nsheets)
    #print ("Worksheet name(s):", book.sheet_names())
    sh = book.sheet_by_index(WS_NUM-1) # так как с 0
    #print (sh.name, sh.nrows, sh.ncols)
    for rx in range(sh.nrows):
        name = sh.cell_value(rx, col(COL_NAME))
        if name in profile_ids[t]:
            price_rub = sh.cell_value(rx, col(COL_PRICE_RUB)) * K
            length = sh.cell_value(rx, col(COL_LEN))
            #density = sh.cell_value(rx, COL_DENSITY)
            
            res.append( [name, price_rub, length, length]) #, density])
    return (res)
    
if __name__ == '__main__':
    print (parse_f("прайс_октябрь_2014.xls", 1))
