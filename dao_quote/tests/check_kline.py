# !/usr/bin/env python
# coding=utf-8

import os
import sys
import time
import sqlite3
import optparse


def shift_time(timestamp):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(timestamp)
    return time.strftime(format, value)


def query_table_bar(conn, key_name):
    c = conn.cursor()
    s = c.execute(('''SELECT * FROM "{}" order by timestamp''').format(key_name))
    return s


def check_kline(key_name, days):
    end_time = int(time.time())
    begin_time = end_time - 60*60*24*float(days)

    begin_time = int(begin_time) * 1000
    end_time = int(end_time) * 1000
    conn_a = sqlite3.connect('../dao_quote.db', timeout=21)
    c = conn_a.cursor()
    s = c.execute(('''SELECT name FROM sqlite_master WHERE type='table' and name like '%kline%' ORDER BY name;'''))
    for i in s:
        key_name_ = i[0]
        if (key_name_ == key_name):
            print('checking: {}'.format(key_name))
            klines = query_table_bar(conn_a, key_name)
            timestamp_prev = 0
            for kline in klines:
                timestamp = kline[0]
                if (len(str(timestamp)) == 13):
                    timestamp = timestamp / 1000
                print(shift_time(timestamp), kline)
                # if ((timestamp_prev+60 != timestamp) and
                #    (timestamp_prev != 0)):
                #     print(timestamp_prev)
                #     print(timestamp)
                #     print(shift_time(timestamp_prev))
                #     print(shift_time(timestamp))
                # else:
                #     pass
                # timestamp_prev = timestamp
                # print(shift_time(timestamp))
    pass


def main():
    parser = optparse.OptionParser()
    parser.add_option("-e", "--exchange", dest="exchange",
                      help="okexf/okex/huobi")
    parser.add_option("-s", "--symbol", dest="symbol",
                      help="btc_usdt/btc_usd-quarter")
    parser.add_option("-p", "--period", dest="period",
                      help="3min/15min")
    parser.add_option("-d", "--days", dest="days",
                      help="1/3")
    (options, args) = parser.parse_args()
    try:
        exchange = options.exchange
        symbol = options.symbol
        period = options.period
        days = options.days
        if (period != '1min'):
            key_name = '{}_{}_kline.{}'.format(exchange, symbol, period)
        elif (period == '1min'):
            key_name = '{}_{}_kline'.format(exchange, symbol)
        check_kline(key_name, days)
    except Exception as e:
        # raise
        filename = os.path.basename(__file__)
        print('need set param, such as:')
        print('python {} -e {} -s {} -p {} -d {}'.format(filename,
              'okex', 'btc_usdt', '15min', '1'))


if __name__ == '__main__':
    main()
