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
    instrument_list = instruments()
    symbol_dict = {}
    for instrument in instrument_list:
        alias = instrument['alias']
        key = '{}-{}'.format(instrument['underlying'].lower().replace('-', '_'), alias)
        instrument_id = instrument['instrument_id']
        symbol_dict[key] = instrument_id
        if (alias == 'this_week'):
            delivery = instrument['delivery']
    symbol_dict['expire_time'] = to_timestamp('{} {}'.format(delivery, '16:00:00'))


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
    response = requests.get(url, headers=headers, timeout=5)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    resp = resp.replace("true", "True").replace("false", "False").replace("null", "None")
    return ast.literal_eval(resp)


def instruments():
    params = ''
    return do_get(params)


def depth(symbol, size):
    symbol = process_symbol(symbol)
    params = '{}/book?size={}'.format(symbol, size)
    return do_get(params)


def get_depth_api(symbol, size, depth=''):
    try:
        symbol = process_symbol(symbol)
        params = '{}/book?size={}&depth={}'.format(symbol, size, depth)
        data = do_get(params)
        data ['ts'] = to_timestamp_v3(data['timestamp'])*1000
        del data['timestamp']
    except Exception as e:
        data = {}
    return data


def request(api, method, params, api_key, secret_key):
    secret_key, passphrase = secret_key.split('-')
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
    null = None
    return eval(response.content)


def position(symbol, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = "{instrument_id}/position".format(instrument_id=instrument_id)
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def future_position_4fix(symbol, api_key, secret_key, contract_type, type):
    symbol = '{}-{}'.format(symbol, contract_type)
    positions = position(symbol, api_key, secret_key)
    try:
        position_dict = {}
        positions = positions['holding'][0]
        position_dict['buy_amount'] = float(positions['long_qty'])
        position_dict['buy_available'] = float(positions['long_avail_qty'])
        position_dict['buy_profit_lossratio'] = float(positions['long_pnl_ratio'])
        position_dict['sell_amount'] = float(positions['short_qty'])
        position_dict['sell_available'] = float(positions['short_avail_qty'])
        position_dict['sell_profit_lossratio'] = float(positions['short_pnl_ratio'])
        positions = {'holding': [position_dict]}
    except Exception as e:
        positions = {'error_code': 1}
    return positions


def accounts(api_key, secret_key):
    api = 'accounts'
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def future_userinfo(api_key, secret_key):
    rst = accounts(api_key, secret_key)
    try:
        account_balance_dict = {}
        info = rst['info']
        for coin in info:
            coin_dict = info[coin]
            coin_dict_new = {}
            coin_dict_new['balance'] = float(coin_dict['total_avail_balance'])
            coin_dict_new['contracts'] = [{'available': float(coin_dict['equity'])}]
            account_balance_dict[coin] = coin_dict_new
        rst['info'] = account_balance_dict
    except Exception as e:
        rst['error_code'] = rst['code']
    return rst


def get_leverage(symbol, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = 'accounts/{currency}/leverage'.format(
           currency=instrument_id.split('-')[0].lower())
    method = 'GET'
    params = {}
    return request(api, method, params, api_key, secret_key)


def set_leverage(margin_mode, symbol, direction, leverage, api_key, secret_key):
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


def future_trade(symbol, type, price, size, match_price, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = "order"
    method = 'POST'
    params = {
        'instrument_id': instrument_id,
        'type': type,
        'price': price,
        'size': size,
        'match_price': match_price
    }
    return request(api, method, params, api_key, secret_key)


def future_cancel(symbol, order_id, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = 'cancel_order/{instrument_id}/{order_id}'.format(
          instrument_id=instrument_id, order_id=order_id)
    method = 'POST'
    params = {
        'instrument_id': instrument_id,
        'order_id': order_id
    }
    return request(api, method, params, api_key, secret_key)


def future_fetch(symbol, order_id, api_key, secret_key):
    instrument_id = process_symbol(symbol)
    api = 'orders/{instrument_id}/{order_id}'.format(
           instrument_id=instrument_id, order_id=order_id)
    method = 'GET'
    params = {
        'instrument_id': instrument_id,
        'order_id': order_id
    }
    return request(api, method, params, api_key, secret_key)
