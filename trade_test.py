from login import login, version
from dotenv import load_dotenv
import os
import time
import datetime

load_dotenv()

if __name__ == "__main__":
    user_id = os.getenv('USER_ID')
    user_pass = os.getenv('USER_PASS')
    user_cert = os.getenv('CERT_PASS')

    version(user_id, user_pass)
    time.sleep(2)
    kiwoom = login(user_id, user_pass)
    time.sleep(2)

    account_num = kiwoom.GetLoginInfo("ACCOUNT_CNT")        # 전체 계좌수
    accounts = kiwoom.GetLoginInfo("ACCNO")                 # 전체 계좌 리스트
    user_id = kiwoom.GetLoginInfo("USER_ID")                # 사용자 ID
    user_name = kiwoom.GetLoginInfo("USER_NAME")            # 사용자명
    keyboard = kiwoom.GetLoginInfo("KEY_BSECGB")            # 키보드보안 해지여부
    firewall = kiwoom.GetLoginInfo("FIREW_SECGB")           # 방화벽 설정 여부

    print(account_num)
    print(accounts)
    print(user_id)
    print(user_name)
    print(keyboard)
    print(firewall)

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

    # kospi = kiwoom.GetCodeListByMarket('0')
    # kosdaq = kiwoom.GetCodeListByMarket('10')
    # etf = kiwoom.GetCodeListByMarket('8')

    # print(len(kospi), kospi)
    # print(len(kosdaq), kosdaq)
    # print(len(etf), etf)

    name = kiwoom.GetMasterCodeName("005930")
    print(name)

    stock_cnt = kiwoom.GetMasterListedStockCnt("005930")
    print("삼성전자 상장주식수: ", stock_cnt)

    감리구분 = kiwoom.GetMasterConstruction("005930")
    print(감리구분)

    상장일 = kiwoom.GetMasterListedStockDate("005930")
    print(상장일)

    전일가 = kiwoom.GetMasterLastPrice("005930")
    print(int(전일가))

    종목상태 = kiwoom.GetMasterStockState("005930")
    print(종목상태)

    group = kiwoom.GetThemeGroupList(1)
    print(group)

    tickers = kiwoom.GetThemeGroupCode('330')
    for ticker in tickers:
        name = kiwoom.GetMasterCodeName(ticker)
        print(ticker, name)

    # 조건식을 PC로 다운로드
    kiwoom.GetConditionLoad()

    # 전체 조건식 리스트 얻기
    conditions = kiwoom.GetConditionNameList()

    print(conditions)

    if len(conditions) != 0:
        # 0번 조건식에 해당하는 종목 리스트 출력
        condition_index = conditions[0][0]
        condition_name = conditions[0][1]
        codes = kiwoom.SendCondition("0101", condition_name, condition_index, 0)
        print(codes)
    else:
        print("조건없음")
    
    # 문자열로 오늘 날짜 얻기
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")

    # df = kiwoom.block_request("opt10001",
    #                       종목코드="005930",
    #                       output="주식기본정보",
    #                       next=0)
    # print(df)

    df = kiwoom.block_request("opt10081",
                          종목코드="005930",
                          기준일자=today,
                          수정주가구분=1,
                          output="주식일봉차트조회",
                          next=0)
    print(df)

    # sRQName	사용자가 임의로 지정할 수 있는 이름입니다. (예: "삼성전자주문")
    # sScreenNO	화면번호로 "0"을 제외한 4자리의 문자열을 사용합니다. (예: "1000")
    # sAccNo	계좌번호입니다. (예: "8140977311")
    # nOrderType	주문유형입니다. (1: 매수, 2: 매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도 정정)
    # sCode	매매할 주식의 종목코드입니다.
    # nQty	주문수량입니다.
    # nPrice	주문단가입니다.
    # sHogaGb	'00': 지정가, '03': 시장가
    # sOrgOrderNo	원주문번호로 주문 정정시 사용합니다.

    # 삼성전자, 10주, 시장가주문 매수
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