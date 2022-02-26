# coding=utf-8

import time

from dao_quote.settings import config
from dao_quote.collect import get_quote
from dao_quote.util.quote_save import quote_save


def collect_save_bar():
    COLLECT_DICT = config.COLLECT_DICT
    save_exchange_dict = COLLECT_DICT['save_exchange_dict']
    type = 'kline'
    db_name = 'dao_quote.db'
    conn_bar = quote_save.get_db_conn(db_name)

    while True:
        for exchange in save_exchange_dict:
            symbol_list = save_exchange_dict[exchange]
            for symbol in symbol_list:
                key_name = '{}_{}_{}'.format(exchange, symbol, type)
                key_name = key_name.lower()
                try:
                    data = get_quote.get_bar(exchange, symbol)
                    quote_save.save_bar(conn_bar, key_name, data)
                    # print(key_name)
                    time.sleep(1)
                except Exception as e:
                    print(key_name, data)
                    print('collect_save_bar, msg: {}'.format(e))
        time.sleep(60*60)
