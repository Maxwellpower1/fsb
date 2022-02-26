# coding=utf-8

import time

from dao_quote.util.exchange_api.huobi import api_hb


async def async_ticker(symbol):
    '''convert btc_usdt to btcusdt
    '''
    try:
        symbol = symbol.replace('_', '')
        data = await api_hb.async_market_detail_merged(symbol)
        data = data['tick']
        data['last'] = data['close']
        data['ask'] = data['ask'][0]
        data['bid'] = data['bid'][0]
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    '''convert btc_usdt to btcusdt
    '''
    try:
        symbol = symbol.replace('_', '')
        period = '1min'
        size = '500'
        data_ = await api_hb.async_market_history_kline(symbol, period, size)
        data = []
        for k in data_['data']:
            data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['amount'], k['vol']])
        del data_
        data.reverse()
    except Exception as e:
        data = {}
    return data


async def async_depth(symbol):
    '''convert btc_usdt to btcusdt
    '''
    try:
        symbol = symbol.replace('_', '')
        type = 'step0'
        data = await api_hb.async_market_depth(symbol, type)
        data = data['tick']
        data['asks'].reverse()
        data['asks'] = data['asks'][-9:]
        data['bids'] = data['bids'][0:9]
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    '''convert btc_usdt to btcusdt
    '''
    try:
        symbol = symbol.replace('_', '')
        data = api_hb.market_detail_merged(symbol)
        data = data['tick']
        data['last'] = data['close']
        data['ask'] = data['ask'][0]
        data['bid'] = data['bid'][0]
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    '''convert btc_usdt to btcusdt
    '''
    try:
        symbol = symbol.replace('_', '')
        period = '1min'
        size = '500'
        data_ = api_hb.market_history_kline(symbol, period, size)
        data = []
        for k in data_['data']:
            data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['amount'], k['vol']])
        del data_
        data.reverse()
    except Exception as e:
        data = {}
    return data


def depth(symbol):
    '''convert btc_usdt to btcusdt
    '''
    try:
        symbol = symbol.replace('_', '')
        type = 'step0'
        data = api_hb.market_depth(symbol, type)
        data = data['tick']
        data['asks'].reverse()
        data['asks'] = data['asks'][-9:]
        data['bids'] = data['bids'][0:9]
    except Exception as e:
        data = {}
    return data
