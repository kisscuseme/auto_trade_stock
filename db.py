import sqlite3

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

def drop_table():
    global cur
    cur.execute("DROP TABLE trade_data")

# 회사코드, 회사명, 기준년도, 분기, 매출액, 영업이익, 법인세차감전 순이익, 당기순이익, 가능한 많은 정보
def create_table():
    conn.execute('CREATE TABLE trade_data(corp_code TEXT, date TEXT)')
    conn.execute('CREATE INDEX trade_data_idx1 ON trade_data(corp_code, date)')
    
def insert(corp_code, date):
    global cur
    cur.executemany(
        'INSERT INTO trade_data VALUES (?, ?)',
        [(corp_code, date)]
    )

def delete(corp_code, date):
    global cur
    cur.executemany(
        'DELETE FROM trade_data WHERE corp_code = ? AND date = ?',
        [(corp_code, date)]
    )

def show(corp_code, date):
    global cur
    sql = "SELECT * FROM trade_data WHERE corp_code = '{0}' AND date = '{1}'"
    cur.execute(sql.format(corp_code, date))
    rows = cur.fetchall()
    for row in rows:
        print(row)

if __name__ == "__main__":
    init_db()