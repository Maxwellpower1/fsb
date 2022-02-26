# coding=utf-8

import time
import aiohttp
import datetime
import requests


def convert_symbol():
    global symbol_dict
    symbol_dict = {}
    instrument_list = instruments()
    for instrument in instrument_list:
        alias = instrument['alias']
        if alias == 'next_quarter':
            alias = 'bi_quarter'
        key = '{}-{}'.format(instrument['uly'].lower().replace('-', '_'), alias)
        instrument_id = instrument['instId']
        symbol_dict[key] = instrument_id
        if (alias == 'this_week'):
            symbol_dict['expire_time'] = int(instrument['expTime'])
    return symbol_dict


def convert_wss_symbol():
    symbol_dict = {}
    r_symbol_dict = {}
    instrument_list = instruments()
    for instrument in instrument_list:
        alias = instrument['alias']
        if alias == 'next_quarter':
            alias = 'bi_quarter'
        key = '{}-{}'.format(instrument['uly'].lower().replace('-', '_'), alias)
        instrument_id = instrument['instId']
        symbol_dict[key] = instrument_id
        r_symbol_dict[instrument_id] = key
        if (alias == 'this_week'):
            symbol_dict['expire_time'] = int(instrument['expTime'])
    return symbol_dict, r_symbol_dict


async def do_async_get(params):
    url = 'https://www.okex.com/api/v5{}'.format(params)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            result = await response.json()
            result = result['data']
            return result


async def async_all_ticker():
    params = '/market/tickers?instType=FUTURES'
    return await do_async_get(params)


async def async_ticker(symbol):
    symbol = process_symbol(symbol)
    params = '/market/ticker?instId={}'.format(symbol)
    rst =  await do_async_get(params)
    rst = rst[0]
    return rst


async def async_depth(symbol, size):
    symbol = process_symbol(symbol)
    params = '/market/books?instId={}&sz={}'.format(symbol, size)
    rst =  await do_async_get(params)
    rst = rst[0]
    rst_ = {}
    asks = [[float(i[0]), float(i[1]), float(i[2]), float(i[3])] for i in rst['asks']]
    data['asks'].reverse()
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
    params = '/market/candles?instId={}&bar={}&limit={}'.format(symbol, bar, size)
    candles = await do_async_get(params)
    klines = [[int(i[0]), float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
    klines.reverse()
    return klines


def process_symbol(symbol):
    global symbol_dict
    try:
        expire_time = symbol_dict['expire_time']
        if (time.time() > expire_time):
            convert_symbol()
        symbol = symbol_dict[symbol]
    except Exception as e:
        convert_symbol()
        symbol = symbol_dict[symbol]
    return symbol


def do_get(params):
    url = 'https://www.okex.com/api/v5{}'.format(params)
    response = requests.get(url, timeout=3)
    return response.json()['data']


def instruments():
    params = '/public/instruments?instType=FUTURES'
    return do_get(params)


def all_ticker():
    params = '/market/tickers?instType=FUTURES'
    return do_get(params)


def ticker(symbol):
    symbol = process_symbol(symbol)
    params = '/market/ticker?instId={}'.format(symbol)
    return do_get(params)[0]


def depth(symbol, size):
    symbol = process_symbol(symbol)
    params = '/market/books?instId={}&sz={}'.format(symbol, size)
    rst = do_get(params)[0]
    rst_ = {}
    asks = [[float(i[0]), float(i[1]), float(i[2]), float(i[3])] for i in rst['asks']]
    data['asks'].reverse()
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
    params = '/market/candles?instId={}&bar={}&limit={}'.format(symbol, bar, size)
    candles = do_get(params)
    klines = [[int(i[0]), float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
    klines.reverse()
    return klines
