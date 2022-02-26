# coding=utf-8

import os
import sys
import time
import json
import redis
import gevent
import datetime
from multiprocessing import Process
from gevent import monkey; monkey.patch_all()

from dao_quote.settings import config
from dao_quote.collect import get_quote
from dao_quote.util.quote_save import quote_save


COLLECT_DICT = config.COLLECT_DICT
CHANNEL = COLLECT_DICT['channel']
LPUSH_RECORD_MQ = COLLECT_DICT['lpush_record_mq']
EXCHANGE_DICT = COLLECT_DICT['exchange_dict']
IMPORTANT_KEY_NAME_LIST = COLLECT_DICT['important_key_name_list']
TYPE_LIST = COLLECT_DICT['type_list']
EXCHANGE_DICT = COLLECT_DICT['exchange_dict']


def set_one_type_symbol(exchange, symbol, type):
    global pool
    global kline_dict

    if (type == 'ticker'):
        data = get_quote.get_ticker(exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            send_event_dict(exchange, symbol, type, data)
        else:
            pass
    elif (type == 'kline'):
        data = get_quote.get_bar(exchange, symbol)
        if (data != {}):
            key_name = set_event_dict(exchange, symbol, type, data)
            kline_time = float(data[-1][0])
            try:
                if (kline_dict[key_name] < kline_time):
                    kline_dict[key_name] = kline_time
                    send_event_dict(exchange, symbol, type, data)
            except Exception as e:
                kline_dict[key_name] = kline_time
                send_event_dict(exchange, symbol, type, data)
        else:
            pass
    elif (type == 'depth'):
        data = get_quote.get_depth(exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            send_event_dict(exchange, symbol, type, data)
        else:
            pass
    else:
        data = {}
    del data
    return None


def set_event_dict(exchange, symbol, type, data):
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    r = redis.StrictRedis(connection_pool=pool)
    r[key_name] = str(data)
    return key_name


def send_event_dict(exchange, symbol, type, data):
    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    r = redis.StrictRedis(connection_pool=pool)
    event_type = type
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['key_name'] = key_name
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    event_dict = json.dumps(event_dict)
    r.publish(key_name, event_dict)
    r.publish(CHANNEL, event_dict)
    r[key_name] = str(data)
    r.lpush(LPUSH_RECORD_MQ, event_dict)
    return key_name


def gevent_collect_process(key_name_type):
    global pool
    global kline_dict

    kline_dict = {}
    exchange_dict = EXCHANGE_DICT
    important_key_name_list = IMPORTANT_KEY_NAME_LIST
    type_list = TYPE_LIST
    redis_host = config.REDIS_HOST
    redis_port = config.REDIS_PORT

    pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
    important_param_list = []
    usual_param_list = []
    for exchange in exchange_dict:
        symbol_list = exchange_dict[exchange]
        for symbol in symbol_list:
            for type in type_list:
                key_name = '{}_{}_{}'.format(exchange, symbol, type)
                key_name = key_name.lower()
                param = (exchange, symbol, type)
                if (key_name in important_key_name_list):
                    important_param_list.append(param)
                else:
                    usual_param_list.append(param)
    if (key_name_type == 'important'):
        single_gevent(important_param_list)
    elif (key_name_type == 'usual'):
        single_gevent(usual_param_list)


def single_gevent(param_list):
    while True:
        task_list = []
        for param in param_list:
            task_list.append(gevent.spawn(set_one_type_symbol, *param))
        gevent.joinall(task_list)
        time.sleep(0.3)
        del task_list


def set_pool(pool_):
    global pool
    pool = pool_


def gevent_start_collect(key_name_type):
    try:
        gevent_collect_process(key_name_type)
    except (KeyboardInterrupt):
        filename = 'collect, type: {}'.format(key_name_type)
        print(' Stop {} !'.format(filename))


def gevent_start():
    key_name_type = 'important'
    p1 = Process(target=gevent_start_collect, args=(key_name_type, ))
    p1.start()
    key_name_type = 'usual'
    p2 = Process(target=gevent_start_collect, args=(key_name_type, ))
    p2.start()
    process_dict_list = [
        {'name': 'gevent_start_collect_im', 'process': p1, 'pid': p1.pid},
        {'name': 'gevent_start_collect_us', 'process': p2, 'pid': p2.pid},
    ]
    print(('quote_im: {}, quote_us: {}').format(p1.pid, p2.pid))
    gevent_simple_process_monitor(process_dict_list)


def gevent_simple_process_monitor(process_dict_list):
    counter = 1
    while True:
        if (counter > 710):
            if (20 < time.time()%60 < 40):
                counter = 1
                for process_dict in process_dict_list:
                    if ('gevent_start_collect' in process_dict['name']):
                        os.system('kill {}'.format(process_dict['pid']))
        for process_dict in process_dict_list:
            process = process_dict['process']
            if (process.is_alive() is False):
                name = process_dict['name']
                if (name == 'gevent_start_collect_im'):
                    key_name_type = 'important'
                    p1 = Process(target=gevent_start_collect, args=(key_name_type, ))
                    p1.start()
                    process_dict['process'] = p1
                    process_dict['pid'] = p1.pid
                    print('{}, name: {}, new_pid: {}'.format(
                          datetime.datetime.now(), name, p1.pid))
                elif (name == 'gevent_start_collect_us'):
                    key_name_type = 'usual'
                    p2 = Process(target=gevent_start_collect, args=(key_name_type, ))
                    p2.start()
                    process_dict['process'] = p2
                    process_dict['pid'] = p2.pid
                    print('{}, name: {}, new_pid: {}'.format(
                          datetime.datetime.now(), name, p2.pid))
        time.sleep(5)
        counter += 1
