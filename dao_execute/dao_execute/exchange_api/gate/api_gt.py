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
    url = "https://data.gateio.co/api2/1/{}/{}{}".format(
          sec_type, symbol, other)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            true = True
            false = False
            result = await response.json()
            return result


async def async_ticker(symbol):
    return await do_async_get('ticker', symbol)


async def async_depth(symbol):
    return await do_async_get('orderBook', symbol)


async def async_kline(symbol, group_sec, range_hour):
    other = '?group_sec={}&range_hour={}'.format(group_sec, range_hour)
    return await do_async_get('candlestick2', symbol, other)


def do_get(sec_type, symbol, other=''):
    url = "https://data.gateio.co/api2/1/{}/{}{}".format(
          sec_type, symbol, other)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    response = requests.get(url, headers=headers, timeout=3)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return ast.literal_eval(resp)


def ticker(symbol):
    return do_get('ticker', symbol)


def depth(symbol):
    return do_get('orderBook', symbol)


def kline(symbol, group_sec, range_hour):
    other = '?group_sec={}&range_hour={}'.format(group_sec, range_hour)
    return do_get('candlestick2', symbol, other)


def request(api, params, api_key, secret_key):
    url = "https://api.gateio.co/api2/1/private/{}".format(api)

    bSecretKey = bytes(secret_key, encoding='utf8')

    sign = ''
    for key in params.keys():
        value = str(params[key])
        sign += key + '=' + value + '&'
    bSign = bytes(sign[:-1], encoding='utf8')
    mySign = hmac.new(bSecretKey, bSign, hashlib.sha512).hexdigest()

    headers = {
        'contentType': 'application/x-www-form-urlencoded',
        "KEY": api_key,
        "SIGN": mySign
    }
    response = requests.post(url, headers=headers, data=params)

    true = True
    false = False
    resp = response.content
    # resp = resp.decode('utf-8')
    # resp = ast.literal_eval(resp)
    resp = eval(resp)
    return resp


def balances(api_key, secret_key):
    api = 'balances'
    params = {}
    return request(api, params, api_key, secret_key)


def margin_balances(api_key, secret_key):
    api = 'marginbalances'
    params = {}
    return request(api, params, api_key, secret_key)


def order(symbol, order_type, api_key, secret_key, price='', amount=''):
    if (order_type == 'market_buy'):
        api = 'buy'
        order_type = 'ioc'
    elif (order_type == 'market_sell'):
        api = 'sell'
        order_type = 'ioc'
    elif (order_type == 'limit_buy'):
        api = 'buy'
        order_type = ''
    elif (order_type == 'limit_sell'):
        api = 'sell'
        order_type = ''
    params = {
        'currencyPair': symbol,
        'orderType': order_type
    }
    if price:
        params['rate'] = price
    if amount:
        params['amount'] = amount
    return request(api, params, api_key, secret_key)


def fetch_or_cancel_order(api, symbol, id, api_key, secret_key):
    params = {
        'currencyPair': symbol,
        'orderNumber': id
    }
    return request(api, params, api_key, secret_key)


def fetch_order(symbol, id, api_key, secret_key):
    api = "getOrder"
    return fetch_or_cancel_order(api, symbol, id, api_key, secret_key)


def cancel_order(symbol, id, api_key, secret_key):
    api = "cancelOrder"
    return fetch_or_cancel_order(api, symbol, id, api_key, secret_key)
