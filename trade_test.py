from login import login
from dotenv import load_dotenv
import os
import time
import datetime
import pandas as pd
from db import *

def insert(df, ticker, interval):
    init_db()
    delete_trade_data(ticker, interval)
    for i in range(len(df)):
        date = df['일자'].iloc[i]
        open = df['시가'].iloc[i]
        high = df['고가'].iloc[i]
        low = df['저가'].iloc[i]
        close = df['현재가'].iloc[i]
        volume = df['거래량'].iloc[i]
        insert_trade_data(ticker, interval, date, open, high, low, close, volume)
    commit()

if __name__ == "__main__":
    load_dotenv()
    user_id = os.getenv('USER_ID')
    user_pass = os.getenv('USER_PASS')
    user_cert = os.getenv('CERT_PASS')

    # 로그인 처리
    kiwoom = login(user_id, user_pass)
    time.sleep(2)

    # 전체 계좌 리스트
    accounts = kiwoom.GetLoginInfo("ACCNO")
    print('계좌:', accounts)

    # "0"  코스피
    # "3"  ELW
    # "4"  뮤추얼펀드
    # "5"  신주인수권
    # "6"  리츠
    # "8"  ETF
    # "9"  하이얼펀드
    # "10" 코스닥
    # "30" K-OTC
    # "50" 코넥스
    etf = kiwoom.GetCodeListByMarket('8')

    # 테스트 종목
    # ticker = "005930"

    # 종목명
    # name = kiwoom.GetMasterCodeName(ticker)
    # print(ticker, name)
    
    # 문자열로 오늘 날짜 얻기
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")
    count = 3
    target_etf = []
    dfs = []
    for ticker in etf:
        name = kiwoom.GetMasterCodeName(ticker)
        start_date = kiwoom.GetMasterListedStockDate(ticker)
        print(ticker, name, start_date)
        
        if start_date < now - datetime.timedelta(600*count):
            target_etf.append(ticker)
    
    for ticker in target_etf:
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

    # init_db()
    # df = get_df(ticker, 'day', start_date.strftime("%Y%m%d"))
    # print(df)

    #-------------------------------------------------------------------------------------------------
    # 주문 기능
    # sRQName	사용자가 임의로 지정할 수 있는 이름입니다. (예: "삼성전자주문")
    # sScreenNO	화면번호로 "0"을 제외한 4자리의 문자열을 사용합니다. (예: "1000")
    # sAccNo	계좌번호입니다. (예: "8140977311")
    # nOrderType	주문유형입니다. (1: 매수, 2: 매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도 정정)
    # sCode	매매할 주식의 종목코드입니다.
    # nQty	주문수량입니다.
    # nPrice	주문단가입니다.
    # sHogaGb	'00': 지정가, '03': 시장가
    # sOrgOrderNo	원주문번호로 주문 정정시 사용합니다.
    #-------------------------------------------------------------------------------------------------

    # 예시) 삼성전자, 10주, 시장가주문 매수
    sRQName = "시장가매수"
    sScreenNO = "0101"
    sAccNo = accounts[0]
    nOrderType = 1
    sCode = "005930"
    nQty = 10
    nPrice = 0
    sHogaGb = "03"
    sOrgOrderNo = ""

    # kiwoom.SendOrder(sRQName, sScreenNO, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo)
    