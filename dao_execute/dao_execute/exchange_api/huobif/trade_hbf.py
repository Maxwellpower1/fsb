# coding=utf-8

import time
import datetime
import http.client
import urllib.request
import urllib.error
import urllib.parse
import __main__
import OpenSSL

from dao_execute.exchange_api.huobif import api_hbf as api


def market_history_kline(symbol, period, size):
    while True:
        try:
            return api.market_history_kline(symbol, period, size)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_history_kline error...")
        time.sleep(0.1)


def market_detail_merged(symbol):
    while True:
        try:
            return api.market_detail_merged(symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_detail_merged error...")
        time.sleep(0.1)


def market_depth(symbol, type):
    while True:
        try:
            return api.market_depth(symbol, type)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_depth error...")
        time.sleep(0.1)


def market_trade(symbol):
    while True:
        try:
            return api.market_trade(symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_trade error...")
        time.sleep(0.1)


def market_history_trade(symbol, size):
    while True:
        try:
            return api.market_history_trade(symbol, size)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_history_trade error...")
        time.sleep(0.1)


def contract_account_info(api_key, secret_key, symbol=''):
    while True:
        try:
            return api.contract_account_info(api_key, secret_key, symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("contract_account_info error...")
        time.sleep(0.3)


def contract_position_info(api_key, secret_key, symbol=''):
    while True:
        try:
            return api.contract_position_info(api_key, secret_key, symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("contract_position_info error...")
        time.sleep(0.4)


def contract_order(symbol, contract_type, contract_code, price,
                   volume,direction, offset, lever_rate,
                   order_price_type, api_key, secret_key):
    while True:
        status = False
        try:
            result = api.contract_order(symbol, contract_type, contract_code,
                                        price, volume, direction, offset,
                                        lever_rate, order_price_type,
                                        api_key, secret_key)
            order_id = result['data']['order_id']
            status = True
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError):
            print('orders_place error...')
            time.sleep(0.1)
        except (KeyError):
            print("Failed, " + str(result))
            order_id = 0
            break
        if status is True:
            break
    return order_id


def contract_cancel(symbol, api_key, secret_key, order_id=''):
    while True:
        order_result = False
        try:
            result = api.contract_cancel(symbol, api_key, secret_key, order_id)
            if (int(result['data']['successes']) == int(order_id)):
                order_result = True
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError):
            print('contract_cancel error...')
        except (NameError, KeyError):
            return False
            time.sleep(0.1)
    return order_result


def contract_cancelall(symbol, api_key, secret_key):
    while True:
        order_result = False
        try:
            result = api.contract_cancelall(symbol, api_key, secret_key)
            if (result['data']['successes'] != ''):
                order_result = True
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError):
            print('contract_cancelall error...')
        except (NameError, KeyError):
            return False
            time.sleep(0.1)
    return order_result


def contract_openorders(api_key, secret_key, symbol='',
                        page_index='', page_size=''):
    while True:
        order_result = False
        try:
            order_info = api.contract_openorders(api_key, secret_key, symbol,
                                                 page_index, page_size)
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('contract_openorders error...')
            time.sleep(0.1)


def contract_order_info(symbol, api_key, secret_key, order_id=''):
    while True:
        order_result = False
        try:
            order_info = api.contract_order_info(symbol, api_key, secret_key, order_id)
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('contract_order_info error...')
            time.sleep(0.3)
