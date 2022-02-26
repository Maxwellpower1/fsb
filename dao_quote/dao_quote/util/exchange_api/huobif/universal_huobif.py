# coding=utf-8

import time

from dao_quote.util.exchange_api.huobif import api_hbf


async def async_ticker(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol_ = '{}_{}'.format(symbol_, contract_type)
        data = await api_hbf.async_market_detail_merged(symbol_)
        data = data['tick']
        data['last'] = data['close']
        data['ask'] = data['ask'][0]
        data['bid'] = data['bid'][0]
    except Exception as e:
        data = {}
    return data


async def async_bar(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol_ = '{}_{}'.format(symbol_, contract_type)
        period = '1min'
        size = '500'
        data_ = await api_hbf.async_market_history_kline(symbol_, period, size)
        data = []
        for k in data_['data']:
            data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['vol'], k['amount']])
        # data.reverse()
        del data_
    except Exception as e:
        data = {}
    return data


async def async_depth(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol_ = '{}_{}'.format(symbol_, contract_type)
        type = 'step6'
        data = await api_hbf.async_market_depth(symbol_, type)
        data = data['tick']
        data['asks'].reverse()
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol_ = '{}_{}'.format(symbol_, contract_type)
        data = api_hbf.market_detail_merged(symbol_)
        data = data['tick']
        data['last'] = data['close']
        data['ask'] = data['ask'][0]
        data['bid'] = data['bid'][0]
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    period = '1min'
    num = '500'
    data = bars(symbol, period, num)
    return data


def bars(symbol, period, num='2000'):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol_ = '{}_{}'.format(symbol_, contract_type)
        period = period
        size = num
        data_ = api_hbf.market_history_kline(symbol_, period, size)
        data = []
        for k in data_['data']:
            data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['vol'], k['amount']])
        del data_
    except Exception as e:
        data = {}
    return data


def depth(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol_ = '{}_{}'.format(symbol_, contract_type)
        type = 'step6'
        data = api_hbf.market_depth(symbol_, type)
        data = data['tick']
        data['asks'].reverse()
    except Exception as e:
        data = {}
    return data
