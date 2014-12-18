import urllib.request
import xml.etree.ElementTree as ETree


def get_euro_rate():
    u = urllib.request.urlopen("http://www.cbr.ru/scripts/XML_daily.asp",
                               timeout=10)
    tree = ETree.fromstring(u.read())
    txt_rate = tree.findall('./Valute[@ID="R01239"]/Value')[0].text
    rate = float(txt_rate.replace(',', '.'))
    code = tree.findall('./Valute[@ID="R01239"]/CharCode')[0].text
    return rate, code


def get_usd_rate():
    u = urllib.request.urlopen("http://www.cbr.ru/scripts/XML_daily.asp",
                               timeout=10)
    tree = ETree.fromstring(u.read())
    txt_rate = tree.findall('./Valute[@ID="R01235"]/Value')[0].text
    rate = float(txt_rate.replace(',', '.'))
    return rate


if __name__ == '__main__':
    print(get_euro_rate())
    print(get_usd_rate())