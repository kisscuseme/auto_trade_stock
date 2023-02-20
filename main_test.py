from login import login
from dotenv import load_dotenv
import os
import time
import datetime
import pandas as pd
from db import *
from indicator import *
from conditions import *
from balances_test import *
from trade_test import *
import exchange_calendars as ecals
import math
from util import *

kiwoom = None

load_dotenv()
init_db()

def init(test=True):
    global kiwoom
    
    user_id = os.getenv('USER_ID')
    user_pass = os.getenv('USER_PASS')
    if test:
        user_cert = None
    else:
        user_cert = os.getenv('CERT_PASS')

    # 로그인 처리
    kiwoom = login(user_id, user_pass, user_cert)

def insert(df, ticker, interval):
    delete_trade_data(ticker, interval)
    commit()
    for i in range(len(df)):
        date = df['일자'].iloc[i]
        open = df['시가'].iloc[i]
        high = df['고가'].iloc[i]
        low = df['저가'].iloc[i]
        close = df['현재가'].iloc[i]
        volume = df['거래량'].iloc[i]
        insert_trade_data(ticker, interval, date, open, high, low, close, volume)
    commit()

def get_tr(etf, last_ticker, count=3):
    try:
        now = datetime.datetime.now()
        today = now.strftime("%Y%m%d")
        count = 3
        for ticker in etf:
            start_date = kiwoom.GetMasterListedStockDate(ticker)
            if start_date < now - datetime.timedelta(600*count) and ticker >= last_ticker:
                name = kiwoom.GetMasterCodeName(ticker)
                print(ticker, name, start_date)
                dfs = []
                last_ticker = ticker
                for i in range(count):
                    dfs.append(kiwoom.block_request("opt10081",
                                        종목코드=ticker,
                                        기준일자=today,
                                        수정주가구분=1,
                                        output="주식일봉차트조회",
                                        next=i*2))
                    time.sleep(3.6)
                df = pd.concat(dfs)
                insert(df, ticker, 'day')
    except Exception as ex:
        print('[오류]', ex)
        time.sleep(3.6)
        print('재시도 중...')
        get_tr(etf, last_ticker, count)

def buy_list():
    etf = get_etf()
    return etf

def cut_df(df, index, preiod=20):
    return df[index:preiod+index+2]

def check_holiday(date):
    XKRX = ecals.get_calendar("XKRX") # 한국 코드
    # holiday_list = XKRX.schedule.loc[start_date.strftime("%Y-%m-%d"):last_date.strftime("%Y-%m-%d")]
    return XKRX.is_session(date.strftime("%Y-%m-%d"))

def test():
    # TEST
    test_flag = False

    # 로그인
    # init()

    # 백테스팅 날짜 계산
    start_date = get_from_date()
    last_date = get_to_date()
    delta = 1196
    period = 120

    from_date = start_date.strftime('%Y%m%d')
    to_date = last_date.strftime('%Y%m%d')

    # ETF 차트 정보 로드
    dfs = []
    etf =  get_etf()
    pick_tickers = select_tickers()
    for ticker in etf:
        name = get_ticker_name(ticker)
        # if name.find('TIGER') > -1:
        if ticker in pick_tickers:
            print(name)
            dfs.append({
                "ticker": ticker,
                "data": get_df(ticker, 'day', to_date, from_date)})

            if test_flag:
                if len(dfs) == 5:
                    break
    
    # 백테스팅
    init_balance(etf)
    cut_rate = 0.01
    make_log('정보', '테스트 시작')
    print(start_date, last_date)
    for i in range(delta+1):
        target_tickers = []
        target_tickers_only = []
        now_date = None

        # 매수 대상 선정
        for df in dfs:
            temp_df = cut_df(df['data'], i, period)
            now_df = temp_df[0:period+1]
            now_date = now_df.index[-1]
            current_price = temp_df['open'].iloc[-1]
            if buy_conditions(df['ticker'], now_df, current_price):
                target_tickers.append(df)
                target_tickers_only.append(df['ticker'])
        
        print(now_date, len(target_tickers))

        # 매도 로직
        for df in dfs:
            if get_balance(df['ticker'])['volume'] != 0:
                temp_df = cut_df(df['data'], i, period)
                now_df = temp_df[0:period+1]
                current_price = temp_df['open'].iloc[-1]
                low_price = temp_df['low'].iloc[-1]
                avg_buy_price = balances[df['ticker']]['avg_buy_price']
                now_rate = (avg_buy_price - low_price)/avg_buy_price
                if now_rate > cut_rate:
                    sell(df['ticker'], avg_buy_price*(1-cut_rate), balances, now_df)
                elif df['ticker'] not in target_tickers_only or sell_conditions(df['ticker'], current_price, False):
                    sell(df['ticker'], current_price, balances, now_df)

        # 매수 로직
        adjust_factor = 1 #len(dfs)/(len(dfs) - len(target_tickers))/2
        change = math.ceil(get_balance('KRW')['volume']/(len(target_tickers)+1)*adjust_factor)
        # change = math.ceil(get_balance('KRW')['volume']/(len(etf)+1))
        for target_df in target_tickers:
            if get_balance(target_df['ticker'])['volume'] == 0:
                if change > 100000:
                    temp_df = cut_df(target_df['data'], i, period)
                    now_df = temp_df[0:period+1]
                    current_price = temp_df['open'].iloc[-1]
                    buy(target_df['ticker'], current_price, balances, change, now_df)
    
    print(balances)
    print(total_balance())
    # write_json('./data/', 'balance' + '.json', balances, True)

def select_tickers():
    result = []
    check_balance = read_json('./data/', 'balance' + '.json')
    sort_result = sorted(check_balance.items(), key = lambda item: item[1]['earning'], reverse=True)
    cnt = 0
    cut_num = 15
    for data in sort_result:
        name = get_ticker_name(data[0])
        if data[1]['earning'] > 0:
            cnt += 1
            if cnt < cut_num:
                print(data[0], name, math.ceil(data[1]['earning']))
                result.append(data[0])
            else:
                break
    return result


if __name__ == "__main__":
    test()
    # select_tickers()
