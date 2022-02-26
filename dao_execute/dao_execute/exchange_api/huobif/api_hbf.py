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


async def do_async_get(params):
    url = 'https://api.hbdm.com/{}'.format(params)
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            true = True
            false = False
            result = await response.json(content_type=None)
            return result


async def async_market_detail_merged(symbol):
    params = 'market/detail/merged?symbol={}'.format(symbol)
    return await do_async_get(params)


async def async_market_depth(symbol, type):
    params = 'market/depth?symbol={}&type={}'.format(symbol, type)
    return await do_async_get(params)


async def async_market_history_kline(symbol, period, size):
    params = 'market/history/kline?symbol={}&period={}&size={}'.format(
             symbol, period, size)
    return await do_async_get(params)


def do_get(params):
    url = 'https://api.hbdm.com/{}'.format(params)
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    response = requests.get(url, headers=headers, timeout=5)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return ast.literal_eval(resp)


def contract_contract_info(symbol, contract_type, contract_code):
    params = 'api/v1/contract_contract_info'
    params_dict = {}
    if (symbol != ''):
        params_dict['symbol'] = symbol
    if (contract_type != ''):
        params_dict['contract_type'] = contract_type
    if (contract_code != ''):
        params_dict['contract_code'] = contract_code
    if (params_dict != {}):
        params += '?{}'.format(urllib.parse.urlencode(params_dict))
    return do_get(params)


def contract_index(symbol):
    params = 'api/v1/contract_index?symbol={}'.format(symbol)
    return do_get(params)


def contract_price_limit(symbol, contract_type, contract_code):
    params = 'api/v1/contract_price_limit'
    params_dict = {}
    if (symbol != ''):
        params_dict['symbol'] = symbol
    if (contract_type != ''):
        params_dict['contract_type'] = contract_type
    if (contract_code != ''):
        params_dict['contract_code'] = contract_code
    if (params_dict != {}):
        params += '?{}'.format(urllib.parse.urlencode(params_dict))
    return do_get(params)


def contract_open_interest(symbol, contract_type, contract_code):
    params = 'api/v1/contract_open_interest'
    params_dict = {}
    if (symbol != ''):
        params_dict['symbol'] = symbol
    if (contract_type != ''):
        params_dict['contract_type'] = contract_type
    if (contract_code != ''):
        params_dict['contract_code'] = contract_code
    if (params_dict != {}):
        params += '?{}'.format(urllib.parse.urlencode(params_dict))
    return do_get(params)


def contract_delivery_price(symbol):
    params = 'api/v1/contract_delivery_price?symbol={}'.format(symbol)
    return do_get(params)


def market_depth(symbol, type):
    params = 'market/depth?symbol={}&type={}'.format(symbol, type)
    return do_get(params)


def market_history_kline(symbol, period, size):
    params = 'market/history/kline?symbol={}&period={}&size={}'.format(
             symbol, period, size)
    return do_get(params)


def market_detail_merged(symbol):
    params = 'market/detail/merged?symbol={}'.format(symbol)
    return do_get(params)


def market_trade(symbol):
    params = 'market/trade?symbol={}'.format(symbol)
    return do_get(params)


def market_history_trade(symbol, size):
    params = 'market/history/trade?symbol={}&size={}'.format(symbol, size)
    return do_get(params)


def api_key_get(api, params, api_key, secret_key):
    method = 'GET'
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    params.update({'AccessKeyId': api_key,
                   'SignatureMethod': 'HmacSHA256',
                   'SignatureVersion': '2',
                   'Timestamp': timestamp})

    url = 'https://api.hbdm.com'
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

    url = 'https://api.hbdm.com'
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


def contract_account_info(api_key, secret_key, symbol=''):
    params = {}
    if (symbol != ''):
        params['symbol'] = symbol
    api = '/api/v1/contract_account_info'
    return api_key_post(api, params, api_key, secret_key)


def contract_position_info(api_key, secret_key, symbol=''):
    params = {}
    if (symbol != ''):
        params['symbol'] = symbol
    api = '/api/v1/contract_position_info'
    return api_key_post(api, params, api_key, secret_key)


def contract_order(symbol, contract_type, contract_code, price, volume,
                   direction, offset, lever_rate, order_price_type,
                   api_key, secret_key):
    params = {}
    params['symbol'] = symbol
    params['contract_type'] = contract_type
    params['price'] = price
    params['volume'] = volume
    params['direction'] = direction
    params['offset'] = offset
    params['lever_rate'] = lever_rate
    params['order_price_type'] = order_price_type
    if (contract_code !=''):
        params['contract_code'] = contract_code
    api = '/api/v1/contract_order'
    return api_key_post(api, params, api_key, secret_key)


def contract_cancel(symbol, api_key, secret_key, order_id=''):
    params = {}
    params['symbol'] = symbol
    if (order_id !=''):
        params['order_id'] = order_id
    api = '/api/v1/contract_cancel'
    return api_key_post(api, params, api_key, secret_key)


def contract_cancelall(symbol, api_key, secret_key):
    params = {}
    params['symbol'] = symbol
    api = '/api/v1/contract_cancelall'
    return api_key_post(api, params, api_key, secret_key)


def contract_order_info(symbol, api_key, secret_key, order_id=''):
    params = {}
    params['symbol'] = symbol
    if (order_id !=''):
        params['order_id'] = order_id
    api = '/api/v1/contract_order_info'
    return api_key_post(api, params, api_key, secret_key)


def contract_order_detail(symbol, order_id, created_at, order_type,
                          api_key, secret_key, page_index='', page_size=''):
    params = {}
    params['symbol'] = symbol
    params['order_id'] = order_id
    params['created_at'] = created_at
    params['order_type'] = order_type
    if (page_index !=''):
        params['page_index'] = page_index
    if (page_size !=''):
        params['page_size'] = page_size
    api = '/api/v1/contract_order_detail'
    return api_key_post(api, params, api_key, secret_key)


def contract_openorders(api_key, secret_key, symbol='',
                        page_index='', page_size=''):
    params = {}
    if (symbol !=''):
        params['symbol'] = symbol
    if (page_index !=''):
        params['page_index'] = page_index
    if (page_size !=''):
        params['page_index'] = page_index
    api = '/api/v1/contract_openorders'
    return api_key_post(api, params, api_key, secret_key)


def contract_hisorders(symbol, trade_type, type, status, create_date,
                       api_key, secret_key, page_index='', page_size=''):
    params = {}
    params['symbol'] = symbol
    params['trade_type'] = trade_type
    params['type'] = type
    params['status'] = status
    params['create_date'] = create_date
    if (page_index !=''):
        params['page_index'] = page_index
    if (page_size !=''):
        params['page_index'] = page_index
    api = '/api/v1/contract_hisorders'
    return api_key_post(api, params, api_key, secret_key)
