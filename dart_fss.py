from zipfile import ZipFile
import requests
import xmltodict
from io import BytesIO
from dotenv import load_dotenv
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import time
from bs4 import BeautifulSoup
import pandas as pd
from util import write_json
import math

load_dotenv()

crtfc_key = os.getenv('CRTFC_KEY')
headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"}
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent={0}'.format(user_agent))
browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)

all_data = {}
except_corp_code = ['01476219']

# 기업 코드 ex) [{'corp_code': '00126380', 'corp_name': '삼성전자', 'stock_code': '005930', 'modify_date': '20220509'}]
def get_corp_code(name=None, match=None):
    global crtfc_key
    url = 'https://opendart.fss.or.kr/api/corpCode.xml'
    params = {'crtfc_key': crtfc_key}
    res = requests.get(url, params=params)
    zipfile_bytes = res.content
    zipfile_obj = ZipFile(BytesIO(zipfile_bytes))
    xmlfile_objs = {name: zipfile_obj.read(name) for name in zipfile_obj.namelist()}
    xml_str = xmlfile_objs['CORPCODE.xml'].decode('utf-8')
    data_dict = xmltodict.parse(xml_str).get('result', {}).get('list')
    result = []

    if match == True:
        for item in data_dict:
            if name == item['corp_name'] and item['stock_code'] is not None:
                result.append(item)
    elif match == False:
        for item in data_dict:
            if name in item['corp_name'] and item['stock_code'] is not None:
                result.append(item)
    else:
        for item in data_dict:
            if item['stock_code'] is not None and item['corp_code'] not in except_corp_code:
                result.append(item)
    return result

# fs_div = CFS:연결재무제표, OFS:재무제표, sj_div = BS:재무상태표, IS:손익계산서
def get_corp_data_by_api(corp_code, bsns_year, reprt_code, fs_div='OFS', sj_div='IS', all_div=False):
    global crtfc_key
    url = 'https://opendart.fss.or.kr/api/fnlttMultiAcnt.json'
    params = {
        'crtfc_key': crtfc_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code
    }
    res = requests.get(url, params=params, headers=headers).json()
    result = []
    for item in res['list']:
        if all_div:
            result.append(item)
        elif item['fs_div'] == fs_div:
            if item['sj_div'] == sj_div:
                result.append(item)
    return result

def get_corp_data_by_web(corp_code):
    global browser
    if browser is None:
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=webdriver.ChromeOptions())
    now = datetime.datetime.now()
    ymd_from = str(now.year-1) + str(now.month).rjust(2,'0') + str(now.day).rjust(2,'0')
    ymd_to = str(now.year) + str(now.month).rjust(2,'0') + str(now.day).rjust(2,'0')
    data = {
        "textCrpCik": corp_code,
        "startDate": ymd_from,
        "endDate": ymd_to,
        "publicType": "A001"
    }
    base_url = 'https://dart.fss.or.kr'
    res = requests.post(base_url + '/dsab007/detailSearch.ax', data)
    soup = BeautifulSoup(res.content, 'html.parser')
    a_tag = soup.select('.tL > a')
    if len(a_tag) > 0:
        url = base_url + a_tag[0].attrs['href']
        browser.get(url)
        browser.execute_script("document.querySelectorAll('#family option').forEach(function(item){if(item.getAttribute('title') && item.getAttribute('title').indexOf('사업보고서')>-1){changeFamily(item.getAttribute('value'));}});")
        browser.execute_script("document.querySelectorAll('#listTree a').forEach(function(item){if(item.textContent.indexOf('III. 재무에 관한 사항')>-1){item.click();}});")
        time.sleep(0.5)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        url = base_url + soup.select('#ifrm')[0].attrs['src']
        res = requests.get(url)
        print(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        check_tags = soup.select('p, table')
        return check_tags
    else:
        return None

def get_index_data(data):
    result = []
    for i, tag in enumerate(data):
        if tag.text != '':
            result.append(
                {
                    'index': i,
                    'name': tag.name,
                    'data': tag
                }
            )
    return result

def get_tag_data(data, tag_name):
    result = []
    for tag in data:
        if tag['name'] == tag_name:
            result.append(tag)
    return result

def get_target_data(data, include_words):
    result = []
    for tag in data:
        for word in include_words:
            if word in tag['data'].text.replace(' ',''):
                result.append(tag)
                break
    return result

def get_df_data(tag):
    dfs = pd.read_html(str(tag['data']))
    df = dfs[0]
    return df

def get_ness_data(data, ness_words):
    result = data
    for word in ness_words:
        result = get_target_data(result, [word])
    return result

def get_row_value(df, row_name=None, index=1):
    for i in range(len(df)):
        if not df.isna().iloc[i][0] and row_name in str(df.iloc[i][0]).replace(' ',''):
            val = df.iloc[i][index]
            print(row_name)
            print(val)
            return val
    return None

def get_column_name(df, col_name=None):
    result = []
    for col in df.columns.get_level_values(-1):
        if col_name in str(col).replace(' ',''):
            result.append(col)
    return result

def get_custom_data(corp_code):
    row_name_list = ['매출액','당기순이익','영업이익','자본총계','부채총계']
    result = {
        '재무제표': {
            '연결': {},
            '별도': {}
        }
    }
    
    web_data = get_corp_data_by_web(corp_code)

    if web_data is not None:
        index_data = get_index_data(web_data)

        # 단위 정보 정리
        unit_info = []

        # 재무제표
        table_data = get_tag_data(index_data, 'table')
        fs_data = get_ness_data(table_data, row_name_list)

        # 단위
        ness_unit_words = ['단위:']
        no_ness_unit_words = ['주당']
        ness_unit_data = get_ness_data(index_data, ness_unit_words)
        unit_words_kor = ['백만원','천원','원','KRW']
        unit_words_for = ['USD','CNY','RMB','JPY','엔']
        unit_words = unit_words_kor + unit_words_for
        unit_numbers_kor = [1000000,1000,1,1]
        unit_numbers_for = [0,0,0,0,0]
        unit_numbers = unit_numbers_kor + unit_numbers_for
        unit_data = get_target_data(ness_unit_data, unit_words)

        # 단위 데이터 전처리
        for i in range(len(unit_data)):
            unit_text = unit_data[i]['data'].text.replace(' ','')
            if '주당순이익:' in unit_text:
                 unit_data[i]['data'] = BeautifulSoup(str(unit_data[i]['data']).replace('주당순이익',''), 'html.parser')

        for i in range(len(fs_data)):
            unit_info.append({
                'str': None
            })
            for unit in unit_data:
                if unit['name'] == 'table':
                    select_tags = unit['data'].select('td')
                elif unit['name'] == 'p':
                    select_tags = [unit['data']]
                for tag in select_tags:
                    tag_text = tag.text.replace(' ','')
                    if ness_unit_words[0] in tag_text and no_ness_unit_words[0] not in tag_text:
                        if i == 0:
                            if unit['index'] <= fs_data[i]['index']:
                                unit_info[i]['str'] = unit
                                break
                        elif i < len(fs_data):
                            if fs_data[i-1]['index'] < unit['index'] <= fs_data[i]['index']:
                                unit_info[i]['str'] = unit
                                break

            # 단위 못찾을 경우 탐색
            if unit_info[i]['str'] is None:
                df = get_df_data(fs_data[i])
                check_row_name = '부채총계'
                origin = get_row_value(df,row_name=check_row_name)
                for table in table_data:
                    temp_unit_num = None
                    if  fs_data[i]['index'] < table['index']:
                        df = get_df_data(table)
                        comp = get_row_value(df, row_name=check_row_name)
                        if comp is not None:
                            for unit in unit_data:
                                if fs_data[i]['index'] < unit['index'] <= table['index']:
                                    if unit['name'] == 'table':
                                        select_tags = unit['data'].select('td')
                                    elif unit['name'] == 'p':
                                        select_tags = [unit['data']]
                                    for tag in select_tags:
                                        tag_text = tag.text.replace(' ','')
                                        if ness_unit_words[0] in tag_text and no_ness_unit_words[0] not in tag_text:
                                            for j in range(len(unit_words)):
                                                if unit_words[j] in tag_text:
                                                    temp_unit_num = unit_numbers[j]
                                                    break

                            if temp_unit_num is not None:
                                cut_len = None
                                if len(str(origin)) < len(str(comp)):
                                    cut_len = len(str(origin))
                                else:
                                    cut_len = len(str(comp))
                                if str(origin).isdigit() and str(comp).isdigit() and round(int(str(origin)[0:cut_len-1])/int(str(comp)[0:cut_len-1])) == 1:
                                    temp_unit_str = None
                                    origin_len = len(str(origin))
                                    comp_len = len(str(int(comp)*temp_unit_num))
                                    temp_len = len(str(temp_unit_num))
                                    len_gap = comp_len - origin_len
                                    if len_gap == 6 or temp_len + len_gap == 6:
                                        temp_unit_str = '백만원'
                                    elif len_gap == 3 or temp_len + len_gap == 3:
                                        temp_unit_str = '천원'
                                    elif len_gap == 0 or temp_len + len_gap == 0:
                                        temp_unit_str = '원'

                                    unit_info[i]['str'] = {
                                        'name': 'p',
                                        'data': BeautifulSoup('<p>(단위:'+temp_unit_str+')</p>', 'html.parser')
                                        }
        
        checkForeign = False
        for i in range(int(len(fs_data)/2)):
            if unit_info[i]['str']['name'] == 'table':
                select_tags = unit_info[i]['str']['data'].select('td')
            elif unit_info[i]['str']['name'] == 'p':
                select_tags = [unit_info[i]['str']['data']]
            for tag in select_tags:
                tag_text = tag.text.replace(' ','')
                if ness_unit_words[0] in tag_text and no_ness_unit_words[0] not in tag_text:
                    for j in range(len(unit_words_for)):
                        if unit_words_for[j] in tag_text:
                            checkForeign = True
                            break
        
        if not checkForeign:
            if len(unit_info) < 3:
                fs_data = fs_data[0:1]
                unit_info = unit_info[0:1]
            else:
                fs_data = fs_data[0:2]
                unit_info = unit_info[0:2]
        
        for i in range(len(unit_info)):
            unit_info[i]['num'] = None
            if unit_info[i]['str']['name'] == 'table':
                select_tags = unit_info[i]['str']['data'].select('td')
            elif unit_info[i]['str']['name'] == 'p':
                select_tags = [unit_info[i]['str']['data']]
            for tag in select_tags:
                tag_text = tag.text.replace(' ','')
                if ness_unit_words[0] in tag_text and no_ness_unit_words[0] not in tag_text:
                    for j in range(len(unit_words)):
                        if unit_words[j] in tag_text:
                            unit_info[i]['num'] = unit_numbers[j]
                            break

        for i in range(len(fs_data)):
            if unit_info[i]['num'] != 0:
                df = get_df_data(fs_data[i])
                link = get_row_value(df,'연결')
                dvsn = None
                if link is not None:
                    dvsn = '연결'
                else:
                    dvsn = '별도'
                for row_name in row_name_list:
                    row = get_row_value(df,row_name=row_name)
                    if row is not None:
                        row = str(row)
                        if '-' == row:
                            row = 0
                        elif '△' in row:
                            row = row.replace('△', '').replace(',','')
                            row = int(row) * -1
                        elif 'Δ' in row:
                            row = row.replace('Δ', '').replace(',','')
                            row = int(row) * -1
                        elif '(' in row:
                            row = row.replace('(', '').replace(')', '').replace(',','')
                            row = int(row) * -1
                        else:
                            row = row.replace(',','')
                            row = int(row)
                        result['재무제표'][dvsn][row_name] = row * unit_info[i]['num']
        
    return result

def insert_data():
    global all_data, row_name_list
    corp_list = get_corp_code()
    # corp_list = [{'corp_code': '00956028', 'corp_name': '엑세스바이오', 'stock_code': '950130', 'modify_date': '20170630'}]
    # corp_list = [{'corp_code': '00232317', 'corp_name': '지오엠씨', 'stock_code': '033030', 'modify_date': '20170630'}]
    # corp_list = [{'corp_code': '01170962', 'corp_name': 'GRT', 'stock_code': '900290', 'modify_date': '20181122'}]
    # corp_list = [{'corp_code': '00141389', 'corp_name': '영풍정밀', 'stock_code': '036560', 'modify_date': '20211208'}]
    # corp_list = [{'corp_code': '00351092', 'corp_name': '삼보모터스', 'stock_code': '053700', 'modify_date': '20211208'}]
    # corp_list = [{'corp_code': '00147082', 'corp_name': '재영솔루텍', 'stock_code': '049630', 'modify_date': '20211210'}]
    # corp_list = [{'corp_code': '00146719', 'corp_name': '일화모직공업', 'stock_code': '001590', 'modify_date': '20210618'}]
    # corp_list = [{'corp_code': '00136624', 'corp_name': '신영와코루', 'stock_code': '005800', 'modify_date': '20211215'}]
    # corp_list_skip = [{'corp_code': '00225159', 'corp_name': 'SNT홀딩스', 'stock_code': '036530', 'modify_date': '20211130'}]
    # corp_list_skip = [{'corp_code': '01365384', 'corp_name': '이성씨엔아이', 'stock_code': '379390', 'modify_date': '20220214'}]
    # corp_list_skip = [{'corp_code': '00113492', 'corp_name': '깨끗한나라', 'stock_code': '004540', 'modify_date': '20211202'}]
    corp_list_skip = [{'corp_code': '01117246', 'corp_name': 'EMB', 'stock_code': '278990', 'modify_date': '20220208'}]
    cnt = 0
    for corp_info in corp_list:
        print(corp_info)

        if corp_info['corp_code'] == corp_list_skip[0]['corp_code']:
            cnt += 1
        
        if cnt > 0:
        # if True:
            all_data[corp_info['corp_code']] = {
                'name': corp_info['corp_name'],
                'stock_code': corp_info['stock_code'],
                'data': get_custom_data(corp_info['corp_code'])
            }
            # cnt += 1
            # if cnt == 100:
            #     break
            time.sleep(1)
    print(all_data)
    write_json('./data/', 'all_data' + '.json', all_data, True)

    # corp_data = get_corp_data_by_api(corp_info['corp_code'], '2019', '11011', all_div=False)
    # for data in corp_data:
    #     print(data)

insert_data()

# https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220322000596
# https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220316001424
# https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220321001331
# https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20220308000798