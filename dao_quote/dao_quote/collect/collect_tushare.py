import time
import redis
import datetime

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.quote_save import quote_save
from dao_quote.util.exchange_api.tushare.tushare_api import tuShare


def manage_stock_data(data):
    bars = []
    for bar in data:
        n_bar = []
        n_bar.append(convert.to_timestamp_date(bar[1])*1000)
        n_bar.append(bar[5])
        n_bar.append(bar[3])
        n_bar.append(bar[4])
        n_bar.append(bar[2])
        n_bar.append(bar[9])
        n_bar.append(bar[10])
        bars.append(n_bar)
    return bars


def collect():
    db_name = 'dao_quote.db'
    conn_bar = quote_save.get_db_conn(db_name)

    ts = tuShare()
    ts_md_symbols = config.COLLECT_DICT['ts_md_symbols']
    start_date = '20100101'
    end_date = '20211205'
    for exchange in ts_md_symbols:
        for symbol in ts_md_symbols[exchange]:
            key_name = '{}_{}_kline.1d'.format('stock', symbol)
            data = ts.get(exchange, symbol, start_date, end_date)
            data = manage_stock_data(data)
            quote_save.save_bar(conn_bar, key_name, data)


def main():
    collect()
