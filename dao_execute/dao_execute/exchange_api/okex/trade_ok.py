# coding=utf-8

import time
import http.client
import urllib.request
import urllib.error
import urllib.parse
import OpenSSL

from dao_execute.exchange_api.okex import api_ok as api


def ticker(symbol):
    while True:
        try:
            return api.ticker(symbol)
        except (IOError, http.client.HTTPException,
                urllib.error.HTTPError, urllib.error.URLError,
                KeyError, SyntaxError, OpenSSL.SSL.ZeroReturnError):
            print("ticker error...")
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
            order_info_n = {'orders': []}
            order_id = order_info['order_id']
            order_dict = {}
            order_dict['order_id'] = order_id
            order_dict['amount'] = float(order_info['size'])
            order_dict['deal_amount'] = float(order_info['filled_size'])
            order_dict['avg_price'] = float(order_info['price_avg'])
            order_dict['status'] = int(order_info['state'])
            order_info_n['orders'].append(order_dict)
            if (int(order_id) == int(id)):
                return order_info_n
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
            print(result)
            order_id = result['order_id']
            result = result['result']
            if ((order_id == id) and result):
                order_result = True
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, SyntaxError):
            print('cancel_order Err...')
            time.sleep(0.1)
        except (KeyError):
            print('cancel_order failed, {}'.format(result))
            try:
                code = result['code']
                if (code == 33014):
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
