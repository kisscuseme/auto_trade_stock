from config import get_send_log_enabled
from telegram_bot import send_log
from util import write_file
import datetime

log_dvsn = 'etf'

def set_log_dvsn(pType='etf'):
    global log_dvsn
    log_dvsn = pType

def make_log(pType, desc, detailOnly=False, sendLog=False):
    global log_dvsn
    basePath = './log/'
    date = datetime.datetime.now().replace(microsecond=0)
    data = '[' + pType + '] ' + str(date) + ' ' + desc
    # strDate = str(date.year)+('0'+str(date.month))[-2:]+('0'+str(date.day))[-2:]
    strDate = 'day_trade_' + log_dvsn

    if detailOnly != True:
        path = basePath
        file_name = strDate +'.log'
        write_file(path, file_name, data)

    path_detail = basePath + 'detail/'
    file_name_detail = strDate + '.log'
    write_file(path_detail, file_name_detail, data)
    
    if sendLog and get_send_log_enabled():
        send_log(data)