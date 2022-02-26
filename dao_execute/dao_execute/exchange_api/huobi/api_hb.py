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
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return await do_async_get('/market/detail', params)


async def async_market_detail_merged(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return await do_async_get('/market/detail/merged', params)


async def async_market_depth(symbol, type):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&type={}'.format(symbol, type)
    return await do_async_get('/market/depth', params)


async def async_market_history_kline(symbol, period, size):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&period={}&size={}'.format(
             symbol, period, size)
    return await do_async_get('/market/history/kline', params)


def convert_symbol(symbol):
    return symbol.replace('_', '')


def do_get(api, params=''):
    url = 'https://api.huobipro.com{}{}'.format(api, params)
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.71 Safari/537.36'),
    }
    response = requests.get(url, headers=headers, timeout=5)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return ast.literal_eval(resp)


def market_history_kline(symbol, period, size):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&period={}&size={}'.format(
             symbol, period, size)
    return do_get('/market/history/kline', params)


def market_detail_merged(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return do_get('/market/detail/merged', params)


def market_tickers():
    params = ''
    return do_get('/market/tickers', params)


def market_depth(symbol, type):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&type={}'.format(symbol, type)
    return do_get('/market/depth', params)


def market_trade(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return do_get('/market/trade', params)


def market_history_trade(symbol, size):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&size={}'.format(symbol, size)
    return do_get('/market/history/trade', params)


def market_detail(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return do_get('/market/detail', params)


def time():
    params = ''
    return do_get('/v1/common/timestamp', params)


def api_key_get(api, params, api_key, secret_key):
    method = 'GET'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params.update({'AccessKeyId': api_key,
                   'SignatureMethod': 'HmacSHA256',
                   'SignatureVersion': '2',
                   'Timestamp': timestamp})

    url = 'https://api.huobipro.com'
    host_name = urllib.parse.urlparse(url).hostname
    host_name = host_name.lower()
    params['Signature'] = createSign(params, method,
                                     host_name, api, secret_key)

    url = url + api
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/39.0.2171.71 Safari/537.36'),
    }
    postdata = urllib.parse.urlencode(params)
    response = requests.get(url, postdata, headers=headers, timeout=5)
    null = None
    resp = response.content
    # resp = resp.decode('utf-8')
    # resp = ast.literal_eval(resp)
    resp = eval(resp)
    return resp


def api_key_post(api, params, api_key, secret_key):
    method = 'POST'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params_to_sign = {'AccessKeyId': api_key,
                      'SignatureMethod': 'HmacSHA256',
                      'SignatureVersion': '2',
                      'Timestamp': timestamp}

    url = 'https://api.huobipro.com'
    host_name = urllib.parse.urlparse(url).hostname
    host_name = host_name.lower()
    params_to_sign['Signature'] = createSign(params_to_sign, method,
                                             host_name, api, secret_key)

    url = url + api + '?' + urllib.parse.urlencode(params_to_sign)
    headers = {
               "Accept": "application/json",
               'Content-Type': 'application/json'
    }
    postdata = json.dumps(params)
    response = requests.post(url, postdata, headers=headers, timeout=5)
    null = None
    resp = response.content
    # resp = resp.decode('utf-8')
    # resp = ast.literal_eval(resp)
    resp = eval(resp)
    return resp


def createSign(pParams, method, url, api, secret_key):
    sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
    encode_params = urllib.parse.urlencode(sorted_params)
    payload = [method, url, api, encode_params]
    payload = '\n'.join(payload)
    payload = payload.encode(encoding='UTF8')
    secret_key = secret_key.encode(encoding='UTF8')

    digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)
    signature = signature.decode()
    return signature


def account(api_key, secret_key):
    params = {}
    api = '/v1/account/accounts'
    return api_key_get(api, params, api_key, secret_key)


def account_balance(account_id, api_key, secret_key):
    params = {}
    api = '/v1/account/accounts/{}/balance'.format(account_id)
    return api_key_get(api, params, api_key, secret_key)


def account_balance_by_type(type, api_key, secret_key):
    account_msg = account(api_key, secret_key)
    for account_one in account_msg['data']:
        if account_one['type'] == type:
            account_id = account_one['id']
    return account_balance(account_id, api_key, secret_key)


def account_id_by_type(type, api_key, secret_key):
    for account_one in account(api_key, secret_key)['data']:
        if account_one['type'] == type:
            account_id = account_one['id']
    return account_id


def orders_place(symbol, type, price, amount, account_id,
                 source, api_key, secret_key):
    symbol = convert_symbol(symbol)
    api = "/v1/order/orders/place"
    params = {
        'account-id': account_id,
        'amount': amount,
        'price': price,
        'source': source,
        'symbol': symbol,
        'type': type
    }
    return api_key_post(api, params, api_key, secret_key)


def open_orders(side, size, api_key, secret_key, symbol='', account_id=''):
    symbol = convert_symbol(symbol)
    api = "/v1/order/openOrders"
    params = {}
    if account_id:
        params['account-id'] = account_id
    if symbol:
        params['symbol-id'] = symbol
    params = {
        'side': side,
        'size': size,
    }
    return api_key_get(api, params, api_key, secret_key)


def submit_cancel(order_id, api_key, secret_key):
    api = "/v1/order/orders/{}/submitcancel".format(order_id)
    params = {}
    return api_key_post(api, params, api_key, secret_key)


def batch_cancel(order_ids, api_key, secret_key):
    params = {
        'order-ids': order_ids,
    }
    return api_key_post(api, params, api_key, secret_key)


def fetch_order(order_id, api_key, secret_key):
    api = "/v1/order/orders/{}".format(order_id)
    params = {}
    return api_key_get(api, params, api_key, secret_key)
