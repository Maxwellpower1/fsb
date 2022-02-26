# coding=utf-8

import os
import ast
import hmac
import json
import time
import random
import socket
import aiohttp
import hashlib
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


async def do_async_get(sec_type, symbol, other=''):
    url = 'https://www.okex.com/api/v1/{}?symbol={}{}'.format(
          sec_type, symbol, other)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            true = True
            false = False
            result = await response.json()
            return result


async def async_future_ticker(symbol, contract_type):
    other = '&contract_type={}'.format(contract_type)
    return await do_async_get('future_ticker.do', symbol, other)


async def async_future_depth(symbol, contract_type, size):
    other = '&contract_type={}&size={}'.format(contract_type, size)
    return await do_async_get('future_depth.do', symbol, other)


async def async_future_kline(symbol, type, contract_type, size, since):
    other = '&type={}&contract_type={}&size={}&since={}'.format(
            type, contract_type, size, since)
    return await do_async_get('future_kline.do', symbol, other)


def do_get(sec_type, symbol, other=''):
    url = ('https://www.okex.com/api/v1/'
           '{}?symbol={}{}').format(sec_type, symbol, other)
    headers = {'contentType': 'application/x-www-form-urlencoded'}
    response = requests.get(url, headers=headers, timeout=1)
    resp = response.content
    resp = resp.decode('utf-8')
    resp = resp.replace("true", "True").replace("false", "False").replace("null", "None")
    return ast.literal_eval(resp)


def future_ticker(symbol, contract_type):
    other = '&contract_type={}'.format(contract_type)
    return do_get('future_ticker.do', symbol, other)


def future_depth(symbol, contract_type, size):
    other = '&contract_type={}&size={}'.format(contract_type, size)
    return do_get('future_depth.do', symbol, other)


def future_kline(symbol, type, contract_type, size, since):
    other = '&type={}&contract_type={}&size={}&since={}'.format(
            type, contract_type, size, since)
    return do_get('future_kline.do', symbol, other)


def main():
    print('test ok! ')


if __name__ == '__main__':
    main()
