import pandas as pd

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