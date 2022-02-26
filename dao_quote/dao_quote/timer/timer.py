# coding=utf-8

import os
import time
import json
import redis
import datetime
from multiprocessing import Process

from dao_quote.settings import config_collect


def send_event_dict(type_, data):
    global pool

    key_name = 'dao_timer_{}s'.format(type_)

    r = redis.StrictRedis(connection_pool=pool)
    event_dict = {}
    event_dict['event_type'] = 'timer'
    event_dict['key_name'] = key_name
    event_dict['exchange'] = ''
    event_dict['symbol'] = ''
    event_dict['data'] = json.dumps(data)
    event_dict = json.dumps(event_dict)
    r.publish(key_name, event_dict)


def timer():
    global pool
    timer_period_list = config_collect.TIMER_PERIOD_LIST
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    data = {}
    last_second = 0
    while True:
        dt = datetime.datetime.now()
        second = dt.second
        if (second != last_second):
            last_second = second
            data['ts'] = dt.timestamp()
            data['time_now'] = str(dt).split('.')[0]
            for period in timer_period_list:
                if (second % period == 0):
                    send_event_dict(period, data)
        time.sleep(0.001)


def process_monitor(process_dict_list):
    for process_dict in process_dict_list:
        process = process_dict['process']
        if (process.is_alive() is False):
            name = process_dict['name']
            if (name == 'timer'):
                p1 = Process(target=timer, args=())
                p1.start()
                process_dict['process'] = p1
                process_dict['pid'] = p1.pid
                print('{}, name: {}, new_pid: {}'.format(
                      datetime.datetime.now(), name, p1.pid))
    time.sleep(5)


def main():
    process_dict_list = []
    p1 = Process(target=timer, args=())
    p1.start()
    process_dict = {'name': 'timer', 'process': p1, 'pid': p1.pid}
    process_dict_list.append(process_dict)
    process_monitor(process_dict_list)
