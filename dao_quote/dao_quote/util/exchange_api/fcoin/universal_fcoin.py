# coding=utf-8

import time

from dao_quote.util.exchange_api.fcoin import api_fc


async def async_ticker(symbol):
    try:
        data = await api_fc.async_ticker(symbol)
        data = data['data']['ticker']
        tick_dict = {}
        tick_dict['last'] = data[0]
        tick_dict['high'] = data[7]
        tick_dict['low'] = data[8]
        tick_dict['vol'] = data[10]
        tick_dict['ask'] = data[4]
        tick_dict['bid'] = data[2]
        data = tick_dict
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    try:
        period = 'M1'
        data_ = await api_fc.async_kline(symbol, period)
        data_ = data_['data']
        data = [[i['id']*1000, i['open'], i['high'], i['low'],
                i['close'], i['quote_vol'], i['base_vol']] for i in data_]
        data.reverse()
        del data_
    except Exception as e:
        print(e)
        data = {}
    return data


async def async_depth(symbol):
    try:
        level = 'L20'
        data = await api_fc.async_depth(symbol, level)
        data = data['data']
        asks_ = data['asks']
        bids_ = data['bids']
        asks = []
        bids = []
        for i in range(0, len(asks_)):
            if (i % 2 == 0):
                asks.append([asks_[i], asks_[i+1]])
                bids.append([bids_[i], bids_[i+1]])
        asks.reverse()
        data['asks'] = asks
        data['bids'] = bids
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    try:
        data = api_fc.ticker(symbol)
        data = data['data']['ticker']
        tick_dict = {}
        tick_dict['last'] = data[0]
        tick_dict['high'] = data[7]
        tick_dict['low'] = data[8]
        tick_dict['vol'] = data[10]
        tick_dict['ask'] = data[4]
        tick_dict['bid'] = data[2]
        data = tick_dict
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    try:
        period = 'M1'
        data_ = api_fc.kline(symbol, period)
        data_ = data_['data']
        data = [[i['id']*1000, i['open'], i['high'], i['low'],
                i['close'], i['quote_vol'], i['base_vol']] for i in data_]
        data.reverse()
        del data_
    except Exception as e:
        print(e)
        data = {}
    return data


def depth(symbol):
    try:
        level = 'L20'
        data = api_fc.depth(symbol, level)
        data = data['data']
        asks_ = data['asks']
        bids_ = data['bids']
        asks = []
        bids = []
        for i in range(0, len(asks_)):
            if (i % 2 == 0):
                asks.append([asks_[i], asks_[i+1]])
                bids.append([bids_[i], bids_[i+1]])
        asks.reverse()
        data['asks'] = asks
        data['bids'] = bids
    except Exception as e:
        data = {}
    return data
