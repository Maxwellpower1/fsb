# coding=utf-8

import asyncio

from dao_quote.util.exchange_api.okex import universal_okex_v5 as universal_okex
from dao_quote.util.exchange_api.huobi import universal_huobi
from dao_quote.util.exchange_api.huobif import universal_huobif
from dao_quote.util.exchange_api.binance import universal_binance
from dao_quote.util.exchange_api.okexf import universal_okexf_v5 as universal_okexf


async def get_async_ticker(exchange, symbol):
    if (exchange == 'okex'):
        data = await universal_okex.async_ticker(symbol)
    elif (exchange == 'okexf'):
        data = await universal_okexf.async_ticker(symbol)
    elif (exchange == 'huobi'):
        data = await universal_huobi.async_ticker(symbol)
    elif (exchange == 'huobif'):
        data = await universal_huobif.async_ticker(symbol)
    elif (exchange == 'binance'):
        data = await universal_binance.async_ticker(symbol)
    else:
        data = {}
    return data


async def get_async_bar(exchange, symbol):
    data = {}
    if (exchange == 'okex'):
        data = await universal_okex.async_bar(symbol)
    elif (exchange == 'okexf'):
        data = await universal_okexf.async_bar(symbol)
    elif (exchange == 'huobi'):
        data = await universal_huobi.async_bar(symbol)
    elif (exchange == 'huobif'):
        data = await universal_huobif.async_bar(symbol)
    elif (exchange == 'binance'):
        data = await universal_binance.async_bar(symbol)
    else:
        data = {}
    try:
        bar_test = float(data[-2][4])
    except Exception as e:
        data = {}
    return data


async def get_async_depth(exchange, symbol):
    data = {}
    if (exchange == 'okex'):
        data = await universal_okex.async_depth(symbol)
    elif (exchange == 'okexf'):
        data = await universal_okexf.async_depth(symbol)
    elif (exchange == 'huobi'):
        data = await universal_huobi.async_depth(symbol)
    elif (exchange == 'huobif'):
        data = await universal_huobif.async_depth(symbol)
    elif (exchange == 'binance'):
        data = await universal_binance.async_depth(symbol)
    else:
        data = {}
    return data


def get_ticker(exchange, symbol):
    if (exchange == 'okex'):
        data = universal_okex.ticker(symbol)
    elif (exchange == 'okexf'):
        data = universal_okexf.ticker(symbol)
    elif (exchange == 'huobi'):
        data = universal_huobi.ticker(symbol)
    elif (exchange == 'huobif'):
        data = universal_huobif.ticker(symbol)
    elif (exchange == 'binance'):
        data = universal_binance.ticker(symbol)
    else:
        data = {}
    return data


def get_bar(exchange, symbol):
    data = {}
    if (exchange == 'okex'):
        data = universal_okex.bar(symbol)
    elif (exchange == 'okexf'):
        data = universal_okexf.bar(symbol)
    elif (exchange == 'huobi'):
        data = universal_huobi.bar(symbol)
    elif (exchange == 'huobif'):
        data = universal_huobif.bar(symbol)
    elif (exchange == 'binance'):
        data = universal_binance.bar(symbol)
    else:
        data = {}
    try:
        bar_test = float(data[-2][4])
    except Exception as e:
        data = {}
    return data


def get_depth(exchange, symbol):
    data = {}
    if (exchange == 'okex'):
        data = universal_okex.depth(symbol)
    elif (exchange == 'okexf'):
        data = universal_okexf.depth(symbol)
    elif (exchange == 'huobi'):
        data = universal_huobi.depth(symbol)
    elif (exchange == 'huobif'):
        data = universal_huobif.depth(symbol)
    elif (exchange == 'binance'):
        data = universal_binance.depth(symbol)
    else:
        data = {}
    return data
