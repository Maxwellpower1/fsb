#coding=utf-8

import os
import ast
import time
import hmac
import json
import random
import aiohttp
import socket
import hashlib
import urllib3
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


async def do_async_get(api, params=''):
    url = 'https://api.binance.com/api/v1/{}{}'.format(api, params)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            true = True
            false = False
            result = await response.json(content_type=None)
            return result


async def async_ticker(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return await do_async_get('ticker/24hr', params)


async def async_depth(symbol, limit=10):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&limit={}'.format(symbol, limit)
    return await do_async_get('depth', params)


async def async_klines(symbol, interval, startTime, endTime, limit):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&interval={}&startTime={}&endTime={}&limit={}'.format(
             symbol, interval, startTime, endTime, limit)
    return await do_async_get('klines', params)


async def async_time():
    return await do_async_get('time')


def convert_symbol(symbol):
    return symbol.replace('_', '').upper()


def do_get(api, params=''):
	url = "https://api.binance.com/api/v1/"+api+params
	# headers = {'contentType': 'application/x-www-form-urlencoded'}
	response = requests.get(url, timeout=5)
	true = True
	false = False
	resp = response.content
	resp = resp.decode('utf-8')
	return ast.literal_eval(resp)


def ping():
	return do_get('ping')


def time():
	return do_get('time')


def exchange_info():
	return do_get('exchangeInfo')


def depth(symbol, limit=10):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&limit={}'.format(symbol, limit)
    return do_get('depth', params)


def trades(symbol, limit=10):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&limit={}'.format(symbol, limit)
    return do_get('trades', params)


def klines(symbol, interval, startTime, endTime, limit):
    symbol = convert_symbol(symbol)
    params = '?symbol={}&interval={}&startTime={}&endTime={}&limit={}'.format(
             symbol, interval, startTime, endTime, limit)
    return do_get('klines', params)


def ticker(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return do_get('ticker/24hr', params)


def ticker_24hr(symbol):
    symbol = convert_symbol(symbol)
    params = '?symbol={}'.format(symbol)
    return do_get('ticker/24hr', params)


def request(api, params, method, api_key, secret_key):
	url = "https://api.binance.com/api/v3/" + api
	headers = {'Accept': 'application/json',
			   'User-Agent': 'binance/python',
	           'X-MBX-APIKEY': api_key}

	# params_sig = '&'.join(["{}={}".format(d[0], d[1]) for d in params])

	# params['recvWindow'] = recvWindow
	# params['timestamp'] = int(time()['serverTime'])*1000
	params['timestamp'] = int(time()['serverTime'])
	query = urllib3.request.urlencode(sorted(params.items()))
	signature = hmac.new(secret_key.encode('utf-8'),
	                    msg=query.encode('utf-8'),
					    digestmod=hashlib.sha256).hexdigest()
	query += "&signature={}".format(signature)
	# sign = ''
	# for key in sorted(params.keys()):
	# 	sign += key + '=' + str(params[key]) +'&'
	# data = sign+'secret_key='+secret_key
	# sign = hashlib.md5(data.encode("utf8")).hexdigest().upper()
	# params.sort(key=itemgetter(0))
	# params['timestamp'] = int(time()['serverTime'] * 1000)
	# params['signature'] = signature
	url = url + '?' + query

	response = requests.request(method, url, headers=headers)

	true = True
	false = False
	resp = response.content
	# resp = resp.decode('utf-8')
	# resp = ast.literal_eval(resp)
	resp = eval(resp)
	return resp


def account(recvWindow, api_key, secret_key):
	api = "account"
	params ={'recvWindow':recvWindow}
	method = 'GET'
	return request(api, params, method, api_key, secret_key)


def new_order(symbol, side, type_, price, quantity, timeInForce,
              api_key, secret_key, newClientOrderId='', stopPrice=0,
		      icebergQty=0, newOrderRespType=''):
    symbol = convert_symbol(symbol)
    api = "order"
    params = {
        'symbol': symbol,
        'side': side,
        'type': type_,
        'quantity': quantity,
    }
    if type_ == 'LIMIT':
        params['timeInForce'] = timeInForce
        # params['price'] = price
        params['price'] = '{:.8f}'.format(float(price))
    if newClientOrderId:
        params['newClientOrderId'] = newClientOrderId
    if stopPrice:
        params['stopPrice'] = stopPrice
    if icebergQty:
        params['icebergQty'] = icebergQty
    if newOrderRespType:
        params['newOrderRespType'] = newOrderRespType
    method = 'POST'
    return request(api, params, method, api_key, secret_key)


def query_order(symbol, orderId, recvWindow, api_key, secret_key):
    symbol = convert_symbol(symbol)
    api = "order"
    params = {
        'symbol': symbol,
        'orderId': orderId,
        'recvWindow': recvWindow,
    }
    method = 'GET'
    return request(api, params, method, api_key, secret_key)


def cancel_order(symbol, orderId, recvWindow, api_key, secret_key):
    symbol = convert_symbol(symbol)
    api = "order"
    params = {
        'symbol': symbol,
        'orderId': orderId,
        'recvWindow': recvWindow,
    }
    method = 'DELETE'
    return request(api, params, method, api_key, secret_key)


def current_open_orders(symbol, recvWindow, api_key, secret_key):
    symbol = convert_symbol(symbol)
    api = "openOrders"
    params = {
        'symbol': symbol,
        'recvWindow': recvWindow,
    }
    method = 'GET'
    return request(api, params, method, api_key, secret_key)


def all_orders(symbol, startTime, endTime, limit,
               recvWindow, api_key, secret_key, orderId=''):
    symbol = convert_symbol(symbol)
    api = "allOrders"
    params = {
        'symbol': symbol,
        'startTime': startTime,
        'endTime': endTime,
        'limit': limit,
        'recvWindow': recvWindow,
    }
    if orderId:
        params['orderId'] = orderId
    method = 'GET'
    return request(api, params, method, api_key, secret_key)


def account_trade_list(symbol, startTime, endTime, limit,
                       recvWindow, api_key, secret_key, fromId=''):
    symbol = convert_symbol(symbol)
    api = "myTrades"
    params = {
        'symbol': symbol,
        'startTime': startTime,
        'endTime': endTime,
        'limit': limit,
        'recvWindow': recvWindow,
    }
    if orderId:
        params['orderId'] = orderId
    method = 'GET'
    return request(api, params, method, api_key, secret_key)
