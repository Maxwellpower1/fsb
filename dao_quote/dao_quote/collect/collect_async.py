# coding=utf-8

import os
import sys
import time
import json
import redis
import asyncio
from multiprocessing import Process

from dao_quote.settings import config
from dao_quote.collect import get_quote
from dao_quote.util.quote_save import quote_save
from dao_quote.settings import config_collect


def set_pool(pool_):
    global pool
    pool = pool_


async def async_set_one_type_symbol(exchange, symbol, type):
    global pool
    global kline_dict

    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    key_name = key_name.lower()
    channel = 'quote'
    event_type = type
    event_dict = {}
    event_dict['key_name'] = key_name
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    r = redis.StrictRedis(connection_pool=pool)

    if (type == 'ticker'):
        data = await get_quote.get_async_ticker(exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            r[key_name] = str(data)
            event_dict['data'] = json.dumps(data)
            event_dict = json.dumps(event_dict)
            r.publish(channel, event_dict)
            r.publish(key_name, event_dict)
        else:
            pass
    elif (type == 'kline'):
        data = await get_quote.get_async_bar(exchange, symbol)
        if (data != {}):
            r[key_name] = str(data)
            kline_time = float(data[-1][0])
            try:
                if (kline_dict.get(key_name, 0) < kline_time):
                    event_dict['data'] = json.dumps(data)
                    event_dict = json.dumps(event_dict)
                    r.publish(channel, event_dict)
                    r.publish(key_name, event_dict)
                    kline_dict[key_name] = kline_time
                else:
                    pass
            except Exception as e:
                kline_dict[key_name] = kline_time
        else:
            pass
    elif (type == 'depth'):
        data = await get_quote.get_async_depth(exchange, symbol)
        if (data != {}):
            timestamp = time.time() * 1000
            data['ts'] = timestamp
            r[key_name] = str(data)
            event_dict['data'] = json.dumps(data)
            event_dict = json.dumps(event_dict)
            r.publish(channel, event_dict)
            r.publish(key_name, event_dict)
        else:
            pass
    del event_dict
    del data
    return None


def async_collect_process():
    global pool
    global kline_dict

    kline_dict = {}
    COLLECT_DICT = config.COLLECT_DICT
    exchange_dict = COLLECT_DICT['exchange_dict']
    type_list = COLLECT_DICT['type_list']
    redis_host = config.REDIS_HOST
    redis_port = config.REDIS_PORT
    pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
    while True:
        task_list = []
        for exchange in exchange_dict:
            symbol_list = exchange_dict[exchange]
            for symbol in symbol_list:
                for type in type_list:
                    task_list.append(async_set_one_type_symbol(exchange, symbol, type))
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.gather(*task_list))
        loop.close()
        time.sleep(0.3)
        # print(time.time())
        pass


def async_start_collect():
    async_collect_process()


def async_start():
    p1 = Process(target=async_start_collect, args=())
    p1.start()
    process_dict_list = [
        {'name': 'async_start_collect', 'process': p1, 'pid': p1.pid}
    ]
    print('collect: {}'.format(p1.pid))
    async_process_monitor(process_dict_list)


def async_process_monitor(process_dict_list):
    counter = 1
    while True:
        if (counter > 710):
            if (20 < time.time()%60 < 40):
                counter = 1
                for process_dict in process_dict_list:
                    if (process_dict['name'] == 'async_start_collect'):
                        os.system('kill {}'.format(process_dict['pid']))
                    else:
                        pass
        for process_dict in process_dict_list:
            process = process_dict['process']
            if (process.is_alive() is False):
                name = process_dict['name']
                if (name == 'async_start_collect'):
                    p1 = Process(target=async_start_collect, args=())
                    p1.start()
                    process_dict['process'] = p1
                    process_dict['pid'] = p1.pid
                    print('name: {}, new_pid: {}'.format(
                          name, p1.pid))
        time.sleep(5)
