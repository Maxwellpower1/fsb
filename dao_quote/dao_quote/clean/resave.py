#coding=utf-8

import datetime
import traceback

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.quote_fetch import quote_fetch
from dao_quote.util.quote_save import (quote_save, save_mongo)


def get_key_name_dict_list():
    RESAVE_DICT = config.RESAVE_DICT
    exchange_dict = RESAVE_DICT['hfd_exchange_dict']
    type_list = RESAVE_DICT['wss_type_list']
    key_name_dict_list = []
    for exchange in exchange_dict:
        symbol_list = exchange_dict[exchange]
        for symbol in symbol_list:
            key_name_dict = {}
            key_name_dict['exchange'] = exchange
            key_name_dict['symbol'] = symbol
            key_name_dict_list.append(key_name_dict)
    return key_name_dict_list


def resave(db_name):
    db = save_mongo.get_db()
    key_name_dict_list = get_key_name_dict_list()
    seconds = 60 * 10
    if ('.csv' in db_name):
        resave_csv(db_name)
    else:
        db_time_list = split_db(db_name, seconds)
        for key_name_dict in key_name_dict_list:
            exchange = key_name_dict['exchange']
            symbol = key_name_dict['symbol']

            for i in range(0, len(db_time_list)-1):
                begin_time = db_time_list[i]
                end_time = db_time_list[i+1]
                print('[*] {} resaving, {}-{}, {}--{}'.format(datetime.datetime.now(),
                      exchange, symbol, begin_time, end_time))
                resave_one_symbol(db, db_name, exchange, symbol, begin_time, end_time)
            # create index
            conn = quote_save.get_db_conn(db_name)
            key_name = '{}_{}_hfd'.format(exchange, symbol)
            index_dict = {'ts': 1}
            print('[*] {} creating index, {}'.format(
                  datetime.datetime.now(), key_name))
            quote_save.create_index(conn, key_name, index_dict)

    return True


def resave_one_symbol(db, db_name, exchange, symbol, begin_time, end_time):
    collection = '{}_{}_hfd'.format(exchange, symbol)
    collection_ins = db[collection]
    tick_dict_list = quote_fetch.get_sqlite_ticks_by_db(db_name, exchange, symbol, begin_time, end_time)

    if (exchange == 'ctp'):
        rst = save_mongo_db(collection_ins, tick_dict_list)
        del tick_dict_list
    else:
        depth_dict_list = quote_fetch.get_sqlite_depths_by_db(db_name, exchange, symbol, begin_time, end_time)
        # try:
        #     print(datetime.datetime.now(), tick_dict_list[-1], depth_dict_list[-1])
        # except Exception as e:
        #     print(datetime.datetime.now(), e)

        collection_dict_list_1 = combine_two_list(tick_dict_list, depth_dict_list)

        depthall_dict_list = quote_fetch.get_sqlite_depthalls_by_db(db_name, exchange, symbol, begin_time, end_time)
        trade_dict_list = quote_fetch.get_sqlite_trades_by_db(db_name, exchange, symbol, begin_time, end_time)
        # try:
        #     print(datetime.datetime.now(), depthall_dict_list[-1], trade_dict_list[-1])
        # except Exception as e:
        #     print(datetime.datetime.now(), e)
        collection_dict_list_2 = combine_two_list(depthall_dict_list, trade_dict_list)

        collection_dict_list = combine_two_list(collection_dict_list_1, collection_dict_list_2)

        rst = save_mongo_db(collection_ins, collection_dict_list)
        del tick_dict_list
        del depth_dict_list
        del collection_dict_list_1
        del depthall_dict_list
        del trade_dict_list
        del collection_dict_list_2
    return True


def resave_csv(db_name):
    exchange = 'ctp'
    symbol = db_name.split('_')[1]
    db = save_mongo.get_db()
    collection = '{}_{}_hfd'.format(exchange, symbol)
    collection_ins = db[collection]
    print('[*] resaving, {}'.format(db_name))
    tick_dict_list = quote_fetch.get_csv_ticks(db_name)
    rst = save_mongo_db(collection_ins, tick_dict_list)
    index_dict = {'ts': 1}
    rst = save_mongo.create_index(db, collection, index_dict)
    return True


def save_mongo_db(collection_ins, data_dict_list):
    try:
        collection_ins.insert_many(data_dict_list)
    except Exception as e:
        # print(e)
        for data_dict in data_dict_list:
            collection_ins.save(data_dict)
    return True


def split_db(db_name, seconds):
    # split_db by perids of times, such as 300s
    # 1 day have 60 * 60 * 24 = 86400
    one_day_ts = 86400
    db_date = db_name.split('_')[1].split('.')[0]
    db_timestamp = convert.to_timestamp_date(db_date)
    db_time_list = []
    begin_timestamp = int(db_timestamp-one_day_ts*0.25)
    end_timestamp = int(db_timestamp+one_day_ts*1.25)
    for i in range(begin_timestamp, end_timestamp, seconds):
        time_date = convert.shift_time(i)
        db_time_list.append(time_date)
    return db_time_list


def combine_two_list(list_1, list_2):
    collection_dict_list = []
    len_list_1 = len(list_1)
    len_list_2 = len(list_2)
    if ((len_list_1 == 0) and (len_list_2 == 0)):
        return []
    elif ((len_list_1 == 0) and (len_list_2 > 0)):
        return list_2
    elif ((len_list_1 > 0) and (len_list_2 == 0)):
        return list_1
    elif ((len_list_1 > 0) and (len_list_2 > 0)):
        while True:
            try:
                ts_1 = list_1[0]['ts']
                ts_2 = list_2[0]['ts']
                if (ts_1 < ts_2):
                    collection_dict_list.append(list_1[0])
                    list_1 = list_1[1:]
                else:
                    collection_dict_list.append(list_2[0])
                    list_2 = list_2[1:]
            except Exception as e:
                if (len(list_1) > len(list_2)):
                    collection_dict_list += list_1
                else:
                    collection_dict_list += list_2
                break
    return collection_dict_list


def create_index():
    db = save_mongo.get_db()
    index_name = 'ts'
    key_name_dict_list = get_key_name_dict_list()
    for key_name_dict in key_name_dict_list:
        exchange = key_name_dict['exchange']
        symbol = key_name_dict['symbol']
        collection = '{}_{}_hfd'.format(exchange, symbol)
        rst = save_mongo.create_index(db, collection, index_name)
        print('[*] {}, {}'.format(collection, rst))
