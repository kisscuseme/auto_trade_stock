from balances_test import get_balance
from make_log import make_log
from indicator import *
import traceback
from util import *

# 매도 조건
def sell_conditions(pTicker, current_price, inTime=True):
    try:
        if inTime:
            make_log('정보', pTicker + ': ' + str(current_price) + ': 매수 대상 아닌 모든 건 매도', detailOnly=True)
            return True
        else:
            avg_buy_price = float(get_balance(pTicker)['avg_buy_price'])
            loss = (current_price - avg_buy_price)/avg_buy_price
            ret = loss < -0.02
            if ret:
                make_log('정보', pTicker + ': ' + str(current_price) + ': 손절, 손실률: ' + str(loss*100) + '%' , detailOnly=True)
            return ret
    except Exception as ex:
        vType = '에러'
        log = 'sell_conditions error! ' + traceback.format_exc()
        make_log(vType, log, detailOnly=True)
        return False

# 매수 조건
def buy_conditions(pTicker, df, current_price):
    target_list = [] 
    target_list.append('290130')
    
    find_ticker = False
    for target in target_list:
        if pTicker.find(target) > -1:
            find_ticker = True

    if find_ticker:
        ret_val = etf_buy_condition(pTicker, df, current_price)
    else:
        ret_val = etf_buy_condition(pTicker, df, current_price)

    return ret_val

def etf_buy_condition(pTicker, df, current_price):
    try:
        if len(df) > 20:
            ma1 = get_ma(df, 1)
            ma3 = get_ma(df, 3)
            ma5 = get_ma(df, 5)
            ma10 = get_ma(df, 10)
            ma15 = get_ma(df, 15)
            ma20 = get_ma(df, 20)
            ma60 = get_ma(df, 60)
            ma120 = get_ma(df, 120)
            va1 = get_va(df, 1)
            va3 = get_va(df, 3)
            va20 = get_va(df, 20)
            va60 = get_va(df, 60)
            va120 = get_va(df, 120)
            macd = get_macd(df)

            # 최초 매수 시 체크
            cond_va = True
            cond_gc = True
            cond_bal = True
            balance = get_balance(pTicker) 

            if balance['volume'] == 0:
                cond_va = va3.iloc[-2] < va1.iloc[-1]
            
                cond_init = ma20.iloc[-1] < ma5.iloc[-1] and ma20.iloc[-2] < ma20.iloc[-1]

                cond5 = ma120.iloc[-2] < ma120.iloc[-1] and ma60.iloc[-2] < ma60.iloc[-1] and ma20.iloc[-2] < ma20.iloc[-1] and ma10.iloc[-2] < ma10.iloc[-1] and ma5.iloc[-2] < ma5.iloc[-1] and ma3.iloc[-2] < ma3.iloc[-1]
                cond6 = ma120.iloc[-1] < ma60.iloc[-1] and ma120.iloc[-1] < ma60.iloc[-1] and ma20.iloc[-1] < ma10.iloc[-1] and ma10.iloc[-1] < ma5.iloc[-1] and ma5.iloc[-1] < ma3.iloc[-1]
                cond_gc = (ma3.iloc[-2] < ma120.iloc[-2] and ma3.iloc[-1] > ma120.iloc[-1]) #or (ma20.iloc[-2] < ma60.iloc[-2] and ma20.iloc[-1] > ma60.iloc[-1]) or (ma5.iloc[-2] < ma20.iloc[-2] and ma5.iloc[-1] > ma20.iloc[-1])

                cond_after = cond5 or cond6 or cond_gc
                
                cond = cond_init and cond_after and cond_va
            else:
                cond = etf_after_buy_conditions(pTicker, df) and cond_bal

            make_log('정보', '{} 매수 조건 cond => {}'.format(pTicker, cond), detailOnly=True)
            return cond           
        else:
            make_log('정보', '거래 데이터 정보 부족, 매수 안 함', detailOnly=True)
            return False
    except Exception as ex:
        vType = '에러'
        log = 'new_buy_conditions error! : ' + pTicker + ' : ' + traceback.format_exc()
        make_log(vType, log, detailOnly=True)
        return False

def etf_after_buy_conditions(pTicker, df):
    try:
        if len(df) > 20:
            # ia3 = get_ichimoku(df, 3)
            # ia5 = get_ichimoku(df, 5)
            # ia10 = get_ichimoku(df, 10)
            # ia20 = get_ichimoku(df, 20)
            # ga1 = get_max_min_gap(df, 1)
            ga2 = get_max_min_gap(df, 2)
            ga3 = get_max_min_gap(df, 3)
            # ga5 = get_max_min_gap(df, 5)
            ga7 = get_max_min_gap(df, 7)
            ga10 = get_max_min_gap(df, 10)
            ga13 = get_max_min_gap(df, 13)
            # ga15 = get_max_min_gap(df, 15)
            # ga26 = get_max_min_gap(df, 26)
            oc1 = get_open_close_gap(df, 1)
            oc3 = get_open_close_gap(df, 3)
            oc5 = get_open_close_gap(df, 5)
            oc7 = get_open_close_gap(df, 7)
            # oc10 = get_open_close_gap(df, 10)
            oca1 = get_open_close_abs_gap(df, 1)
            oca2 = get_open_close_abs_gap(df, 2)
            oca3 = get_open_close_abs_gap(df, 3)
            oca5 = get_open_close_abs_gap(df, 5)
            oca10 = get_open_close_abs_gap(df, 10)
            oca20 = get_open_close_abs_gap(df, 20)
            ma1 = get_ma(df, 1)
            ma2 = get_ma(df, 2)
            ma3 = get_ma(df, 3)
            ma4 = get_ma(df, 4)
            ma5 = get_ma(df, 5)
            ma7 = get_ma(df, 7)
            ma10 = get_ma(df, 10)
            # ma12 = get_ma(df, 12)
            ma15 = get_ma(df, 15)
            ma20 = get_ma(df, 20)
            va1 = get_va(df, 1)
            va2 = get_va(df, 2)
            va3 = get_va(df, 3)
            # va4 = get_va2(df, 4)
            va5 = get_va(df, 5)
            # va7 = get_va2(df, 7)
            va10 = get_va(df, 10)
            # va15 = get_va2(df, 15)
            va20 = get_va(df, 20)
            nr1 = get_noise_ratio(df,n=1)
            nr2 = get_noise_ratio(df,n=2)
            nr3 = get_noise_ratio(df,n=3)
            nr5 = get_noise_ratio(df,n=5)
            nr10 = get_noise_ratio(df,n=10)
            rsi7 = rsi(df,n=7)
            # rsi10 = rsi(df,n=10)
            # rsi14 = rsi(df,n=14)
            hc1 = get_high_close_gap(df, 1)
            ol1 = get_open_low_gap(df, 1)
            ho1 = get_high_open_gap(df, 1)
            cl1 = get_close_low_gap(df, 1)
            stcst = get_stochastic(df, 14, 7, 7)
            macd = get_macd(df)
            pnl5 = get_pnl_rate(df, 5)

            cond_ma1 = ma2.iloc[-1] < ma1.iloc[-1] or ma3.iloc[-1] < ma2.iloc[-1] or ma4.iloc[-1] < ma3.iloc[-1] or ma5.iloc[-1] < ma4.iloc[-1]
            cond_ma2 = ma5.iloc[-2] < ma2.iloc[-2] or ma5.iloc[-2] < ma3.iloc[-2] or ma3.iloc[-2] < ma2.iloc[-2] or ma5.iloc[-2] < ma4.iloc[-2]
            cond_ma3 = ga3.iloc[-1] > ga10.iloc[-1] or ga3.iloc[-1] > ga13.iloc[-1] or ga2.iloc[-1] > ga7.iloc[-1]
            # cond_ma4 = (ia3.iloc[-1] - ia10.iloc[-1])/ia10.iloc[-1] >= 0 or (ia3.iloc[-1] - ia20.iloc[-1])/ia20.iloc[-1] >= 0 or (ia3.iloc[-1] - ia5.iloc[-1])/ia5.iloc[-1] >= 0
            cond_ma5 = ma3.iloc[-1] < ma1.iloc[-1] and ma5.iloc[-1] < ma1.iloc[-1] and ma10.iloc[-1] < ma1.iloc[-1] and ma20.iloc[-1] < ma1.iloc[-1]
            cond_ma = cond_ma1 or cond_ma2 or cond_ma3
            cond_va1 = va5.iloc[-1] < va3.iloc[-1] or va10.iloc[-1] < va5.iloc[-1] or va20.iloc[-1] < va10.iloc[-1]
            cond_va2 =  va3.iloc[-2] < va2.iloc[-2] or va5.iloc[-2] < va3.iloc[-2]
            cond_va3 = 5*va10.iloc[-2] > va1.iloc[-1]
            cond_va = cond_va1 or cond_va2
            # cond_vb = get_volatility_break(df,k=5)
            cond_rsi = rsi7.iloc[-1] < 30
            cond_stcst = stcst['d'].iloc[-1] > stcst['k'].iloc[-1]
            cond_macd = macd['macd'].iloc[-1] > macd['macd_signal'].iloc[-1] and macd['macd'].iloc[-1] > 0
            cond_tail = oc1.iloc[-1] <= 0 #and ho1.iloc[-1] < cl1.iloc[-1]
            # cond_ai = predict_buy(pTicker, df.iloc[-1].name.strftime("%Y%m%d"))
            
            cond_fall = 0
            cond_minus = []
            cond_m_cnt = 0
            cond_plus = []
            cond_p_cnt = 0
            cond_down_cnt = 0
            cond_huge_down_cnt = 0
            cond_huge_up_cnt = 0
            cond_st_up_cnt = 0
            cond_up_cnt = 0
            cond_before_up_cnt = 0
            # cond_1st_up_yn = False
            # cond_2nd_up_yn = False
            # cond_tg_cnt = 0
            oc_min = min([oca1.iloc[-1],oca1.iloc[-2],oca1.iloc[-3]] )
            cond_minus_cnt = 0
            cond_minus_total = 0
            cond_small_oc = 0
            for i in range(10):
                if 3*oc_min < oca1.iloc[-1-i] and oc1.iloc[-1-i] < 0:
                    cond_fall += 1

                if oc1.iloc[-1-i] <= 0:
                    cond_minus.append(oca1.iloc[-1-i])
                    cond_m_cnt += 1

                    if oca1.iloc[-1-i] > 2*oca20.iloc[-1]:
                        cond_huge_down_cnt += 1
                else:
                    cond_plus.append(oca1.iloc[-1-i])
                    cond_p_cnt += 1

                    if oca1.iloc[-1-i] > 2*oca20.iloc[-1]:
                        cond_huge_up_cnt += 1

                if i < 5:
                    if oc1.iloc[-1-i] >= 0:
                        cond_up_cnt += 1
                        # if i == 0:
                        #     cond_1st_up_yn = True
                        # if i == 1:
                        #     cond_2nd_up_yn = True
                        if i < 3:
                            cond_st_up_cnt += 1
            
                    if oc1.iloc[-1-i] < 0:
                        cond_down_cnt += (1+i)

                        if 0 < i < 4:
                            cond_minus_total += oca1.iloc[-1-i]
                            cond_minus_cnt += 1
                    
                    if oca1.iloc[-1-i] < 1/10*oca1.iloc[-1]:
                        cond_small_oc += 1
                        
                    if oc1.iloc[-3-i] > 0:
                        cond_before_up_cnt += 1
            
            cond_minus.sort()
            cond_plus.sort()
            cond_m_avg = sum(cond_minus)/cond_m_cnt if cond_m_cnt > 0 else 0
            cond_p_avg = sum(cond_plus)/cond_p_cnt if cond_p_cnt > 0 else 0
            cond_mp = cond_m_cnt >= cond_p_cnt and cond_m_avg >= cond_p_avg

            cond_risk1 = oca1.iloc[-1] > 2*oca10.iloc[-2] and ((oc1.iloc[-1] > 0 and hc1.iloc[-1] > 3*ol1.iloc[-1]) or (oc1.iloc[-1] <= 0 and 3*ho1.iloc[-1] > cl1.iloc[-1]))
            cond_risk2 = cond_mp and oca10.iloc[-1] < oca20.iloc[-1]
            # cond_risk3 = ma5.iloc[-2] > ma5.iloc[-1] and ma10.iloc[-2] > ma10.iloc[-1] and ma20.iloc[-2] > ma20.iloc[-1] and oca1.iloc[-1] > 2*oca20.iloc[-1]
            # cond_risk4 = cond_up_cnt < 3 and oc1.iloc[-1] <= 0 #and rsi7.iloc[-1] > 50 and nr5.iloc[-1] > 1/2
            cond_risk = cond_risk1 and cond_risk2

            cond_up1 = ma2.iloc[-3] < ma2.iloc[-2] and ma5.iloc[-3] < ma5.iloc[-2] and ma3.iloc[-4] < ma3.iloc[-3] and ma5.iloc[-4] < ma5.iloc[-3] and ma4.iloc[-3] < ma4.iloc[-2]
            cond_up2 = ma2.iloc[-2] < ma2.iloc[-1] and ma5.iloc[-2] < ma5.iloc[-1]
            cond_up3 = (ma2.iloc[-2] < ma5.iloc[-2] and ma2.iloc[-1] > ma5.iloc[-1]) or (ma7.iloc[-2] < ma20.iloc[-2] and ma7.iloc[-1] > ma20.iloc[-1])
            cond_up4 = (va2.iloc[-2] < va3.iloc[-2] and va2.iloc[-1] > va3.iloc[-1])
            cond_up5 = ma1.iloc[-3] < ma1.iloc[-2] and ma1.iloc[-2] < ma1.iloc[-1] and ma2.iloc[-3] < ma2.iloc[-2] and ma2.iloc[-2] < ma2.iloc[-1]
            cond_up6 = nr1.iloc[-2] > 4/5 and oc1.iloc[-1] > 0 and ol1.iloc[-1] > 2*oc1.iloc[-1] and oc1.iloc[-3] < 0 and oc1.iloc[-2] < 0 and oca1.iloc[-3] > 3*oca1.iloc[-2]
            cond_up7 = oc1.iloc[-2] > 0 or oc1.iloc[-3] > 0
            cond_up8 = cond_p_cnt > 5 and ma3.iloc[-3] < ma3.iloc[-2] and ma5.iloc[-3] < ma5.iloc[-2] and oca1.iloc[-1] < 0.03*ma1.iloc[-1]
            cond_up9 = oc1.iloc[-1] < 0 and nr1.iloc[-1] > 2/3 and cond_m_cnt > 5
            cond_up = ((cond_up1 or cond_up2 or cond_up3 or cond_up5 or cond_up8) and (cond_up7)) or cond_up4 or cond_up6
            cond_upward = (ma10.iloc[-1] - ma10.iloc[-2] > 0 and ma10.iloc[-2] - ma10.iloc[-3] > 0) or (ma20.iloc[-1] - ma20.iloc[-2] > 0 and ma20.iloc[-2] - ma20.iloc[-3] > 0) or (ma15.iloc[-1] - ma15.iloc[-2] > 0 and ma15.iloc[-2] - ma15.iloc[-3] > 0)

            cond_down = cond_down_cnt > 3 and cond_up_cnt < 3

            cond_downward1 = ma20.iloc[-1] - ma20.iloc[-2] <= 0 and ma20.iloc[-2] - ma20.iloc[-3] <= 0
            cond_downward2 = ma10.iloc[-1] - ma10.iloc[-2] <= 0 and ma10.iloc[-2] - ma10.iloc[-3] <= 0
            cond_downward3 = ma7.iloc[-1] - ma7.iloc[-2] <= 0 and ma7.iloc[-2] - ma7.iloc[-3] <= 0
            cond_downward = cond_downward1 or cond_downward2 or cond_downward3

            cond_up_and_down = oc1.iloc[-2] > 0 and oc1.iloc[-1] < 0 and oca1.iloc[-2] < oca1.iloc[-1] and cond_mp 
            cond_huge_down = cond_huge_down_cnt >= 2 and cond_huge_up_cnt <= 1
            cond_down_base = cond_huge_down and cond_downward1 and (nr5.iloc[-1] > 1/2 or nr3.iloc[-1] > 1/2 or nr1.iloc[-1] > 1/2)

            cond_continue = oc1.iloc[-1] > 0 and oc1.iloc[-2] > 0 and oc1.iloc[-3] > 0 and ma20.iloc[-1] < ma2.iloc[-1]

            cond_noise1 = nr1.iloc[-1] < 3/4 and cond_downward
            cond_noise2 = nr3.iloc[-1] < 3/4 and nr5.iloc[-1] < 4/5 and (cond_upward or cond_up3 or cond_up4)
            cond_noise3 = oc1.iloc[-2] <= 0 and oc1.iloc[-1] <= 0 and nr1.iloc[-1] > 5/6
            cond_noise4 = oc1.iloc[-1] < 0 and nr2.iloc[-1] > 3/4 and 3/2*ho1.iloc[-1] > cl1.iloc[-1] and ma2.iloc[-2] > ma2.iloc[-1]
            cond_noise5 = ma2.iloc[-2] < ma2.iloc[-1] and ma3.iloc[-2] < ma3.iloc[-1] and ma5.iloc[-2] < ma5.iloc[-1] and cond_continue
            cond_noise = cond_noise1 or cond_noise2 or cond_noise3 or cond_noise5

            cond_oc1 = (cond_down and oc1.iloc[-1] > 0) or not cond_down
            cond_oc2 = oc1.iloc[-2] < oc1.iloc[-1]
            # cond_oc3 = not cond_oc2 and nr1.iloc[-1] < 10/11
            cond_oc4 = oc1.iloc[-1] < 0 and 2*oca5.iloc[-1] < oca5.iloc[-5]
            cond_oc5 = oc1.iloc[-1] < 0 and 2*oca1.iloc[-2] < oca1.iloc[-1]

            cond_max = min(cond_minus) < max(cond_plus)
            # cond_tail2 = oc1.iloc[-1] <= 0 and nr2.iloc[-1] > 1/2

            cond_sec = (ma2.iloc[-1] < ma2.iloc[-2] and (nr3.iloc[-1] > 2/3 or nr2.iloc[-1] > 2/3)) or abs(1 - ma5.iloc[-1]/ma20.iloc[-1]) < 1/1000
            cond_trd = (va2.iloc[-1] < va5.iloc[-1] or va2.iloc[-1] < va3.iloc[-1]) and cond_downward and cond_tail and cond_mp
            
            cond_min = oc_min == abs(oc1.iloc[-1])
            cond_tg =  oc1.iloc[-1] > 0 and hc1.iloc[-1] > ol1.iloc[-1] and hc1.iloc[-1] > 9/2*oc1.iloc[-1]
            cond_now = (oc1.iloc[-1] <= 0 and 5/2*(oca1.iloc[-1] + oca1.iloc[-2]) > oca3.iloc[-1]) or oc1.iloc[-1] > 0

            cond_small = oca5.iloc[-2]/ma1.iloc[-2] < 2/100 and oca10.iloc[-2]/ma1.iloc[-2] < 2/100 and oc1.iloc[-1] <= 0 and oc1.iloc[-2] <= 0 and cond_mp
            cond_change = oca5.iloc[-2]/ma1.iloc[-2] > 1/100 and oca10.iloc[-2]/ma1.iloc[-2] > 1/100
            cond_short_up = cond_down and oc1.iloc[-1] > 2*oca10.iloc[-1]

            cond_big_down = cond_down_cnt > 3 and 5*oca1.iloc[-1] < max(cond_minus) and nr5.iloc[-1] > 3/4 and nr10.iloc[-1] > 2/3
            cond_down_up = cond_m_cnt > 6 and max(cond_minus)/ma1.iloc[-1] > 0.1 and oc1.iloc[-1] > 0

            # cond_big_up = oc1.iloc[-1] > 0 and oca1.iloc[-1] > 5*oca5.iloc[-2] and ma5.iloc[-1] < ma3.iloc[-1] < ma2.iloc[-1]

            cond_stop1 = ma3.iloc[-2] < ma3.iloc[-1] and ma5.iloc[-2] < ma5.iloc[-1]
            cond_stop2 = 1.01*ma20.iloc[-2] > ma20.iloc[-1]
            cond_stop3 = oca1.iloc[-1]/ma1.iloc[-1] < 0.01 and oca10.iloc[-5]/ma1.iloc[-1] < 0.02 and nr1.iloc[-1] > 3/4
            cond_stop4 = oc1.iloc[-1] < 0 and oc1.iloc[-2] > 0 and oca1.iloc[-1] > oca1.iloc[-2] and nr1.iloc[-1] > 1/2
            cond_stop5 = oc1.iloc[-1] < 0 and nr10.iloc[-1] > 3/4 and nr1.iloc[-1] > 4/5
            cond_stop6 = ma5.iloc[-2] > ma5.iloc[-1] and nr10.iloc[-1] > 1/2
            cond_stop7 = oc1.iloc[-1] < 0 and oc1.iloc[-2] > 0 and oc1.iloc[-3] < 0
            cond_stop8 = oca1.iloc[-2] < oca1.iloc[-1] + oca1.iloc[-3]
            cond_stop9 = nr3.iloc[-1] > 3/4
            cond_stop10 = nr1.iloc[-1] > 6/7 and rsi7.iloc[-1] > 70
            # cond_stop11 = ma2.iloc[-2] > ma2.iloc[-1] and ma3.iloc[-2] < ma3.iloc[-1]
            # cond_stop12 = (oca1.iloc[-1] + oca1.iloc[-3])/2 < oca1.iloc[-2] and oc1.iloc[-2] < 0
            # cond_stop13 = nr1.iloc[-1] > 2/3 and (va1.iloc[-1] + va1.iloc[-3])/2 < va1.iloc[-2] and nr10.iloc[-1] > 1/2
            cond_stop14 = oc1.iloc[-1] > 0 and oc1.iloc[-2] < 0 and oc1.iloc[-3] < 0
            cond_stop15 = nr1.iloc[-2] > 3/4 or nr1.iloc[-3] > 3/4 or nr1.iloc[-4] > 3/4
            cond_stop16 = oca1.iloc[-2] > 1/2*oca1.iloc[-1] and oca5.iloc[-3] < 1/2*oca1.iloc[-2] and cond_small_oc > 1
            cond_stop17 = oc1.iloc[-1] > 0 and hc1.iloc[-1] > 3*oc1.iloc[-1]
            
            cond_stop_a = cond_stop1 and cond_stop2 and (cond_stop3 or cond_stop4)
            cond_stop_b = cond_stop1 and cond_stop5
            cond_stop_c = cond_stop6 and cond_stop7 and cond_stop8
            cond_stop_d = cond_stop7 and cond_stop9
            cond_stop_e = cond_stop10
            # cond_stop_f = cond_stop2 and cond_stop11 and cond_stop12 and cond_stop13
            cond_stop_g = cond_stop14 and cond_stop15 and cond_stop16
            cond_stop_h = cond_stop17

            cond_20_min_1 = min(df['close'].iloc[-20:].min(), df['open'].iloc[-20:].min()) < ma1.iloc[-1]
            cond_20_min_2 = df['low'].iloc[-20:].min() < ma1.iloc[-1]
            cond_20_min = cond_20_min_1

            oc1_minus_cnt = 0
            oca1_sum = 0
            for i in range(3):
                if oc1.iloc[-2-i] < 0:
                    oc1_minus_cnt += 1
                    oca1_sum += oca1.iloc[-2-i]

            cond_chaos_1 = oc1.iloc[-1] > 0 and oc1_minus_cnt > 1 and oca1.iloc[-1] > 2*oca1_sum
            cond_chaos = cond_chaos_1

            cond_sidewalk_cnt = 0
            if oca3.iloc[-1]/ma3.iloc[-1] < 0.03:
                cond_sidewalk_cnt += 1
            if oca3.iloc[-4]/ma3.iloc[-4] < 0.03:
                cond_sidewalk_cnt += 1
            cond_sidewalk_1 = cond_sidewalk_cnt > 0
            cond_sidewalk_2 = oca3.iloc[-1]/ma3.iloc[-1] < 0.05 and oca3.iloc[-4]/ma3.iloc[-4] < 0.05
            cond_sidewalk = cond_sidewalk_1 and cond_sidewalk_2

            cond_init = (ma20.iloc[-1] < ma1.iloc[-1] and ma20.iloc[-2] < ma20.iloc[-1])
            cond_base = (cond_fall < 5 or cond_rsi or cond_macd) and not cond_down_base and not cond_up_and_down and not cond_small

            cond1 = cond_ma and cond_va and cond_up and cond_noise and cond_now and not cond_risk and cond_max and not cond_chaos
            cond2 = ((cond_sec or cond_trd) and (cond_oc1 or cond_oc2 or cond_oc4 or cond_oc5)) or (not cond_sec and not cond_trd)

            cond_fixed = ((cond_base and cond1 and cond2) or (not cond_base and cond_ma5 and cond_min and not cond_huge_down and not cond_short_up)) #and not cond_stop_f
            cond_last1 = cond_init and not cond_tg and not cond_noise4 and not cond_stop_a and not cond_stop_b and not cond_stop_c and not cond_stop_d and not cond_stop_g
            cond_last2 = not cond_init and cond_change and not (cond_tg and cond_va3) and not cond_big_down and not cond_down_up #and not cond_stop_e and not cond_stop_h
            
            cond_except_1 = cond_before_up_cnt > 4 and oc1.iloc[-2] <= 0 and oc1.iloc[-1] > 0
            cond_except_2 = cond_p_cnt > 5 and oc1.iloc[-1] > 0 and 2*oca1.iloc[-2] < cl1.iloc[-2]
            cond_except_3 = pnl5.iloc[-3] < 0.02 and oc1.iloc[-2] > 0 and oc1.iloc[-1] < 0 and ma10.iloc[-1] < ma5.iloc[-1] < ma3.iloc[-1]
            cond_except_4 = oc1.iloc[-3] > 0 and oc1.iloc[-2] > 0 and oc1.iloc[-1] < 0 and oca1.iloc[-1] < 1/2*oca2.iloc[-2] and nr1.iloc[-2] < 3/4
            
            cond_except = cond_except_1 or cond_except_2 or cond_except_3 or cond_except_4
            
            # cond_add = cond_big_up
            
            # cond_future1 = ma20.iloc[-1] > ma5.iloc[-1] or ma20.iloc[-1] > ma3.iloc[-1] or ma20.iloc[-1] > ma2.iloc[-1]
            # cond_future2 = ma10.iloc[-1] > ma5.iloc[-1] or ma10.iloc[-1] > ma3.iloc[-1] or ma10.iloc[-1] > ma2.iloc[-1]
            # cond_future3 = ma5.iloc[-1] > ma3.iloc[-1] or ma5.iloc[-1] > ma2.iloc[-1] or ma5.iloc[-1] > ma1.iloc[-1]
            # cond_future = cond_future1 or cond_future2 or cond_future3

            cond = (((cond_last1 or cond_last2) and cond_fixed) or cond_except)

            log_str1 = 'ma20: {},ma5: {}, ma3: {}'
            log_msg1 = log_str1.format(get_num_to_str(ma20.iloc[-1]), get_num_to_str(ma5.iloc[-1]), get_num_to_str(ma3.iloc[-1]))
            
            log_str2 = 'va5: {}, va3: {}, price: {}'
            log_msg2 = log_str2.format(get_num_to_str(va5.iloc[-1]), get_num_to_str(va3.iloc[-1]), get_num_to_str(df['close'].iloc[-1]))
            
            log_str3 = 'cond_last1:, {}, cond_last2: {}, cond_fixed: {}, cond_except: {}'
            log_msg3 = log_str3.format(cond_last1, cond_last2, cond_fixed, cond_except)

            make_log('정보', '{} 매수 조건 {}, {}, {}'.format(pTicker, log_msg1, log_msg2, log_msg3), detailOnly=True)
            
            log_str4 = 'cond_init: {}, cond_tg: {}, cond_noise4: {}, cond_stop_a: {}, cond_stop_b: {}, cond_stop_c: {}, cond_stop_d: {}, cond_stop_g: {}'
            log_msg4 = log_str4.format(cond_init, cond_tg, cond_noise4, cond_stop_a, cond_stop_b, cond_stop_c, cond_stop_d, cond_stop_g)

            make_log('정보', '{} 매수 조건 cond_last1 => {}'.format(pTicker, log_msg4), detailOnly=True)
            
            cond_last2 = not cond_init and cond_change and not (cond_tg and cond_va3) and not cond_big_down and not cond_down_up
            
            log_str5 = 'cond_init: {}, cond_change: {}, cond_tg: {}, cond_va3: {}, cond_big_down: {}, cond_down_up: {}'
            log_msg5 = log_str5.format(cond_init, cond_change, cond_tg, cond_va3, cond_big_down, cond_down_up)

            make_log('정보', '{} 매수 조건 cond_last2 => {}'.format(pTicker, log_msg5), detailOnly=True)
           
            log_str6 = 'cond_base: {}, cond1: {}, cond2: {}, cond_ma5: {}, cond_min: {}, cond_huge_down: {}, cond_short_up: {}'
            log_msg6 = log_str6.format(cond_base, cond1, cond2, cond_ma5, cond_min, cond_huge_down, cond_short_up)

            make_log('정보', '{} 매수 조건 cond_fixed => {}'.format(pTicker, log_msg6), detailOnly=True)
            
            log_str7 = 'cond_except_1: {}, cond_except_2: {}, cond_except_3: {}, cond_except_4: {}'
            log_msg7 = log_str7.format(cond_except_1, cond_except_2, cond_except_3, cond_except_4)

            make_log('정보', '{} 매수 조건 cond_except => {}'.format(pTicker, log_msg7), detailOnly=True)
            
            log_str8 = 'cond_ma: {}, cond_va: {}, cond_up: {}, cond_noise: {}, cond_now: {}, cond_risk: {}, cond_max: {}'
            log_msg8 = log_str8.format(cond_ma, cond_va, cond_up, cond_noise, cond_now, cond_risk, cond_max)

            make_log('정보', '{} 매수 조건 cond1 => {}'.format(pTicker, log_msg8), detailOnly=True)
            
            return cond
        else:
            make_log('정보', '거래 데이터 정보 부족, 매수 안 함', detailOnly=True)
            return False
    except Exception as ex:
        vType = '에러'
        log = 'buy_conditions error! : ' + pTicker + ' : ' + traceback.format_exc()
        make_log(vType, log, detailOnly=True)
        return False
