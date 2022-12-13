from zipfile import ZipFile
import requests
import xmltodict
from io import BytesIO
from dotenv import load_dotenv
import os
load_dotenv()

crtfc_key = os.getenv('CRTFC_KEY')

# 기업 코드 ex) [{'corp_code': '00126380', 'corp_name': '삼성전자', 'stock_code': '005930', 'modify_date': '20220509'}]
def get_corp_code(name, match=True):
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
    if match:
        for item in data_dict:
            if name == item['corp_name']:
                result.append(item)
    else:
        for item in data_dict:
            if name in item['corp_name']:
                result.append(item)
    return result

# fs_div = CFS:연결재무제표, OFS:재무제표, sj_div = BS:재무상태표, IS:손익계산서
def get_corp_data(corp_code, bsns_year, reprt_code, fs_div='OFS', sj_div='BS'):
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
        if item['fs_div'] == fs_div:
            if item['sj_div'] == sj_div:
                result.append(item)
    return result

corp_code = get_corp_code('삼성전자')[0]
corp_data = get_corp_data(corp_code['corp_code'], '2021', '11011')
print(corp_data)