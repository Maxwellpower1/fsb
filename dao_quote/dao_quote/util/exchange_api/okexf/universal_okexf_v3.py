# coding=utf-8

import time

from dao_quote.util.exchange_api.okexf import api_okf_v3 as api_okf


async def async_ticker(symbol):
    try:
        data = await api_okf.async_ticker(symbol)
        data['ask'] = data['best_ask']
        data['bid'] = data['best_bid']
        data['high'] = data['high_24h']
        data['low'] = data['low_24h']
        data['vol'] = data['volume_24h']
        del data['best_ask']
        del data['best_bid']
        del data['high_24h']
        del data['low_24h']
        del data['volume_24h']
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    try:
        type = '1min'
        size = 300
        since = ''
        data = await api_okf.async_kline(symbol, type, size, since)
    except Exception as e:
        data = {}
    return data


async def async_depth(symbol):
    try:
        size = 9
        data = await api_okf.async_depth(symbol, size)
        data['asks'].reverse()
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    try:
        data = api_okf.ticker(symbol)
        data['ask'] = data['best_ask']
        data['bid'] = data['best_bid']
        data['high'] = data['high_24h']
        data['low'] = data['low_24h']
        data['vol'] = data['volume_24h']
        del data['best_ask']
        del data['best_bid']
        del data['high_24h']
        del data['low_24h']
        del data['volume_24h']
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    period = '1min'
    num = 300
    data = bars(symbol, period, num)
    return data


def bars(symbol, period, num=''):
    try:
        type = period
        size = num
        since = ''
        data = api_okf.kline(symbol, type, size, since)
    except Exception as e:
        data = {}
    return data


def depth(symbol):
    try:
        size = 9
        data = api_okf.depth(symbol, size)
        data['asks'].reverse()
    except Exception as e:
        data = {}
    return data
