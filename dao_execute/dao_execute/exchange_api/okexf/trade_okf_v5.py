# coding=utf-8

import time
import datetime
import http.client
import urllib.error
import urllib.parse
import urllib.request
import OpenSSL
import __main__

from dao_execute.exchange_api.okexf import api_okf_v5 as api


def fetch_order(symbol, order_id, api_key, secret_key):
    v5_api = api.ApiOkf()
    try:
        result = v5_api.fetch_order(symbol, order_id, api_key, secret_key)
        result = result[0]
        result_ret = {}
        result_ret['amount'] = float(result['sz'])
        result_ret['deal_amount'] = float(result['accFillSz'])
        if result['avgPx'] == '':
            result_ret['price_avg'] = 0
        else:
            result_ret['price_avg'] = float(result['avgPx'])
        result_ret['status'] = result['state']
        result = {'orders': [result_ret]}
    except (IOError, http.client.HTTPException, urllib.error.HTTPError,
            urllib.error.URLError, KeyError, SyntaxError):
        result = 'wait'
        time.sleep(0.3)
    return result


def future_cancel(symbol, order_id, api_key, secret_key):
    v5_api = api.ApiOkf()
    while True:
        order_result = False
        try:
            result = v5_api.future_cancel(symbol, order_id, api_key, secret_key)
            result = result[0]
            print(result)
            order_id = result['ordId']
            error_code = result['sCode']
            if (error_code == '0'):
                order_result = True
                break
            elif error_code in ['51400', '51401', '51402']:
                order_result = True
                break
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, KeyError, SyntaxError):
            time.sleep(0.5)
            print('future_cancel failed')
    return order_result


def future_trade(symbol, type, api_key, secret_key, amount, price):
    v5_api = api.ApiOkf()
    while True:
        error_code = '1'
        try:
            result = v5_api.future_trade(symbol, type, price, amount, api_key, secret_key)
            result = result[0]
            print(result)
            order_id = result['ordId']
            error_code = result['sCode']
        except (IOError, http.client.HTTPException, urllib.error.HTTPError,
                urllib.error.URLError, SyntaxError):
            print('future_trade error...')
            time.sleep(0.3)
        except (KeyError):
            print(("future_trade error, {}".format(result)))
            order_id = 0
            break
        if (error_code in ['0', '51112', '51006', '51008']):
            break
        if order_id == '':
            order_id = 0
            break
    return order_id
