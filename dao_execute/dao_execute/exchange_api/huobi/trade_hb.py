# coding=utf-8

import time
import datetime
import http.client
import urllib.request
import urllib.error
import urllib.parse
import __main__
import OpenSSL

from dao_execute.exchange_api.huobi import api_hb as api


def get_time():
    while True:
        try:
            return api.time()
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("get_time error...")
        time.sleep(0.1)


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


def market_tickers():
    while True:
        try:
            return api.market_tickers()
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_tickers error...")
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


def market_detail(symbol):
    while True:
        try:
            return api.market_detail(symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("market_detail error...")
        time.sleep(0.1)


def account(api_key, secret_key):
    while True:
        try:
            return api.account(api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("account error...")
        time.sleep(0.4)


def account_balance(account_id, api_key, secret_key):
    while True:
        try:
            return api.account_balance(account_id, api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("account_balance error...")
        time.sleep(0.4)


def account_balance_by_type(type, api_key, secret_key):
    while True:
        try:
            return api.account_balance_by_type(type, api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("account_balance_by_type error...")
        time.sleep(0.4)


def account_id_by_type(type, api_key, secret_key):
    while True:
        try:
            return api.account_id_by_type(type, api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("account_id_by_type error...")
        time.sleep(0.4)


def orders_place(symbol, type, price, amount, account_id,
                 source, api_key, secret_key):
    while True:
        status = False
        try:
            result = api.orders_place(symbol, type, price, amount, account_id,
                                      source, api_key, secret_key)
            print(result)
            order_id = result['data']
            status = True
            # status = result['result']
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError):
            print('Network  orders_place Err...')
            time.sleep(0.1)
        except (KeyError):
            print("Failed, " + str(result))
            # if result['error_code'] == 1003:
            id = 0
            break
        if status is True:
            break
    return order_id


def open_orders(side, size, api_key, secret_key, symbol='', account_id=''):
    while True:
        order_result = False
        try:
            order_info = api.open_orders(side, size, api_key, secret_key,
                                         symbol, account_id)
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('Network open_orders Err...')
            time.sleep(0.1)


def submit_cancel(order_id, api_key, secret_key):
    while True:
        order_result = False
        try:
            result = api.submit_cancel(order_id, api_key, secret_key)
            if (int(result['data']) == int(order_id)):
                order_result = True
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError):
            print('Network submit_cancel Err...')
        except (NameError, KeyError):
            return False
            time.sleep(0.1)
    return order_result


# def batch_cancel(order_ids, api_key, secret_key):
#     while True:
#         order_result = False
#         try:
#             order_info = api.submit_cancel(order_id, api_key, secret_key)
#             return order_info
#         except (IOError, http.client.HTTPException, urllib.error.HTTPError,
#                 urllib.error.URLError, KeyError):
#             print('Network batch_cancel Err...')
#             time.sleep(0.1)


def fetch_order(order_id, api_key, secret_key):
    while True:
        order_result = False
        try:
            order_info = api.fetch_order(order_id, api_key, secret_key)
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('Network fetch_order Err...')
            time.sleep(0.1)
