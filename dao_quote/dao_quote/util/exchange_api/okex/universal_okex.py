# coding=utf-8

import time

from dao_quote.util.exchange_api.okex import api_ok


async def async_ticker(symbol):
    try:
        data = await api_ok.async_ticker(symbol)
        data = data['ticker']
        data['ask'] = data['sell']
        data['bid'] = data['buy']
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    try:
        type = '1min'
        size = '500'
        since = ''
        data = await api_ok.async_kline(symbol, type, size, since)
        data = [list(map(float, bar)) for bar in data]
    except Exception as e:
        print(e)
        data = {}
    return data


async def async_depth(symbol):
    try:
        size = 9
        data = await api_ok.async_depth(symbol, size)
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    try:
        data = api_ok.ticker(symbol)
        data = data['ticker']
        data['ask'] = data['sell']
        data['bid'] = data['buy']
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    try:
        type = '1min'
        size = '500'
        since = ''
        data = api_ok.kline(symbol, type, size, since)
        data = [list(map(float, bar)) for bar in data]
    except Exception as e:
        data = {}
    return data


def depth(symbol):
    try:
        size = 9
        data = api_ok.depth(symbol, size)
    except Exception as e:
        data = {}
    return data
