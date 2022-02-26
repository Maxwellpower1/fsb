# !/usr/bin/env python
# coding=utf-8

import csv
import time
import sqlite3
import datetime
import optparse


def create_table_bar(db_name, key_name):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  TIMESTAMP   INTEGER PRIMARY KEY NOT NULL,
                  OPEN        FLOAT    NOT NULL,
                  HIGH        FLOAT    NOT NULL,
                  LOW         FLOAT    NOT NULL,
                  CLOSE       FLOAT    NOT NULL,
                  VOLUME      FLOAT    NOT NULL,
                  VOLUME_COIN FLOAT    NOT NULL
                  );'''.format(key_name))
    conn.commit()
    conn.close()


def save_table_bar(db_name, key_name, data):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    # data.reverse()
    for i in data:
        if (len(i) < 7):
            volume_coin = 0
        else:
            volume_coin = i[6]
        try:
            c.execute(('REPLACE INTO "{}" (TIMESTAMP,OPEN,HIGH,LOW,'
                       'CLOSE,VOLUME,VOLUME_COIN) VALUES '
                       '({},{},{},{},{},{},{})').format(
                       key_name, i[0], i[1], i[2], i[3], i[4], i[5],
                       volume_coin))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                # break
                pass
            else:
                raise
    conn.commit()
    conn.close()


def save_bar(db_name, key_name, data):
    table_name = key_name
    try:
        save_table_bar(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_bar(db_name, table_name)
                save_table_bar(db_name, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def get_backtest_kline_db(conn, key_name, begin_timestamp, end_timestamp):
    c = conn.cursor()
    s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                   'timestamp<={} ORDER BY timestamp').format(
                   key_name, begin_timestamp, end_timestamp))
    # the result kline timestamp is ms
    data = []
    for k in s:
        data.append([k[0], k[1], k[2], k[3], k[4], k[5], k[6]])
    return data


def get_backtest_kline_db_all(conn, key_name):
    c = conn.cursor()
    s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp').format(key_name))
    # the result kline timestamp is ms
    data = []
    for k in s:
        data.append([k[0], k[1], k[2], k[3], k[4], k[5], k[6]])
    return data


def to_timestamp(time_date):
    format = '%Y-%m-%d'
    timearray = time.strptime(time_date, format)
    timestamp = str(int(time.mktime(timearray)))
    return timestamp


def to_ctp_timestamp(time_date):
    format = '%Y-%m-%d %H:%M:%S.%f'
    timestamp = int(datetime.datetime.strptime(time_date[:-3],
                format).timestamp())*1000
    return timestamp


def save_csv_ctp(filename):
    db_name = 'dao_quote.db'
    symbol = filename.split('_')[1]
    key_name = 'ctp_{}_kline'.format(symbol)

    data = []
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            if (reader.line_num > 1):
                row[0] = to_ctp_timestamp(row[0])
                row[1] = float(row[1])
                row[2] = float(row[2])
                row[3] = float(row[3])
                row[4] = float(row[4])
                row[5] = float(row[5])
                row[6] = float(row[7]) - float(row[6])
                data.append(row)
    save_bar(db_name, key_name, data)


def get_db(param):
    begin_time, end_time = param.split(' ')
    begin_timestamp = int(to_timestamp(begin_time)) * 1000
    end_timestamp = int(to_timestamp(end_time)) * 1000
    conn = sqlite3.connect('dao_quote.db', timeout=21)
    db_name = 'temp_quote.db'
    c = conn.cursor()
    s = c.execute(('''SELECT name FROM sqlite_master WHERE type='table' and name like '%kline%' ORDER BY name;'''))
    for i in s:
        key_name = i[0]
        print('geting: {}'.format(key_name))
        data = get_backtest_kline_db(conn, key_name, begin_timestamp, end_timestamp)
        print(len(data))
        save_bar(db_name, key_name, data)


def set_db(param):
    conn = sqlite3.connect('temp_quote.db', timeout=21)
    db_name = 'dao_quote.db'
    c = conn.cursor()
    s = c.execute(('''SELECT name FROM sqlite_master WHERE type='table' and name like '%kline%' ORDER BY name;'''))
    for i in s:
        key_name = i[0]
        print('setting: {}'.format(key_name))
        data = get_backtest_kline_db_all(conn, key_name)
        save_bar(db_name, key_name, data)


def get_hfd(param):
    from dao_quote.util.quote_save import quote_save
    from dao_quote.util.quote_fetch import quote_fetch
    from dao_quote.settings import config_collect

    exchange_dict = config_collect.HFD_EXCHANGE_DICT
    type_list = config_collect.WSS_TYPE_LIST
    source_db_name = param

    dest_db_name = '{}s.db'.format(source_db_name.split('.')[0])
    dest_conn = sqlite3.connect(dest_db_name, timeout=21)
    for exchange in exchange_dict:
        for symbol in exchange_dict[exchange]:
            for type_ in type_list:
                key_name = '{}_{}_{}'.format(exchange, symbol, type_)
                print('geting: {}'.format(key_name))
                if (type_ == 'ticker'):
                    tick_dict_list = quote_fetch.get_all_ticks(source_db_name, exchange, symbol)
                    for data in tick_dict_list:
                        quote_save.save_tick(dest_conn, key_name, data)
                    del tick_dict_list
                elif (type_ == 'depth'):
                    depth_dict_list = quote_fetch.get_all_depths(source_db_name, exchange, symbol)
                    for data in depth_dict_list:
                        quote_save.save_depth(dest_conn, key_name, data)
                    del depth_dict_list
                elif (type_ == 'depthall'):
                    depth_dict_list = quote_fetch.get_all_depthalls(source_db_name, exchange, symbol)
                    for data in depth_dict_list:
                        quote_save.save_depthall(dest_conn, key_name, data)
                    del depth_dict_list
                elif (type_ == 'trade'):
                    trade_dict_list = quote_fetch.get_all_trades(source_db_name, exchange, symbol)
                    for data in trade_dict_list:
                        quote_save.save_trade(dest_conn, key_name, data)
                    del trade_dict_list
                dest_conn.commit()
    pass


def set_hfd(param):
    from dao_quote.util.quote_save import quote_save
    pass


def main():
    '''
    timestamp careful of s ms
    '''
    parser = optparse.OptionParser()
    parser.add_option("-g", "--get", dest="get_db", help="get_db_data -g 'begin_time end_time'")
    parser.add_option("-f", "--hfd", dest="get_hfd", help="get_hfd -f db_name")
    parser.add_option("-s", "--set", dest="set_db", type='string', help="replace_db_data")
    parser.add_option("-c", "--ctp", dest="set_db_ctp", type='string', help="save_csv_ctp")

    (options, args) = parser.parse_args()

    if options.get_db != None:
        param = options.get_db
        get_db(param)

    if options.get_hfd != None:
        param = options.get_hfd
        get_hfd(param)

    if options.set_db != None:
        param = options.set_db
        set_db(param)

    if options.set_db_ctp != None:
        param = options.set_db_ctp
        save_csv_ctp(param)


if __name__ == '__main__':
    main()
