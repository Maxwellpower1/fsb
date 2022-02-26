# coding=utf-8

import re
import json
import time
import redis
import traceback

from tqsdk import TqApi

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.exchange_api.ctp import tq_api


def convert_symbol(symbol):
    pre_symbol = re.findall(r'[0-9]+|[a-zA-Z]+', symbol)[0]
    COLLECT_DICT = config.COLLECT_DICT
    ctp_ex_dict = COLLECT_DICT['ctp_ex_dict']

    for ex, symbol_list in ctp_ex_dict.items():
        if (pre_symbol in symbol_list):
            symbol = '{}.{}'.format(ex, symbol)
            break
    return symbol


def download(days, symbols=[], type_list=['tick', 'bar']):
    COLLECT_DICT = config.COLLECT_DICT
    begin_date = COLLECT_DICT['begin_date']
    end_date = COLLECT_DICT['end_date']
    if symbols == []:
        symbols = COLLECT_DICT['ctp_tq_symbols']
    days = int(days)
    begin_year, begin_month = begin_date.split('.')
    end_year, end_month = end_date.split('.')
    for symbol in symbols:
        exchange, symbol = convert_symbol(symbol).split('.')
        for type_ in type_list:
            if (days==0):
                for year in range(int(begin_year), int(end_year)+1):
                    for month in range(int(begin_month), int(end_month)+1):
                        tq_api.downloader(year, month, exchange, symbol, type_, days)
            else:
                year = 0
                month = 0
                tq_api.downloader(year, month, exchange, symbol, type_, days)


class ForwardTqSdk(object):

    def __init__(self, symbol_list, redis_host, redis_port, channel, lpush_record_mq):
        convert_symbol
        self.symbol_list = []
        for symbol in symbol_list:
            self.symbol_list.append(convert_symbol(symbol))
        self.redis_host = redis_host
        self.redis_port = redis_port
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
        self.r = redis.StrictRedis(connection_pool=pool)
        self.exchange = 'ctp'
        self.channel = channel
        self.kline_name_dict = {}
        self.lpush_record_mq = lpush_record_mq
        self.event_type_k = 'kline'

    def send_event(self, key_name, data, event_dict):
        event_dict = json.dumps(event_dict)
        self.r[key_name] = str(data)
        self.r.publish(self.channel, event_dict)
        self.r.publish(key_name, event_dict)
        self.r.lpush(self.lpush_record_mq, event_dict)

    def send_kline(self, symbol, kline_list):
        key_name = '{}_{}_{}'.format(self.exchange, symbol, self.event_type_k)
        event_dict = {}
        event_dict['key_name'] = key_name
        event_dict['event_type'] = self.event_type_k
        event_dict['exchange'] = self.exchange
        event_dict['symbol'] = symbol
        event_dict['data'] = json.dumps(kline_list)
        self.send_event(key_name, kline_list, event_dict)

    def start(self):
        api = TqApi()
        for symbol in self.symbol_list:
            self.kline_name_dict[symbol.split('.')[1]] = api.get_kline_serial(symbol, 60)
            print('sub: {}'.format(symbol))
        while True:
            api.wait_update()
            for symbol in self.kline_name_dict.keys():
                klines = self.kline_name_dict[symbol]
                # set and pub not the same logic
                if api.is_changing(klines.iloc[-1], "datetime"):
                    kline_list = []
                    for i in range(len(klines)):
                        kline = [int(klines.loc[i, "datetime"]/1e6), klines.loc[i, "open"], klines.loc[i, "high"], klines.loc[i, "low"], klines.loc[i, "close"], klines.loc[i, "volume"], klines.loc[i, "close_oi"]-klines.loc[i, "open_oi"]]
                        kline_list.append(kline)
                    self.send_kline(symbol, kline_list)


def main():
    COLLECT_DICT = config.COLLECT_DICT
    symbol_list = COLLECT_DICT['ctp_md_symbols']
    redis_host = config.REDIS_HOST
    redis_port = config.REDIS_PORT
    channel = COLLECT_DICT['channel']
    lpush_record_mq = COLLECT_DICT['lpush_record_mq']

    forward_tqsdk = ForwardTqSdk(symbol_list, redis_host, redis_port, channel, lpush_record_mq)
    forward_tqsdk.start()
