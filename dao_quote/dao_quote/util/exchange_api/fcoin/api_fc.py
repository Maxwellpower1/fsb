# coding=utf-8

import socket
import aiohttp
import hashlib
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


def convert_symbol(symbol):
    return symbol.replace('_', '')


async def do_async_get(api, **payload):
    url = 'https://api.fcoin.com/v2/{}'.format(api)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=payload) as response:
            result = await response.json(content_type=None)
            return result


async def async_ticker(symbol):
    symbol = convert_symbol(symbol)
    api = 'market/ticker/{}'.format(symbol)
    return await do_async_get(api)


async def async_depth(symbol, level):
    symbol = convert_symbol(symbol)
    api = 'market/depth/{}/{}'.format(level, symbol)
    return await do_async_get(api)


async def async_kline(symbol, period):
    symbol = convert_symbol(symbol)
    api = 'market/candles/{}/{}'.format(period, symbol)
    return await do_async_get(api)


def do_get(method, api, **payload):
    url = 'https://api.fcoin.com/v2/{}'.format(api)
    r = requests.request(method, url, params=payload)
    return r.json()


def ticker(symbol):
    method = 'GET'
    symbol = convert_symbol(symbol)
    api = 'market/ticker/{}'.format(symbol)
    return do_get(method, api)


def depth(symbol, level):
    method = 'GET'
    symbol = convert_symbol(symbol)
    api = 'market/depth/{}/{}'.format(level, symbol)
    return do_get(method, api)


def kline(symbol, period):
    method = 'GET'
    symbol = convert_symbol(symbol)
    api = 'market/candles/{}/{}'.format(period, symbol)
    return do_get(method, api)
