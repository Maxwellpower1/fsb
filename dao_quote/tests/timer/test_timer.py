# !/usr/bin/env python
# coding=utf-8

import time
import json
import redis
import pathmagic
from multiprocessing import Process
from dao_quote.timer import timer
from dao_quote.settings import config_collect



def test_listen_timer():
    timer_period_list = config_collect.TIMER_PERIOD_LIST
    timer_period_list = [3, 60]

    redis_host = config_collect.REDIS_HOST
    pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    p = r.pubsub()
    for period in timer_period_list:
        key_name = 'dao_timer_{}s'.format(period)
        p.subscribe(key_name)
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
            if event_type == 'timer':
                print(key_name, data)


def test_timer():
    p1 = Process(target=timer.main(), args=())
    p2 = Process(target=test_listen_timer, args=())
    p1.start()
    p2.start()
    print('running...')


def main():
    # test_timer()
    test_listen_timer()


if __name__ == '__main__':
    main()
