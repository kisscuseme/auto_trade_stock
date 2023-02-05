from make_log import make_log
from util import get_num_to_str
from balances_test import *
import time
import traceback
import math

slippage = 0.0001
base_ls_amount = 50000000
disabled_ls = True

def buy(pTicker, current_price, balances, change, df=None):
    global slippage
    try:
        local_slippage = slippage
        balance = get_balance('KRW')['volume']
        price = current_price
        if change/base_ls_amount > 1:
            local_slippage += (0.0015 * change/base_ls_amount)
        if disabled_ls:
            local_slippage = 0.0 #force setting
        needs = math.ceil(change * (1.0015 + local_slippage))
        if balance < needs:
            needs = balance
            change = needs / 1.0015
        volume = math.ceil(change / price)

        if get_balance(pTicker)['volume'] == 0:
            set_balance(pTicker, volume, price)
        else:
            old_volume = balances[pTicker]['volume']
            old_price = balances[pTicker]['avg_buy_price']
            set_balance(pTicker, old_volume + volume, (old_price*old_volume + price*volume)/(old_volume+volume))

        balances['KRW']['volume'] -= volume * current_price * 1.0015
        vType = '매수'
        log = '[' + str(df.iloc[-1].name) + '] ' + pTicker + ' --> ' + get_num_to_str(needs,point=0) + ' / price ' + get_num_to_str(price,point=2)
        log += ' / vol. ' + get_num_to_str(volume,point=1) + ' / balance ' + get_num_to_str(get_balance('KRW')['volume'],point=0)
        log += ' / total ' + get_num_to_str(total_balance(),point=0)
        make_log(vType, log, sendLog=False)
        time.sleep(0.1)
    except Exception as ex:
        print('test_buy error!', traceback.format_exc())


def sell(pTicker, current_price, balances, df=None, leverage=1):
    global slippage
    try:
        local_slippage = slippage
        price = current_price
        volume = balances[pTicker]['volume']
        if current_price*volume/base_ls_amount > 1:
            local_slippage += (0.0015 * current_price*volume/base_ls_amount)
        if disabled_ls:
            local_slippage = 0.0 #force setting
        avg_price = balances[pTicker]['avg_buy_price']
        change = (avg_price * volume + (price - avg_price) * volume * leverage) * (0.9985 - local_slippage)
        balances['KRW']['volume'] += change
        sign = ' (-) '
        res = price > avg_price
        if res:
            sign = ' (+) '
        earn_amount = change - avg_price * volume
        earn_rate = earn_amount/(avg_price*volume)*100
        set_balance(pTicker, 0, 1, earn_amount)
        vType = '매도'
        log = '[' + str(df.iloc[-1].name) + '] ' + pTicker + sign + get_num_to_str(change,point=0) + ' / rate ' + get_num_to_str(earn_rate,point=1) + '% / price ' + get_num_to_str(price,point=2)
        log += ' / vol. ' + get_num_to_str(volume,point=1) + ' / balance ' + get_num_to_str(get_balance('KRW')['volume'],point=0)
        log += ' / total ' + get_num_to_str(total_balance(),point=0)
        make_log(vType, log, sendLog=False)
        time.sleep(0.1)
        return [earn_amount, earn_rate]
    except Exception as ex:
        print('test_sell error!', traceback.format_exc())