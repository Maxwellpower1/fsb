# coding=utf-8

import os
import ast
import base64
import time
import hmac
import json
import socket
import random
import aiohttp
import hashlib
import datetime
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


async def do_async_get(params):
    url = "https://www.okcoin.com/api/spot/v3/instruments/{}".format(params)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            true = True
            false = False
            result = await response.json()
            return result


async def async_all_ticker():
    params = 'ticker'
    return await do_async_get(params)


async def async_ticker(symbol):
    symbol = process_symbol(symbol)
    params = '{}/ticker'.format(symbol)
    return await do_async_get(params)


async def async_depth(symbol, size):
    symbol = process_symbol(symbol)
    params = '{}/book?size={}'.format(symbol, size)
    return await do_async_get(params)


async def async_kline(symbol, type, size, since):
    symbol = process_symbol(symbol)
    if ('m' in type):
        granularity = int(type.split('m')[0]) * 60
    elif ('h' in type):
        granularity = int(type.split('h')[0]) * 60 * 60
    end = time.time()
    start = time.time() - granularity * size
    start = urllib.parse.quote(shift_time_v3(start))
    end = urllib.parse.quote(shift_time_v3(end))
    params = '{}/candles?instrument_id={}&granularity={}&start={}&end={}'.format(symbol,
             symbol, granularity, start, end)
    candles = await do_async_get(params)
    klines = [[to_timestamp_v3(i[0]), i[1], i[2], i[3], i[4], i[5]] for i in candles]
    return klines


def process_symbol(symbol):
    if ('_' in symbol):
        symbol_part = symbol.split('_')
        symbol = '{}-{}'.format(symbol_part[0].upper(), symbol_part[1].upper())
    else:
        pass
    return symbol


def shift_time_v3(timestamp):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    iso_time = datetime.datetime.utcfromtimestamp(timestamp).strftime(format)
    return iso_time


def to_timestamp_v3(iso_time):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = datetime.datetime.strptime(iso_time, format)
    timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    return timestamp


def do_get(params):
    url = "https://www.okcoin.com/api/spot/v3/instruments/{}".format(params)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    response = requests.get(url, headers=headers, timeout=3)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return ast.literal_eval(resp)


def all_ticker():
    params = 'ticker'
    return do_get(params)


def ticker(symbol):
    symbol = process_symbol(symbol)
    params = '{}/ticker'.format(symbol)
    return do_get(params)


def depth(symbol, size):
    symbol = process_symbol(symbol)
    params = '{}/book?size={}'.format(symbol, size)
    return do_get(params)


def kline(symbol, type, size, since):
    symbol = process_symbol(symbol)
    if ('m' in type):
        granularity = int(type.split('m')[0]) * 60
    elif ('h' in type):
        granularity = int(type.split('h')[0]) * 60 * 60
    end = time.time()
    start = time.time() - granularity * size
    start = urllib.parse.quote(shift_time_v3(start))
    end = urllib.parse.quote(shift_time_v3(end))
    params = '{}/candles?instrument_id={}&granularity={}&start={}&end={}'.format(symbol,
             symbol, granularity, start, end)
    candles = do_get(params)
    klines = [[to_timestamp_v3(i[0]), i[1], i[2], i[3], i[4], i[5]] for i in candles]
    return klines


def request(api, method, params, api_key, secret_key):
    secret_key_ = secret_key.split('-')
    secret_key = secret_key_[0]
    passphrase = secret_key_[1]
    request_path = '/api/spot/v3/{}'.format(api)
    url = "https://www.okcoin.com"
    timestamp = str(round(time.time(), 3))
    headers = {'Content-Type': 'application/json'}
    headers['OK-ACCESS-KEY'] = api_key
    headers['OK-ACCESS-TIMESTAMP'] = timestamp
    headers['OK-ACCESS-PASSPHRASE'] = passphrase

    if str(params) == '{}' or str(params) == 'None':
        params = ''
    if method == 'GET':
        params = ''
        url += request_path
    if method == 'POST':
        request_path += '?'
        for key, value in params.items():
            request_path = request_path + str(key) + '=' + str(value) + '&'
        request_path = request_path[0:-1]
        params = json.dumps(params)

    message = '{timestamp}{method}{request_path}{params}'.format(
               timestamp=timestamp, method=method,
               request_path=request_path, params=params)

    signature = hmac.new(bytes(secret_key.encode('utf-8')),
                         msg=bytes(message.encode('utf-8')),
                         digestmod=hashlib.sha256).digest()

    headers['OK-ACCESS-SIGN'] = base64.b64encode(signature)

    if method == 'GET':
        response = requests.get(url, headers=headers)
    if method == 'POST':
        url += request_path
        response = requests.post(url, headers=headers, data=params)

    true = True
    false = False
    return eval(response.content)


def accounts(api_key, secret_key):
    api = 'accounts'
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def userinfo(api_key, secret_key):
    return accounts(api_key, secret_key)


def trade(symbol, tradetype, api_key, secret_key, price='', amount=''):
    api = "orders"
    method = 'POST'
    symbol = process_symbol(symbol)
    params = {}
    if ('buy' in tradetype):
        side = 'buy'
    elif ('sell' in tradetype):
        side = 'sell'
    if ('market' in tradetype):
        type = 'market'
        params['notional'] = price
    else:
        type = 'limit'
    params['type'] = type
    params['side'] = side
    params['instrument_id'] = symbol
    params['order_type'] = 0
    params['margin_trading'] = 1
    if price:
        params['price'] = price
    if amount:
        params['size'] = amount
    return request(api, method, params, api_key, secret_key)


def fetch_or_cancel_order(api, method, symbol, id, api_key, secret_key):
    symbol = process_symbol(symbol)
    params = {}
    params['instrument_id'] = symbol
    params['client_oid'] = ''
    params['order_id'] = id
    return request(api, method, params, api_key, secret_key)


def fetch_order(symbol, id, api_key, secret_key):
    symbol = process_symbol(symbol)
    api = "orders/{}?instrument_id={}".format(id, symbol)
    method = 'GET'
    return fetch_or_cancel_order(api, method, symbol, id, api_key, secret_key)


def cancel_order(symbol, id, api_key, secret_key):
    api = "cancel_orders/{}".format(id)
    method = 'POST'
    symbol = process_symbol(symbol)
    return fetch_or_cancel_order(api, method, symbol, id, api_key, secret_key)
