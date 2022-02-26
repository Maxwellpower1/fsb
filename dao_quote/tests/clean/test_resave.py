#coding=utf-8

import pprint
import pathmagic
from dao_quote.clean import resave
from dao_quote.settings import config_collect
from dao_quote.util.quote_save import save_mongo


def test_key_name_dict_list():
    key_name_dict_list = resave.get_key_name_dict_list()
    print(key_name_dict_list)
    type_list = config_collect.WSS_TYPE_LIST
    for key_name_dict in key_name_dict_list:
        exchange = key_name_dict['exchange']
        symbol = key_name_dict['symbol']
        for type_ in type_list:
            key_name = '{}_{}_{}'.format(exchange, symbol, type_)
            print(key_name)


def test_resave():
    begin_time = '2020-01-15 00:00:00'
    end_time = '2020-01-15 02:59:59'
    rst = resave.resave(begin_time, end_time)
    print(rst)


def test_resave_one_symbol():
    db = save_mongo.get_db()
    key_name_dict = {}
    key_name_dict['exchange'] = 'okexf'
    key_name_dict['symbol'] = 'btc_usd-quarter'
    begin_time = '2020-01-14 00:00:00'
    end_time = '2020-01-15 00:58:59'
    resave.resave_one_symbol(db, key_name_dict, begin_time, end_time)


def test_split_db():
    db_name = 'quote_20200229.db'
    seconds = 60 * 60
    db_time_list = resave.split_db(db_name, seconds)
    pprint.pprint(db_time_list)


def main():
    test_key_name_dict_list()
    # test_resave()
    # test_resave_one_symbol()
    # test_split_db()


if __name__ == '__main__':
    main()
