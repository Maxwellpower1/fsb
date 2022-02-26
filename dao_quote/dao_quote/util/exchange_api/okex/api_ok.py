# coding=utf-8

import os
import ast
import time
import hmac
import json
import socket
import random
import aiohttp
import hashlib
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


async def do_async_get(sec_type, symbol, other=''):
    url = "https://www.okex.com/api/v1/{}?symbol={}{}".format(
          sec_type, symbol, other)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            true = True
            false = False
            result = await response.json()
            return result


async def async_ticker(symbol):
    return await do_async_get('ticker.do', symbol)


async def async_depth(symbol, size):
    other = '&size={}'.format(size)
    return await do_async_get('depth.do', symbol, other)


async def async_kline(symbol, type, size, since):
    other = '&type={}&size={}&since={}'.format(type, size, since)
    return await do_async_get('kline.do', symbol, other)


def do_get(sec_type, symbol, other=''):
    url = "https://www.okex.com/api/v1/{}?symbol={}{}".format(
          sec_type, symbol, other)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    response = requests.get(url, headers=headers, timeout=3)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return ast.literal_eval(resp)


def ticker(symbol):
    return do_get('ticker.do', symbol)


def depth(symbol, size):
    other = '&size={}'.format(size)
    return do_get('depth.do', symbol, other)


def kline(symbol, type, size, since):
    other = '&type={}&size={}&since={}'.format(type, size, since)
    return do_get('kline.do', symbol, other)


def request(api, params, secret_key):
    url = "https://www.okex.com/api/v1/{}".format(api)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    sign = ''
    for key in sorted(params.keys()):
        sign += key + '=' + str(params[key]) + '&'
    data = sign+'secret_key='+secret_key
    sign = hashlib.md5(data.encode("utf8")).hexdigest().upper()
    params['sign'] = sign

    response = requests.post(url, headers=headers, data=params)

    true = True
    false = False
    resp = response.content
    # resp = resp.decode('utf-8')
    # resp = ast.literal_eval(resp)
    resp = eval(resp)
    return resp


def userinfo(api_key, secret_key):
    api = "userinfo.do"
    params = {'api_key': api_key}
    return request(api, params, secret_key)


def trade(symbol, tradetype, api_key, secret_key, price='', amount=''):
    api = "trade.do"
    params = {
        'api_key': api_key,
        'symbol': symbol,
        'type': tradetype
    }
    if price:
        params['price'] = price
    if amount:
        params['amount'] = amount
    return request(api, params, secret_key)


def batch_trade(symbol, api_key, secret_key, orders_data):
    api = "batch_trade.do"
    params = {
        'api_key': api_key,
        'symbol': symbol,
        'orders_data': orders_data
    }
    return request(api, params, secret_key)


def fetch_or_cancel_order(api, symbol, id, api_key, secret_key):
    params = {
        'api_key': api_key,
        'symbol': symbol,
        'order_id': id
    }
    return request(api, params, secret_key)


def fetch_order(symbol, id, api_key, secret_key):
    api = "order_info.do"
    return fetch_or_cancel_order(api, symbol, id, api_key, secret_key)


def cancel_order(symbol, id, api_key, secret_key):
    api = "cancel_order.do"
    return fetch_or_cancel_order(api, symbol, id, api_key, secret_key)


def main():
    print('test ok! ')


if __name__ == '__main__':
    main()
