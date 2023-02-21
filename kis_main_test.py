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
from koreainvestment import *

kis = None

load_dotenv()
init_db()

def init(exchange="서울"):
    global kis
    
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    acc_no = os.getenv('ACC_NO')

    # 객체 생성
    kis = KoreaInvestment(
        api_key=api_key,
        api_secret=api_secret,
        acc_no=acc_no,
        exchange=exchange
        # mock=True # 모의투자
    )

def insert(df, ticker, interval):
    delete_trade_data(ticker, interval)
    commit()
    for i in range(len(df)):
        date = df.index[i].strftime("%Y%m%d")
        open = df['open'].iloc[i]
        high = df['high'].iloc[i]
        low = df['low'].iloc[i]
        close = df['close'].iloc[i]
        volume = df['volume'].iloc[i]
        insert_trade_data(ticker, interval, date, open, high, low, close, volume)
    commit()

def get_df_from_kis(ticker, since="", interval="D", count=100):
    temp_dfs = []
    result_df = None
    next_day = since

    while True:
        resp = kis.fetch_ohlcv(
            symbol=ticker,
            timeframe=interval,
            adj_price=True,
            since=next_day
        )

        if kis.exchange == "서울":
            date_field = 'stck_bsop_date'
            candle_fields = ['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_clpr', 'acml_vol', 'acml_tr_pbmn']
        elif kis.exchange == "나스닥":
            date_field = 'xymd'
            candle_fields = ['open', 'high', 'low', 'clos', 'tvol', 'tamt']

        df = pd.DataFrame(resp['output2'])
        dt = pd.to_datetime(df[date_field], format="%Y%m%d")
        df.set_index(dt, inplace=True)
        df = df[candle_fields]
        df.columns = ['open', 'high', 'low', 'close', 'volume', 'value']
        df.index.name = None

        len_df = len(df)
        if count < len_df:
            df = df[0:count]
        
        temp_dfs.append(df)
        
        count -= len_df
        
        if count > 0 and len_df > 0:
            next_day = (df.index[-1] - datetime.timedelta(days=1)).strftime("%Y%m%d")
            time.sleep(0.5)
        else:
            break
    
    result_df = pandas.concat(temp_dfs)
    insert(result_df, ticker, interval)

def get_etf():
    tickers = kis.fetch_kospi_symbols()
    etf = tickers[tickers['그룹코드'] == 'EF']
    start_date = pd.to_numeric(etf['상장일자'])
    etf.set_index(start_date, inplace=True)
    target_etf = etf[etf.index < 20180101]
    target_etf.set_index(target_etf['단축코드'], inplace=True)
    etf_dict = target_etf['한글명'].to_dict()

    return etf_dict

def get_etf_from_kis(etf_dict, continue_ticker="0"):
    for ticker in etf_dict:
        print(ticker, etf_dict[ticker])
        if ticker >= continue_ticker:
            get_df_from_kis(ticker, count=1200)

def cut_df(df, index, preiod=20):
    return df[index:preiod+index+2]

def test():
    # 백테스팅 날짜 계산
    start_date = get_from_date()
    last_date = get_to_date()
    delta = 1200
    period = 120

    from_date = start_date.strftime('%Y%m%d')
    to_date = last_date.strftime('%Y%m%d')

    # ETF 차트 정보 로드
    dfs = []
    target_etf = get_etf()
    for ticker in target_etf:
        print(target_etf[ticker])
        dfs.append({
            "ticker": ticker,
            "data": get_df(ticker, 'D', to_date, from_date)})
    
    # 백테스팅
    init_balance(target_etf)
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

init(exchange="서울")
test()

# get_etf()
# print(get_df("284980","D","20230221","20180217"))