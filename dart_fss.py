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
    url = base_url + soup.select('.tL > a')[0].attrs['href']
    browser.get(url)
    browser.execute_script("document.querySelectorAll('#listTree a').forEach(function(item){if(item.textContent.indexOf(' 요약재무정보')>-1){item.click();}});")
    time.sleep(0.5)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    url = base_url + soup.select('#ifrm')[0].attrs['src']
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    check_tags = soup.select('p, table')
    return check_tags

def get_column_name(df, col_name=None):
    result = []
    for col in df.columns.get_level_values(-1):
        if col_name in str(col).replace(' ',''):
            result.append(col)
    return result

def get_row_name(df, row_name=None):
    for i in range(len(df)):
        if not df.isna().iloc[i][0] and row_name in df.iloc[i][0].replace(' ',''):
            # return df.iloc[i][df.iloc[i].index[1]]
            # print(df.iloc[i])
            return df.iloc[i][1]
    return None

def get_form_data(data):
    result = []
    for tag in data:
        if tag.name == 'table':
            dfs = pd.read_html(str(tag))
            df = dfs[0]
            row = get_row_name(df,row_name='당기순이익')
            if row is not None:
                result.append(row)
            
    return result

def insert_data():
    corp_code = get_corp_code('삼성전자', True)[0]
    # print(corp_code)
    data = get_corp_data_by_web(corp_code['corp_code'])
    form_data = get_form_data(data)
    print(form_data)
    # corp_data = get_corp_data_by_api(corp_code['corp_code'], '2019', '11011', all_div=False)
    # for data in corp_data:
    #     print(data)

insert_data()