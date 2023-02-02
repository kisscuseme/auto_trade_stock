import sqlite3
import pandas
import datetime

conn = None
cur = None

def init_db():
    global conn, cur
    conn = sqlite3.connect("trade.db")
    cur = conn.cursor()

def close():
    global conn
    conn.close()

def commit():
    global conn
    conn.commit()

def drop_corp_data():
    global cur
    cur.execute("DROP TABLE corp_data")

def drop_trade_data():
    global cur
    cur.execute("DROP TABLE trade_data")

# 회사코드, 회사명, 기준년도, 분기, 매출액, 영업이익, 법인세차감전 순이익, 당기순이익, 가능한 많은 정보
def create_corp_data():
    conn.execute('CREATE TABLE corp_data(corp_code TEXT, date TEXT)')
    conn.execute('CREATE INDEX corp_data_idx1 ON trade_data(corp_code, date)')

def create_trade_data():
    conn.execute('CREATE TABLE trade_data(ticker TEXT, interval TEXT, date TEXT, open TEXT, high TEXT, low TEXT, close TEXT, volume TEXT)')
    conn.execute('CREATE INDEX trade_data_idx1 ON trade_data(ticker, interval, date)')

def insert_trade_data(ticker, interval, date, open, high, low, close, volume):
    global cur
    cur.executemany(
        'INSERT INTO trade_data VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        [(ticker, interval, date, open, high, low, close, volume)]
    )

def delete_trade_data(ticker, interval):
    global cur
    cur.executemany(
        'DELETE FROM trade_data WHERE ticker = ? AND interval = ?',
        [(ticker, interval)]
    )

def insert_corp_data(corp_code, date):
    global cur
    cur.executemany(
        'INSERT INTO corp_data VALUES (?, ?)',
        [(corp_code, date)]
    )

def delete_corp_data(corp_code, date):
    global cur
    cur.executemany(
        'DELETE FROM corp_data WHERE corp_code = ? AND date = ?',
        [(corp_code, date)]
    )

def show_trade_data(ticker, interval, date='19700101'):
    global cur
    sql = "SELECT * FROM trade_data WHERE ticker = '{0}' AND interval = '{1}' AND date >= '{2}'"
    cur.execute(sql.format(ticker, interval, date))
    rows = cur.fetchall()
    for row in rows:
        print(row)

def show_corp_data(corp_code, date):
    global cur
    sql = "SELECT * FROM corp_data WHERE corp_code = '{0}' AND date = '{1}'"
    cur.execute(sql.format(corp_code, date))
    rows = cur.fetchall()
    for row in rows:
        print(row)

def get_etf():
    sql = "SELECT distinct ticker FROM trade_data"
    cur.execute(sql)
    rows = cur.fetchall()
    etf = []
    for row in rows:
        etf.append(row[0])
    return etf

def get_from_date():
    sql = "SELECT min(date) FROM trade_data group by ticker order by min(date) desc"
    cur.execute(sql)
    rows = cur.fetchall()
    date = None
    for row in rows:
        date = row[0]
        break
    return date

def get_df(ticker, interval, input_date='19700101'):
    sql = "SELECT * FROM trade_data WHERE ticker = '{0}' AND interval = '{1}' AND date >= '{2}'"
    cur.execute(sql.format(ticker, interval, input_date))
    ohlcv_data = []
    rows = cur.fetchall()
    for row in rows:
        temp = [row[2], float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7])]
        ohlcv_data.append(temp)
    
    df = pandas.DataFrame(ohlcv_data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pandas.to_datetime(df['date'])
    
    df['date'] = df['date'] + datetime.timedelta(hours=0)
    df = df.set_index('date')
    df.index.name = None

    print(df)

    return df

if __name__ == "__main__":
    init_db()
    create_trade_data()