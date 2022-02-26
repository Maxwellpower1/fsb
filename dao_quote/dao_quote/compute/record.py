# coding=utf-8

import sys
import time
import json
import redis
import sqlite3
import traceback

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.quote_save import quote_save


def quote_listen():
    COMPUTE_DICT = config.COMPUTE_DICT
    channel = COMPUTE_DICT['channel']
    period_list = COMPUTE_DICT['period_list']

    bars_list = []
    bars_period_dict = {}
    for period in period_list:
        if ('min' in period):
            bars = int(period.split('min')[0])
        elif ('hour' in period):
            bars = int(period.split('hour')[0]) * 60
        bars_list.append(bars)
        bars_period_dict[bars] = period

    db_name = quote_save.get_db_name()
    conn = quote_save.get_db_conn(db_name)
    counter = 1

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
            if event_type == 'ticker':
                key_name = event_dict['key_name']
                data = json.loads(event_dict['data'])
                quote_save.save_tick(conn, key_name, data)
                del data
            elif event_type == 'depth':
                key_name = event_dict['key_name']
                data = json.loads(event_dict['data'])
                quote_save.save_depth(conn, key_name, data)
                del data
            else:
               pass
            if (counter > 1000):
                counter = 1
            del event_dict


def wss_record():
    COMPUTE_DICT = config.COMPUTE_DICT
    lpush_record_mq = COMPUTE_DICT['lpush_record_mq']
    host = config.REDIS_HOST
    port = config.REDIS_PORT
    pool = redis.ConnectionPool(host=host, port=port, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    db_name = quote_save.get_db_name()
    conn = quote_save.get_db_conn(db_name)

    db_name = 'dao_quote.db'
    conn_bar = quote_save.get_db_conn(db_name)

    init_ts = time.time() * 1000
    ts = init_ts
    connect_counter = 1
    try:
        while True:
            try:
                value = r.brpop(lpush_record_mq)
                value = value[1].decode('utf-8')
                event_dict = json.loads(value)
                event_type = event_dict['event_type']
                key_name = event_dict['key_name']
                data = json.loads(event_dict['data'])
                if event_type == 'ticker':
                    ts = data['ts']
                    quote_save.save_tick(conn, key_name, data)
                elif event_type == 'depth':
                    ts = data['ts']
                    quote_save.save_depth(conn, key_name, data)
                elif event_type == 'depthall':
                    ts = data['ts']
                    quote_save.save_depthall(conn, key_name, data)
                elif event_type == 'trade':
                    ts = data['ts']
                    quote_save.save_trade(conn, key_name, data)
                elif event_type == 'kline':
                    quote_save.save_bar(conn_bar, key_name, data)
                del data
                if (connect_counter > 100000 or (ts-init_ts > 3000)):
                    init_ts = ts
                    conn.commit()
                    db_name_new = quote_save.get_db_name()
                    if (db_name_new != db_name):
                        db_name = db_name_new
                        conn = quote_save.get_db_conn(db_name)
                    connect_counter = 1
                else:
                    connect_counter += 1
            except KeyboardInterrupt:
                conn.commit()
                print('press ctrl+c')
                sys.exit()
            except Exception as e:
                conn.commit()
                exception_msg = traceback.format_exc()
                print('record err: {}'.format(exception_msg))
    except:
        conn.commit()
        print('conn commit')
        sys.exit()


def main():
    wss_record()
