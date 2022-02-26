# coding=utf-8

import time
import json
import redis
import sqlite3

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.quote_save import quote_save


def quote_listen():
    COMPUTE_DICT = config.COMPUTE_DICT
    channel = COMPUTE_DICT['channel']
    period_list = COMPUTE_DICT['period_list']
    bar_key_name_list = COMPUTE_DICT['bar_key_name_list']

    bars_list = []
    bars_period_dict = {}
    for period in period_list:
        if ('min' in period):
            bars = int(period.split('min')[0])
        elif ('hour' in period):
            bars = int(period.split('hour')[0]) * 60
        bars_list.append(bars)
        bars_period_dict[bars] = period

    db_name = 'dao_quote.db'
    conn_bar = quote_save.get_db_conn(db_name)

    host = config.REDIS_HOST
    port = config.REDIS_PORT
    pool = redis.ConnectionPool(host=host, port=port, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            event_type = event_dict['event_type']
            if event_type == 'kline':
                key_name = event_dict['key_name']
                data = json.loads(event_dict['data'])
                if (key_name in bar_key_name_list):
                    for bars in bars_list:
                        if (float(data[-1][0])/1000 % (60 * bars) == 0):
                            period = bars_period_dict[bars]
                            key_name_ = '{}.{}'.format(key_name, period)
                            event_type_ = '{}.{}'.format(event_type, period)
                            event_dict['event_type'] = event_type_
                            event_dict['key_name'] = key_name_

                            length = len(data)
                            klines = data[-bars*(int(length/bars)-1)-1:-1]
                            klines = convert.combine_lines(klines, bars)
                            klines.append(data[-1])
                            data_ = klines

                            quote_save.save_bar(conn_bar, key_name_, data_)
                            data_ = json.dumps(data_)
                            event_dict['data'] = data_
                            r.publish(key_name_, json.dumps(event_dict))
                            del klines
                            del data_
                        else:
                            pass
                else:
                    pass
                # quote_save.save_bar(conn_bar, key_name, data[-5:])
                quote_save.save_bar(conn_bar, key_name, data)
                del data
            else:
               pass
            del event_dict


def main():
    quote_listen()
