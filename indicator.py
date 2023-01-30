import pandas

# 이동평균선
def get_ma(df, n):
    return df['close'].rolling(window=n).mean()

# 거래량평균선
def get_va(df, n):
    return df['volume'].rolling(window=n).mean()

# 노이즈 비율
def get_noise_ratio(df, n=5):
    noise_ratio = 1 - abs(df['open']-df['close'])/(df['high']-df['low'])
    return noise_ratio.rolling(window=n).mean()

# 변동성 돌파 매수 여부
def get_volatility_break(df, k=None):
    if k is None:
        k = get_noise_ratio(df).iloc[-2]
    target_price = (df['close'] + (df['high'] - df['low'])*k).iloc[-2]
    current_price = df['close'].iloc[-1]
    if current_price > target_price:
        return True
    else:
        return False

def rsi(df, n=14):
    delta = df['close'].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    _gain = up.ewm(com=(n -1), min_periods=n).mean()
    _loss = down.abs().ewm(com=(n - 1), min_periods=n).mean()

    RS = _gain / _loss

    ret_rsi = pandas.Series(100 - (100 / (1 + RS)), name='RSI')

    return ret_rsi

def momentum(df, n):
    momentudf = list(df['close'].pct_change(n))
    return momentudf

def get_max_min_gap(df, n):
    return (df['high'] - df['low']).rolling(window=n).mean()

def get_open_close_gap(df, n):
    return (df['close'] - df['open']).rolling(window=n).mean()

def get_open_close_abs_gap(df, n):
    return abs(df['close'] - df['open']).rolling(window=n).mean()

def get_high_close_gap(df, n=1):
    return (df['high'] - df['close']).rolling(window=n).mean()

def get_open_low_gap(df, n=1):
    return (df['open'] - df['low']).rolling(window=n).mean()

def get_high_open_gap(df, n=1):
    return (df['high'] - df['open']).rolling(window=n).mean()

def get_close_low_gap(df, n=1):
    return (df['close'] - df['low']).rolling(window=n).mean()

def get_pnl_rate(df, n=5):
    rate = abs(df['open']-df['close'])/df['open']
    return rate.rolling(window=n).mean()

#일목균형표(기준선=26, 전환선=9)
def get_ichimoku(df, n):
    return (df['high'].rolling(window=n).max() + df['low'].rolling(window=n).min())/2

def get_stochastic(df, n, m, t):
    ndays_high = df['high'].rolling(window=n, min_periods=1).max()
    ndays_low = df['low'].rolling(window=n, min_periods=1).min()
    fast_k = ((df['close'] - ndays_low) / (ndays_high - ndays_low)) * 100
    slow_k = fast_k.ewm(span=m).mean()
    slow_d = slow_k.ewm(span=t).mean()
    return {
        'k': slow_k,
        'd': slow_d
    }

def get_macd(df, m_NumFast=12, m_NumSlow=26, m_NumSignal=9):
    ema_fast = df['close'].ewm( span = m_NumFast, min_periods = m_NumFast - 1).mean()
    ema_slow = df['close'].ewm( span = m_NumSlow, min_periods = m_NumSlow - 1).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm( span = m_NumSignal, min_periods = m_NumSignal-1).mean()
    return {
        'macd': macd,
        'macd_signal': macd_signal
    }