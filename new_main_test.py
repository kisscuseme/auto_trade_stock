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
        acc_no=acc_no
        # mock=True # 모의투자
    )

init()

# tickers = kis.fetch_symbols()
# print(tickers[tickers['그룹코드'] == 'EF'])

resp = kis.fetch_ohlcv(
    symbol="005930",
    timeframe='D',
    adj_price=True,
    since="20220101"
)

# print(resp)

df = pd.DataFrame(resp['output2'])
dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
df.set_index(dt, inplace=True)
df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_clpr']]
df.columns = ['open', 'high', 'low', 'close']
df.index.name = "date"
print(df)