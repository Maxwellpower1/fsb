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


def convert_symbol():
    global symbol_dict
    symbol_dict = {}
    instrument_list = instruments()
    for instrument in instrument_list:
        alias = instrument['alias']
        key = '{}-{}'.format(instrument['underlying'].lower().replace('-', '_'), alias)
        instrument_id = instrument['instrument_id']
        symbol_dict[key] = instrument_id
        if (alias == 'this_week'):
            delivery = instrument['delivery']
    symbol_dict['expire_time'] = to_timestamp('{} {}'.format(delivery, '16:00:00'))
    return symbol_dict


def convert_wss_symbol():
    symbol_dict = {}
    r_symbol_dict = {}
    instrument_list = instruments()
    for instrument in instrument_list:
        alias = instrument['alias']
        key = '{}-{}'.format(instrument['underlying'].lower().replace('-', '_'), alias)
        instrument_id = instrument['instrument_id']
        symbol_dict[key] = instrument_id
        r_symbol_dict[instrument_id] = key
        if (alias == 'this_week'):
            delivery = instrument['delivery']
    symbol_dict['expire_time'] = to_timestamp('{} {}'.format(delivery, '16:00:00'))
    return symbol_dict, r_symbol_dict


async def do_async_get(params):
    url = "https://www.okex.com/api/futures/v3/instruments/{}".format(params)
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
    start = end - granularity * size
    start = urllib.parse.quote(shift_time_v3(start))
    end = urllib.parse.quote(shift_time_v3(end))
    params = '{}/candles?instrument_id={}&granularity={}&start={}&end={}'.format(symbol,
             symbol, granularity, start, end)
    candles = await do_async_get(params)
    klines = [[to_timestamp_v3(i[0])*1000, float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
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


def shift_time_v3(timestamp):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    iso_time = datetime.datetime.utcfromtimestamp(timestamp).strftime(format)
    return iso_time


def to_timestamp_v3(iso_time):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = datetime.datetime.strptime(iso_time, format)
    timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    return timestamp


def to_timestamp(time_date):
    format = '%Y-%m-%d %H:%M:%S'
    timearray = time.strptime(time_date, format)
    timestamp = int(time.mktime(timearray))
    return timestamp


def do_get(params):
    url = 'https://www.okex.com/api/futures/v3/instruments/{}'.format(params)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    response = requests.get(url, headers=headers, timeout=3)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    resp = resp.replace("true", "True").replace("false", "False").replace("null", "None")
    return ast.literal_eval(resp)


def instruments():
    params = ''
    return do_get(params)


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
    klines = [[to_timestamp_v3(i[0])*1000, float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
    klines.reverse()
    return klines


def all_kline(symbol, type, begin_timestamp, end_timestamp):
    symbol = process_symbol(symbol)
    if ('m' in type):
        granularity = int(type.split('m')[0]) * 60
    elif ('h' in type):
        granularity = int(type.split('h')[0]) * 60 * 60
    end = time.time()
    start = time.time() - granularity * size
    start = urllib.parse.quote(shift_time_v3(begin_timestamp))
    end = urllib.parse.quote(shift_time_v3(end_timestamp))
    params = '{}/candles?instrument_id={}&granularity={}&start={}&end={}'.format(symbol,
             symbol, granularity, start, end)
    candles = do_get(params)
    klines = [[to_timestamp_v3(i[0])*1000, float(i[1]), float(i[2]), float(i[3]), float(i[4]), float(i[5]), float(i[6])] for i in candles]
    klines.reverse()
    return klines


def request(api, method, params, api_key, secret_key):
    secret_key_ = secret_key.split('-')
    secret_key = secret_key_[0]
    passphrase = secret_key_[1]
    request_path = '/api/futures/v3/{}'.format(api)
    url = "https://www.okex.com"
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


def position(api_key, secret_key):
    api = "position"
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def accounts(api_key, secret_key):
    api = 'accounts'
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def get_leverage(symbol, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = 'accounts/{currency}/leverage'.format(
           currency=instrument_id.split('-')[0].lower())
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def set_leverage(margin_mode, symbol, direction,
                 leverage, api_key, secret_key):
    '''direction long short
       leverage 10 20
    '''
    instrument_id = process_symbol(symbol)
    currency = instrument_id.split('-')[0].lower()
    api = 'accounts/{currency}/leverage'.format(
           currency=currency)
    method = 'POST'
    if margin_mode == 'crossed':
        params = {
            'leverage': leverage,
            'currency': currency
        }
    elif margin_mode == 'fixed':
        params = {
            'currency': currency,
            'instrument_id': instrument_id,
            'direction': direction,
            'leverage': leverage,
        }
    return request(api, method, params, api_key, secret_key)


def order(symbol, type, price, size, match_price, leverage,
          api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = "order"
    method = 'POST'
    params = {
        'instrument_id': instrument_id,
        'type': type,
        'price': price,
        'size': size,
        'match_price': match_price,
        'leverage': leverage
    }
    return request(api, method, params, api_key, secret_key)


def cancel_order(symbol, order_id, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = 'cancel_order/{instrument_id}/{order_id}'.format(
          instrument_id=instrument_id, order_id=order_id)
    method = 'POST'
    params = {
        'instrument_id': instrument_id,
        'order_id': order_id
    }
    return request(api, method, params, api_key, secret_key)


def fetch_order(symbol, order_id, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = 'orders/{instrument_id}/{order_id}'.format(
           instrument_id=instrument_id, order_id=order_id)
    method = 'GET'
    params = {
        'instrument_id': instrument_id,
        'order_id': order_id
    }
    return request(api, method, params, api_key, secret_key)


def main():
    print('test ok! ')


if __name__ == '__main__':
    main()
