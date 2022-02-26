# coding=utf-8

import time

from dao_quote.util.exchange_api.okex import api_ok_v3 as api_ok


async def async_ticker(symbol):
    try:
        data = await api_ok.async_ticker(symbol)
        del data['best_ask']
        del data['best_bid']
        del data['instrument_id']
        del data['product_id']
        del data['last_qty']
        del data['best_ask_size']
        del data['best_bid_size']
        del data['open_24h']
        del data['timestamp']
        data['last'] = float(data['last'])
        data['ask'] = float(data['ask'])
        data['bid'] = float(data['bid'])
        data['high'] = float(data['high_24h'])
        data['low'] = float(data['low_24h'])
        data['vol'] = float(data['base_volume_24h'])
        del data['high_24h']
        del data['low_24h']
        del data['base_volume_24h']
        del data['quote_volume_24h']
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    try:
        type = '1min'
        size = '500'
        since = ''
        data = await api_ok.async_kline(symbol, type, size, since)
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
        del data['best_ask']
        del data['best_bid']
        del data['instrument_id']
        del data['product_id']
        del data['last_qty']
        del data['best_ask_size']
        del data['best_bid_size']
        del data['open_24h']
        del data['timestamp']
        data['last'] = float(data['last'])
        data['ask'] = float(data['ask'])
        data['bid'] = float(data['bid'])
        data['high'] = float(data['high_24h'])
        data['low'] = float(data['low_24h'])
        data['vol'] = float(data['base_volume_24h'])
        del data['high_24h']
        del data['low_24h']
        del data['base_volume_24h']
        del data['quote_volume_24h']
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    try:
        type = '1min'
        size = '500'
        since = ''
        data = api_ok.kline(symbol, type, size, since)
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
