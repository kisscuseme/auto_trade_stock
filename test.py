import win32gui
import win32con
import win32api
import os
from login import *

kor_notepad = "제목 없음 - Windows 메모장"
eng_notepad = "Untitled - Notepad"

hwnd = win32gui.FindWindow(None, kor_notepad)

if hwnd == 0:
    hwnd = win32gui.FindWindow(None, "*"+kor_notepad)

if hwnd != 0:
    edit = win32gui.GetDlgItem(hwnd, 0xF)

    win32api.SendMessage(edit, win32con.WM_CHAR, ord('H'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('e'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('l'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('l'), 0)
    win32api.Sleep(100)
    win32api.SendMessage(edit, win32con.WM_CHAR, ord('o'), 0)
    win32api.Sleep(100)
else:
    print("메모장을 찾지 못했습니다.")

def test():
    user_id = os.getenv('USER_ID')
    user_pass = os.getenv('USER_PASS')
    kiwoom = login(user_id, user_pass)

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
    # get_tr(etf, last_ticker='0', count=3)

    # 테스트 종목
    # ticker = "005930"

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
    # sRQName = "시장가매수"
    # sScreenNO = "0101"
    # sAccNo = accounts[0]
    # nOrderType = 1
    # sCode = "005930"
    # nQty = 10
    # nPrice = 0
    # sHogaGb = "03"
    # sOrgOrderNo = ""

    # kiwoom.SendOrder(sRQName, sScreenNO, sAccNo, nOrderType, sCode, nQty, nPrice, sHogaGb, sOrgOrderNo)