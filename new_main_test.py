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

def init():
    global kis
    
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')
    acc_no = os.getenv('ACC_NO')

    # 객체 생성
    kis = KoreaInvestment(
        api_key=api_key,
        api_secret=api_secret,
        acc_no=acc_no,
        exchange="서울"
        # mock=True # 모의투자
    )

def get_df(ticker, since, count=100):
    temp_dfs = []
    result_df = None
    next_day = since

    while True:
        resp = kis.fetch_ohlcv(
            symbol=ticker,
            timeframe='D',
            adj_price=True,
            since=next_day
        )

        if kis.exchange == "서울":
            df = pd.DataFrame(resp['output2'])
            dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
            df.set_index(dt, inplace=True)
            df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_clpr', 'acml_vol', 'acml_tr_pbmn']]
            df.columns = ['open', 'high', 'low', 'close', 'volume', 'value']
            df.index.name = "date"
        elif kis.exchange == "나스닥":
            df = pd.DataFrame(resp['output2'])
            dt = pd.to_datetime(df['xymd'], format="%Y%m%d")
            df.set_index(dt, inplace=True)
            df = df[['open', 'high', 'low', 'clos', 'tvol', 'tamt']]
            df.columns = ['open', 'high', 'low', 'close', 'volume', 'value']
            df.index.name = "date"

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
    return result_df

init()

# tickers = kis.fetch_symbols()
# print(tickers[tickers['그룹코드'] == 'EF'])

df = get_df("005930","", count=33) #005930
print(df)