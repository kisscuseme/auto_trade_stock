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

load_dotenv()

crtfc_key = os.getenv('CRTFC_KEY')

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent={0}'.format(user_agent))
browser = webdriver.Chrome(ChromeDriverManager().install(),options=options)

row_name_list = ['당기순이익','영업이익','자본총계','부채총계']
all_data = {}

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
            if item['stock_code'] is not None:
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
    res = requests.get(url, params=params).json()
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

def get_column_name(df, col_name=None):
    result = []
    for col in df.columns.get_level_values(-1):
        if col_name in str(col).replace(' ',''):
            result.append(col)
    return result

# 행 구분 값 가져오기
def get_row_value(df, row_name=None, index=1):
    for i in range(len(df)):
        if not df.isna().iloc[i][0] and row_name in df.iloc[i][0].replace(' ',''):
            return df.iloc[i][index]
    return None

def get_unit(web_data):
    result = []
    for tag in web_data:
        select_tag = tag.select('td, p')
        for unit in select_tag:
            cond1 = '단위:' in unit.text.replace(' ','')
            cond2 = '주당' not in unit.text.replace(' ','')
            cond3 = '백만원' in unit.text.replace(' ','')
            cond4 = '천원' in unit.text.replace(' ','')
            cond5 = 'USD' in unit.text.replace(' ','')
            cond9 = '원' in unit.text.replace(' ','')
            if cond1 and cond2:
                if cond3:
                    result.append(1000000)
                elif cond4:
                    result.append(1000)
                elif cond5:
                    result.append(0)
                elif cond9:
                    result.append(1)
                else:
                    result.append(None)
    return result


# 연결, 별도 재무제표 구분
def get_dvsn(web_data):
    global row_name_list
    linkCount = 0
    rowCount = 0
    dvsn_count = []
    dvsn = []

    for tag in web_data:
        if '연결' in tag.text:
            linkCount += 1
        if rowCount == len(row_name_list):
            dvsn_count.append(linkCount)
            linkCount = 0
            rowCount = 0
        if tag.name == 'table':
            dfs = pd.read_html(str(tag))
            df = dfs[0]
            for row_name in row_name_list:
                    row = get_row_value(df,row_name=row_name)
                    if row is not None:
                        rowCount += 1
    if len(dvsn_count) == 4:
        dvsn = ['연결','연결','별도','별도']
    else:
        dvsn = ['연결','별도']
    return dvsn

# 당기순이익, 영업이익 가져오기
def get_custom_data(web_data):
    global row_name_list
    rowCount = 0
    dvsn = get_dvsn(web_data)
    unit = get_unit(web_data)
    result = {
        '재무제표': {}
    }

    for d in dvsn:
        result['재무제표'][d] = {}

    print(dvsn)
    print(unit)

    for tag in web_data:
        if tag.name == 'table':
            dfs = pd.read_html(str(tag))
            df = dfs[0]
            for row_name in row_name_list:
                row = get_row_value(df,row_name=row_name)
                if row is not None:
                    rowCount += 1
                    if rowCount < len(dvsn)*len(row_name_list):
                        result['재무제표'][dvsn[int(rowCount/row_name_list)]][row_name] = int(row) * unit[0]

            
    return result

def insert_data():
    global all_data
    # corp_list = get_corp_code()
    corp_list = [{'corp_code': '00956028', 'corp_name': '엑세스바이오', 'stock_code': '950130', 'modify_date': '20170630'}]
    for corp_info in corp_list:
        print(corp_info)
        web_data = get_corp_data_by_web(corp_info['corp_code'])
        custom_data = {}
        if web_data is not None:
            custom_data = get_custom_data(web_data)
        all_data[corp_info['corp_code']] = {
            'name': corp_info['corp_name'],
            'stock_code': corp_info['stock_code'],
            'data': custom_data
        }
        time.sleep(1)
    print(all_data)

    # corp_data = get_corp_data_by_api(corp_info['corp_code'], '2019', '11011', all_div=False)
    # for data in corp_data:
    #     print(data)

insert_data()