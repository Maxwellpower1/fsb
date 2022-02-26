# !/usr/bin/env python
# coding=utf-8

import time
import json
import redis
import datetime
import pathmagic

from dao_quote.settings import config_compute
from dao_quote.util.convert import convert


def test_listen_redis_one_symbol():
    channel = 'quote'
    redis_host = config_compute.REDIS_HOST
    BAR_KEY_NAME_LIST = config_compute.BAR_KEY_NAME_LIST
    pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    p.subscribe(channel)
    for item in p.listen():
        if item['type'] == 'message':
            event_dict = item['data']
            r.set('s', 32)
            event_dict = json.loads(event_dict)
            key_name = event_dict['key_name']
            event_type = event_dict['event_type']
            event_exchange = event_dict['exchange']
            event_symbol = event_dict['symbol']
            data = json.loads(event_dict['data'])
            if event_type in ['kline.1hour', 'kline.3min', 'kline.15min', 'kline.30min', 'kline']:
                print(key_name, data[-1])
            # if event_type in ['kline.1hour']:
                # if (key_name in BAR_KEY_NAME_LIST):
                if ((event_exchange == 'huobif' and event_symbol == 'btc_usd-quarter') or
                   (event_exchange == 'okexf' and event_symbol == 'eos_usd-quarter')):
                    timestamp = data[-1][0]/1000
                    time_now = convert.shift_time(timestamp)
                    print(datetime.datetime.now(), time_now, key_name)
                    print(data[-1])
                    print('*' * 50)


def main():
    test_listen_redis_one_symbol()


if __name__ == '__main__':
    main()
