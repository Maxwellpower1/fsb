# coding=utf-8

import time
import datetime
import http.client
import urllib.error
import urllib.parse
import urllib.request
import OpenSSL
import __main__

from dao_execute.exchange_api.okexf import api_okf as api


def future_userinfo(api_key, secret_key):
    while True:
        try:
            return api.future_userinfo(api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("future_userinfo error...")
            time.sleep(0.3)


def future_position_4fix(symbol, api_key, secret_key, contract_type, type):
    while True:
        try:
            return api.future_position_4fix(symbol, api_key, secret_key,
                   contract_type, type)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("future_position_4fix error...")
            time.sleep(0.3)


def fetch_order(symbol, id, api_key, secret_key, contract_type):
    order_id = id
    symbol = '{}-{}'.format(symbol, contract_type)
    try:
        result = api.future_fetch(symbol, order_id, api_key, secret_key)
        result['amount'] = float(result['size'])
        result['deal_amount'] = float(result['filled_qty'])
        result['price_avg'] = float(result['price_avg'])
        result['status'] = int(result['state'])
        result = {'orders': [result]}
    except (IOError, http.client.HTTPException, urllib.error.HTTPError,
            urllib.error.URLError, KeyError, SyntaxError):
        result = 'wait'
        time.sleep(0.3)
    return result


def future_cancel(symbol, id, api_key, secret_key, contract_type):
    order_id = id
    symbol = '{}-{}'.format(symbol, contract_type)
    while True:
        order_result = False
        try:
            result = api.future_cancel(symbol, order_id, api_key, secret_key)
            order_id = result['order_id']
            order_result = result['result']
            error_code = result['error_code']
            if (((int(order_id) == int(id)) and order_result) or (error_code == '32004')):
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError):
            time.sleep(0.5)
            if ',' in str(id):
                break
            else:
                error_code = result['error_code']
                if error_code:
                    break
    return order_result


def future_trade(symbol, type, api_key, secret_key, contract_type,
                 match_price, amount, price):
    size = str(int(amount))
    symbol = '{}-{}'.format(symbol, contract_type)
    while True:
        error_code = 1
        try:
            result = api.future_trade(symbol, type, price, size, match_price,
                                      api_key, secret_key)
            id = int(result['order_id'])
            error_code = int(result['error_code'])
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, SyntaxError):
            print('future_trade error...')
            time.sleep(0.3)
        except (KeyError):
            print(("future_trade error, {}".format(result)))
            id = 0
            break
        if (error_code == 0):
            break
    return id
