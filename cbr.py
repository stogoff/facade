import urllib.request
import xml.etree.ElementTree as ET
import sys

def get_euro_rate():
    u = urllib.request.urlopen("http://www.cbr.ru/scripts/XML_daily.asp", 
        timeout=10)
    tree = ET.fromstring(u.read())
    ratetxt = tree.findall('./Valute[@ID="R01239"]/Value')[0].text
    rate = float(ratetxt.replace(',', '.'))
    code = tree.findall('./Valute[@ID="R01239"]/CharCode')[0].text
    return(rate,code)


def get_usd_rate():
    u = urllib.request.urlopen("http://www.cbr.ru/scripts/XML_daily.asp", 
        timeout=10)
    tree = ET.fromstring(u.read())
    ratetxt = tree.findall('./Valute[@ID="R01235"]/Value')[0].text
    rate = float(ratetxt.replace(',', '.'))
    code = tree.findall('./Valute[@ID="R01235"]/CharCode')[0].text
    return(rate)
