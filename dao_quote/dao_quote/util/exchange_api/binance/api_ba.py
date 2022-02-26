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
    url = 'https://api3.binance.com/api/v1/{}{}'.format(api, params)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            true = True
            false = False
            result = await response.json(content_type=None)
            return result


async def async_ticker(symbol):
	params = '?symbol={}'.format(symbol)
	return await do_async_get('ticker/24hr', params)


async def async_depth(symbol, limit=10):
	params = '?symbol={}&limit={}'.format(symbol, limit)
	return await do_async_get('depth', params)


async def async_klines(symbol, interval, startTime, endTime, limit):
	params = '?symbol={}&interval={}&startTime={}&endTime={}&limit={}'.format(
	         symbol, interval, startTime, endTime, limit)
	return await do_async_get('klines', params)


async def async_time():
    return await do_async_get('time')


def do_get(api, params=''):
	url = "https://api3.binance.com/api/v1/"+api+params
	# headers = {'contentType': 'application/x-www-form-urlencoded'}
	response = requests.get(url, timeout=1)
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
	params = '?symbol={}&limit={}'.format(symbol, limit)
	return do_get('depth', params)


def trades(symbol, limit=10):
	params = '?symbol={}&limit={}'.format(symbol, limit)
	return do_get('trades', params)


def klines(symbol, interval, startTime, endTime, limit):
	params = '?symbol={}&interval={}&startTime={}&endTime={}&limit={}'.format(
	         symbol, interval, startTime, endTime, limit)
	return do_get('klines', params)


def ticker(symbol):
	params = '?symbol={}'.format(symbol)
	return do_get('ticker/24hr', params)


def ticker_24hr(symbol):
	params = '?symbol={}'.format(symbol)
	return do_get('ticker/24hr', params)
