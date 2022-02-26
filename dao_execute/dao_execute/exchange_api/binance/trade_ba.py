#coding=utf-8

import time
import datetime
import __main__
import OpenSSL
import http.client
import urllib.request
import urllib.error
import urllib.parse

from dao_execute.exchange_api.binance import api_ba as api


def ping():
    while True:
        try:
            return api.ping()
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("ping error...")
        time.sleep(0.1)


def get_time():
    while True:
        try:
            return api.time()
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("get_time error...")
        time.sleep(0.1)


def exchange_info():
    while True:
        try:
            return api.exchange_info()
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("exchange_info error...")
        time.sleep(0.1)


def depth(symbol, limit=10):
    while True:
        try:
            return api.depth(symbol, limit)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("depth error...")
        time.sleep(0.1)


def trades(symbol, limit=10):
    while True:
        try:
            return api.trades(symbol, limit)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("trades error...")
        time.sleep(0.1)


def klines(symbol, interval, startTime, endTime, limit):
    while True:
        try:
            klines = api.klines(symbol, interval, startTime, endTime, limit)
            kline = klines[-1]
            test_kline = [float(kline[0])/1000, float(kline[1]),
                          float(kline[2]), float(kline[3]), float(kline[4]),
                          float(kline[5]), float(kline[6])]
            return klines
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError, ValueError,
                OpenSSL.SSL.ZeroReturnError):
            print("klines error...")
        time.sleep(0.1)


def ticker(symbol):
    while True:
        try:
            return api.ticker(symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("ticker error...")
        time.sleep(0.1)


def ticker_24hr(symbol):
    while True:
        try:
            return api.ticker_24hr(symbol)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("ticker error...")
        time.sleep(0.1)


def account(recvWindow, api_key, secret_key):
    while True:
        try:
            return api.account(recvWindow, api_key, secret_key)
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError,
                OpenSSL.SSL.ZeroReturnError):
            print("account error...")
        time.sleep(0.4)


def new_order(symbol, side, type_, price, quantity, timeInForce,
              api_key, secret_key, newClientOrderId='', stopPrice=0,
		      icebergQty=0, newOrderRespType=''):
    while True:
        status = False
        try:
            result = api.new_order(symbol, side, type_, price,
                                   quantity, timeInForce,
                                   api_key, secret_key,
                                   newClientOrderId='', stopPrice=0,
		                           icebergQty=0, newOrderRespType='')
            orderId = result['orderId']
            status = True
            # status = result['result']
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError):
            print('new_order error...')
            time.sleep(0.1)
        except (KeyError):
            print("Failed, " + str(result))
            # if result['error_code'] == 1003:
            orderId = 0
            break
        if status == True:
            break
    return orderId


def query_order(symbol, orderId, recvWindow, api_key, secret_key):
    while True:
        order_result = False
        order_info = {}
        try:
            order_info = api.query_order(symbol, orderId, recvWindow,
                                         api_key, secret_key)
            orderId_new = order_info['orderId']
            if orderId_new == int(orderId):
                return order_info
            else:
                pass
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            try:
                code = order_info['code']
                if (code == -2013):
                    order_info['status'] = 'CANCELED'
                    order_info['executedQty'] = 0
                    return order_info
                else:
                    pass
            except Exception as e:
                pass
            print('order_info error...')
            time.sleep(0.1)


def cancel_order(symbol, orderId, recvWindow, api_key, secret_key):
    while True:
        order_result = False
        try:
            order_info = api.cancel_order(symbol, orderId, recvWindow,
                                         api_key, secret_key)
            # print(order_info)
            try:
                orderId_new = order_info['orderId']
                if orderId_new == int(orderId):
                    return True
            except Exception as e:
                if str(order_info['msg']) == 'UNKNOWN_ORDER':
                    return True
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('order_info error...')
            time.sleep(0.1)


def current_open_orders(symbol, recvWindow, api_key, secret_key):
    while True:
        try:
            order_info = api.current_open_orders(symbol, recvWindow,
                                                 api_key, secret_key)
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('current_open_orders error...')
            time.sleep(0.1)


def all_orders(symbol, startTime, endTime, limit,
               recvWindow, api_key, secret_key, orderId=''):
    while True:
        order_result = False
        try:
            order_info = api.all_orders(symbol, startTime, endTime, limit,
                                        recvWindow, api_key, secret_key,
                                        orderId='')
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('current_open_orders error...')
            time.sleep(0.1)


def account_trade_list(symbol, startTime, endTime, limit,
                       recvWindow, api_key, secret_key, fromId=''):
    while True:
        order_result = False
        try:
            order_info = api.account_trade_list(symbol, startTime, endTime,
                                                limit, recvWindow, api_key,
                                                secret_key, orderId='')
            return order_info
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError):
            print('current_open_orders error...')
            time.sleep(0.1)
