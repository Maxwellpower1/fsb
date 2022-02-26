#coding=utf-8

import json
import pathmagic

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.quote_fetch import quote_fetch
from dao_quote.util.quote_save import save_mongo


def test_get_all_ticks():
    db_name = '../../../docs/quote_20200115.db'
    exchange = 'okexf'
    symbol = 'btc_usd-quarter'
    data = quote_fetch.get_all_ticks(db_name, exchange, symbol)
    for i in data[:10]:
        print(i)


def test_get_all_depths():
    db_name = '../../../docs/quote_20200115.db'
    exchange = 'okexf'
    symbol = 'btc_usd-quarter'
    data = quote_fetch.get_all_depths(db_name, exchange, symbol)
    for i in data[:10]:
        print(i)


def test_get_hfd():
    # exchange = 'okexf'
    # symbol = 'btc_usd-quarter'
    exchange = 'ctp'
    symbol = 'FG105'
    begin_time = '2021-02-03 09:00:00'
    end_time = '2021-02-03 09:03:00'
    begin_timestamp = int(convert.to_timestamp(begin_time))
    end_timestamp = int(convert.to_timestamp(end_time))
    db = save_mongo.get_db()
    type_list = []
    type_list.append(config.HFT_TICKER)
    # type_list.append(config.HFT_DEPTH)
    data = quote_fetch.get_hfd(db, exchange, symbol, type_list, begin_timestamp, end_timestamp)
    data = json.loads(data)
    for i in data:
        print(i)


def test_get_trade_dict_list():
    # exchange = 'okexf'
    # symbol = 'btc_usd-quarter'
    exchange = 'ctp'
    symbol = 'FG105'
    begin_time = '2021-02-03 09:00:00'
    end_time = '2021-02-03 09:03:00'
    begin_timestamp = int(convert.to_timestamp(begin_time))
    end_timestamp = int(convert.to_timestamp(end_time))
    db = save_mongo.get_db()
    data = quote_fetch.get_trade_dict_list(db, exchange, symbol, begin_timestamp, end_timestamp)
    data = json.loads(data)
    for i in data:
        print(i)


def test_get_sqlite_ticks_by_db():
    db_name = '../../../quote_20201230.db'
    # db_name = '../../../quote_20201229.db'
    exchange = 'ctp'
    symbol = 'fu2105'
    begin_time = '2020-12-20 09:00:00'
    end_time = '2020-12-30 23:59:59'
    data = quote_fetch.get_sqlite_ticks_by_db(db_name, exchange, symbol, begin_time, end_time)
    print(data[-3:])


def main():
    # test_get_all_ticks()
    # test_get_all_depths()
    test_get_hfd()
    # test_get_trade_dict_list()
    # test_get_sqlite_ticks_by_db()
    pass


if __name__ == '__main__':
    main()
