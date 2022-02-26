# coding=utf-8

import time

from dao_quote.util.exchange_api.okexf import api_okf


async def async_ticker(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('-')[0]
        data = await api_okf.async_future_ticker(symbol_, contract_type)
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
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('-')[0]
        data = await api_okf.async_future_kline(symbol_, type, contract_type, size, since)
    except Exception as e:
        data = {}
    return data


async def async_depth(symbol):
    try:
        size = 9
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('-')[0]
        data = await api_okf.async_future_depth(symbol_, contract_type, size)
    except Exception as e:
        data = {}
    return data


def ticker(symbol):
    try:
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('-')[0]
        data = api_okf.future_ticker(symbol_, contract_type)
        data = data['ticker']
        data['ask'] = data['sell']
        data['bid'] = data['buy']
    except Exception as e:
        data = {}
    return data


def bar(symbol):
    period = '1min'
    num = '500'
    data = bars(symbol, period, num)
    return data


def bars(symbol, period, num=''):
    try:
        type = period
        size = num
        since = ''
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('-')[0]
        data = api_okf.future_kline(symbol_, type, contract_type, size, since)
    except Exception as e:
        data = {}
    return data


def depth(symbol):
    try:
        size = 9
        contract_type = symbol.split('-')[1]
        symbol_ = symbol.split('-')[0]
        data = api_okf.future_depth(symbol_, contract_type, size)
    except Exception as e:
        data = {}
    return data
