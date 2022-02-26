# coding=utf-8

import aiohttp
import requests


async def do_async_get(params):
    url = 'https://www.okex.com/api/v5/market/{}'.format(params)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            return result['data']


async def async_all_ticker():
    params = 'tickers?instType=SPOT'
    return await do_async_get(params)


async def async_ticker(symbol):
    symbol = process_symbol(symbol)
    params = 'ticker?instId={}'.format(symbol)
    rst = await do_async_get(params)
    rst = rst[0]
    return rst


async def async_depth(symbol, size):
    symbol = process_symbol(symbol)
    params = 'books?instId={}&sz={}'.format(symbol, size)
    rst = await do_async_get(params)
    rst = rst[0]
    rst_ = {}
    asks = [[float(i[0]), float(i[1]), float(i[2]), float(i[3])] for i in rst['asks']]
    asks.reverse()
    bids = [[float(i[0]), float(i[1]), float(i[2]), float(i[3])] for i in rst['bids']]
    rst_['asks'] = asks
    rst_['bids'] = bids
    rst_['ts'] = int(rst['ts'])
    return rst_


async def async_kline(symbol, type, size, since):
    symbol = process_symbol(symbol)
    if ('m' in type):
        bar = '{}m'.format(type.split('m')[0])
    if ('h' in type):
        bar = '{}H'.format(type.split('h')[0])
    params = 'candles?instId={}&bar={}&limit={}'.format(symbol, bar, size)
    candles = await do_async_get(params)
    klines = [[int(i[0]), float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
    klines.reverse()
    return klines


def process_symbol(symbol):
    return symbol.upper().replace('_', '-')


def do_get(params):
    url = 'https://www.okex.com/api/v5/market/{}'.format(params)
    response = requests.get(url, timeout=3)
    return response.json()['data']


def all_ticker():
    params = 'tickers?instType=SPOT'
    return do_get(params)


def ticker(symbol):
    symbol = process_symbol(symbol)
    params = 'ticker?instId={}'.format(symbol)
    return do_get(params)[0]


def depth(symbol, size):
    symbol = process_symbol(symbol)
    params = 'books?instId={}&sz={}'.format(symbol, size)
    rst = do_get(params)[0]
    rst_ = {}
    asks = [[float(i[0]), float(i[1]), float(i[2]), float(i[3])] for i in rst['asks']]
    asks.reverse()
    bids = [[float(i[0]), float(i[1]), float(i[2]), float(i[3])] for i in rst['bids']]
    rst_['asks'] = asks
    rst_['bids'] = bids
    rst_['ts'] = int(rst['ts'])
    return rst_


def kline(symbol, type, size, since):
    symbol = process_symbol(symbol)
    if ('m' in type):
        bar = '{}m'.format(type.split('m')[0])
    if ('h' in type):
        bar = '{}H'.format(type.split('h')[0])
    params = 'candles?instId={}&bar={}&limit={}'.format(symbol, bar, size)
    candles = do_get(params)
    klines = [[int(i[0]), float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
    klines.reverse()
    return klines
