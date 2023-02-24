balances = {}

def set_balance(ticker, volume, avg_buy_price=1, earning=0, init=False):
    global balances
    if not init and balances[ticker]['earning'] is not None:
        cal_earning = balances[ticker]['earning'] + earning
    else:
        cal_earning = earning
    balances[ticker] = {
        'volume': volume,
        'avg_buy_price': avg_buy_price,
        'earning': cal_earning
        }

def get_balance(ticker):
    global balances
    return balances[ticker]

def total_balance():
    total = 0
    for ticker in balances:
        total += balances[ticker]['volume'] * balances[ticker]['avg_buy_price']
    return total