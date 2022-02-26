# coding=utf-8

import time

from dao_quote.util.exchange_api.okex import api_ok_v5 as api_ok


async def async_ticker(symbol):
    tk_data = {}
    try:
        data = await api_ok.async_ticker(symbol)
        tk_data['ask'] = float(data['askPx'])
        tk_data['a_v'] = float(data['askSz'])
        tk_data['bid'] = float(data['bidPx'])
        tk_data['b_v'] = float(data['bidSz'])
        tk_data['last'] = float(data['last'])
        tk_data['open'] = float(data['open24h'])
        tk_data['high'] = float(data['high24h'])
        tk_data['low'] = float(data['low24h'])
        tk_data['vol'] = float(data['vol24h'])
        tk_data['amt'] = float(data['volCcy24h'])
        tk_data['ts'] = int(data['ts'])
    except Exception as e:
        pass
    return tk_data


async def async_bar(symbol):
    try:
        type = '1min'
        size = '300'
        since = ''
        data = await api_ok.async_kline(symbol, type, size, since)
    except Exception as e:
        print(e)
        data = {}
    return data


async def async_depth(symbol):
    try:
        size = 400
        data = await api_ok.async_depth(symbol, size)
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    tk_data = {}
    try:
        data = api_ok.ticker(symbol)
        tk_data['ask'] = float(data['askPx'])
        tk_data['a_v'] = float(data['askSz'])
        tk_data['bid'] = float(data['bidPx'])
        tk_data['b_v'] = float(data['bidSz'])
        tk_data['last'] = float(data['last'])
        tk_data['open'] = float(data['open24h'])
        tk_data['high'] = float(data['high24h'])
        tk_data['low'] = float(data['low24h'])
        tk_data['vol'] = float(data['vol24h'])
        tk_data['amt'] = float(data['volCcy24h'])
        tk_data['ts'] = int(data['ts'])
    except Exception as e:
        pass
    return tk_data


def bar(symbol):
    try:
        type = '1min'
        size = '300'
        since = ''
        data = api_ok.kline(symbol, type, size, since)
    except Exception as e:
        data = {}
    return data


def depth(symbol):
    try:
        size = 400
        data = api_ok.depth(symbol, size)
    except Exception as e:
        data = {}
    return data
