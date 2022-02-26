# coding=utf-8

import time
import http.client
import urllib.request
import urllib.error
import urllib.parse
import OpenSSL

from dao_execute.exchange_api.okcoin import api_okc as api


def ticker(symbol):
    while True:
        try:
            return api.ticker(symbol)
        except (IOError, http.client.HTTPException,
                urllib.error.HTTPError, urllib.error.URLError,
                KeyError, SyntaxError, OpenSSL.SSL.ZeroReturnError):
            print("ticker error...")
        time.sleep(0.1)


def depth(symbol, size):
    while True:
        try:
            return api.depth(symbol, size)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("depth error...")
        time.sleep(0.1)


def kline(symbol, type, size, since):
    while True:
        try:
            kline = api.kline(symbol, type, size, since)
            kline_test = float(kline[-2][4])
            return kline
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("kline error...")
        time.sleep(0.1)


def userinfo(api_key, secret_key):
    while True:
        try:
            return api.userinfo(api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("userinfo error...")
        time.sleep(0.4)


def fetch_order(symbol, id, api_key, secret_key):
    while True:
        order_result = False
        try:
            order_info = api.fetch_order(symbol, id, api_key, secret_key)
            if (len(order_info['orders']) == 0):
                order_dict = {}
                order_dict['order_id'] = id
                order_dict['deal_amount'] = 0.0
                order_dict['avg_price'] = 0.0
                order_dict['status'] = -1
                order_info['orders'].append(order_dict)
            else:
                pass
            order_id = order_info['orders'][0]['order_id']
            if (int(order_id) == int(id)):
                return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError):
            print('Network order_info Err...')
            time.sleep(0.1)


def cancel_order(symbol, id, api_key, secret_key):
    while True:
        if (int(id) == 0):
            order_result = True
            break
        order_result = False
        try:
            result = api.cancel_order(symbol, id, api_key, secret_key)
            order_id = result['order_id']
            if (order_id == id):
                order_result = True
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, SyntaxError):
            print('cancel_order Err...')
            time.sleep(0.1)
        except (KeyError):
            print('cancel_order failed, {}'.format(result))
            try:
                error_code = result['error_code']
                if (error_code == 10001):
                    pass
                else:
                    break
            except Exception as e:
                pass
    return order_result


def trade(symbol, tradetype, api_key, secret_key, price, amount):
    while True:
        status = False
        try:
            result = api.trade(symbol, tradetype, api_key, secret_key,
                               price, amount)
            print(result)
            id = result['order_id']
            status = result['result']
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, SyntaxError) as e:
            print('trade error...{}'.format(e))
            time.sleep(0.1)
        except (KeyError):
            print('trade failed, {}'.format(result))
            id = 0
            break
        if (status is True):
            break
    return id


def batch_trade(symbol, api_key, secret_key, orders_data):
    while True:
        status = False
        try:
            result = batch_trade(symbol, api_key, secret_key, orders_data)
            status = result['result']
            result = result['order_info']
        except Exception as e:
            print('batch_trade error')
        if (status is True):
            break
    return result
