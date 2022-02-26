# !/usr/bin/env python
# coding=utf-8

import time
import json
import datetime
import pathmagic

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.vision.order_flow import OrderFlow
from dao_quote.util.quote_save import save_mongo
from dao_quote.util.quote_fetch import quote_fetch


def test_get_hfd():
    exchange = 'ctp'
    symbol = 'FG105'
    begin_time = '2021-02-03 09:00:00'
    end_time = '2021-02-03 09:03:00'
    begin_timestamp = int(convert.to_timestamp(begin_time))
    end_timestamp = int(convert.to_timestamp(end_time))
    db = save_mongo.get_db()
    type_list = []
    type_list.append(config.HFT_TICKER)
    data = quote_fetch.get_hfd(db, exchange, symbol, type_list, begin_timestamp, end_timestamp)
    data = json.loads(data)
    return data


def test_tick_2_trade_list():
    tick_dict_list = test_get_hfd()
    print('tick_dict_list[-1]:')
    print(tick_dict_list[-1])
    of = OrderFlow(print_msg=False)
    trade_dict_list = of.tick_2_trade_list(tick_dict_list)
    for trade_dict in trade_dict_list:
        print(trade_dict)


def main():
    test_tick_2_trade_list()


if __name__ == '__main__':
    main()
