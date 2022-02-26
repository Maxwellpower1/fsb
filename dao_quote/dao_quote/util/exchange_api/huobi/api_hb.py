# coding=utf-8

import os
import ast
import hmac
import json
import time
import base64
import socket
import random
import aiohttp
import hashlib
import urllib3
import datetime
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


async def do_async_get(api, params=''):
    url = 'https://api.huobipro.com{}{}'.format(api, params)
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.71 Safari/537.36'),
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            true = True
            false = False
            result = await response.json(content_type=None)
            return result


async def async_market_detail(symbol):
    params = '?symbol={}'.format(symbol)
    return await do_async_get('/market/detail', params)


async def async_market_detail_merged(symbol):
    params = '?symbol={}'.format(symbol)
    return await do_async_get('/market/detail/merged', params)


async def async_market_depth(symbol, type):
    params = '?symbol={}&type={}'.format(symbol, type)
    return await do_async_get('/market/depth', params)


async def async_market_history_kline(symbol, period, size):
    params = '?symbol={}&period={}&size={}'.format(
             symbol, period, size)
    return await do_async_get('/market/history/kline', params)


def do_get(api, params=''):
    url = 'https://api.huobipro.com{}{}'.format(api, params)
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.71 Safari/537.36'),
    }
    response = requests.get(url, headers=headers, timeout=3)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return ast.literal_eval(resp)


def market_history_kline(symbol, period, size):
    params = '?symbol={}&period={}&size={}'.format(
             symbol, period, size)
    return do_get('/market/history/kline', params)


def market_detail_merged(symbol):
    params = '?symbol={}'.format(symbol)
    return do_get('/market/detail/merged', params)


def market_tickers():
    params = ''
    return do_get('/market/tickers', params)


def market_depth(symbol, type):
    params = '?symbol={}&type={}'.format(symbol, type)
    return do_get('/market/depth', params)


def market_trade(symbol):
    params = '?symbol={}'.format(symbol)
    return do_get('/market/trade', params)


def market_history_trade(symbol, size):
    params = '?symbol={}&size={}'.format(symbol, size)
    return do_get('/market/history/trade', params)


def market_detail(symbol):
    params = '?symbol={}'.format(symbol)
    return do_get('/market/detail', params)


def main():
    print('test ok! ')


if __name__ == '__main__':
    main()
