# coding=utf-8

import os
import time
import hmac
import json
import base64
import socket
import random
import string
import aiohttp
import hashlib
import requests
import http.client
import urllib.error
import urllib.parse
import urllib.request


def do_get(params):
    url = "https://www.deribit.com/api/v2/public/{}".format(params)
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, headers=headers, timeout=3)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    return json.loads(resp)


def time_():
    params = 'time?'
    return do_get(params)


def test():
    params = 'test?'
    return do_get(params)


def ping():
    params = 'ping?'
    return do_get(params)


def get_announcements(currency, kind):
    params = 'get_announcements?'
    return do_get(params)


def get_book_summary_by_currency(currency, kind):
    params = 'get_book_summary_by_currency?currency={}&kind={}'.format(
             currency, kind)
    return do_get(params)


def get_book_summary_by_instrument(instrument_name):
    params = 'get_book_summary_by_instrument?instrument_name={}'.format(
             instrument_name)
    return do_get(params)


def get_contract_size(instrument_name):
    params = 'get_contract_size?instrument_name={}'.format(
             instrument_name)
    return do_get(params)


def get_currencies():
    params = 'get_currencies?'
    return do_get(params)


def get_funding_chart_data(instrument_name, length):
    params = 'get_funding_chart_data?instrument_name={}&length={}'.format(
             instrument_name, length)
    return do_get(params)


def get_historical_volatility(currency):
    params = 'get_historical_volatility?currency={}'.format(currency)
    return do_get(params)


def get_index(currency):
    params = 'get_index?currency={}'.format(currency)
    return do_get(params)


def get_instruments(currency, kind, expired):
    params = 'get_instruments?currency={}&kind={}&expired={}'.format(
             currency, kind, expired)
    return do_get(params)


def get_last_settlements_by_currency(currency, type, count):
    params = ('get_last_settlements_by_currency?currency={}&type={}&'
              'count={}').format(currency, type, count)
    return do_get(params)


def get_last_settlements_by_instrument(currency, type, count):
    params = ('get_last_settlements_by_instrument?currency={}&type={}&'
              'count={}').format(currency, type, count)
    return do_get(params)


def get_last_trades_by_currency(currency, kind, start_seq, end_seq,
                                count, include_old, sorting):
    params = ('get_last_trades_by_currency?currency={}').format(currency)
    if (kind != ''):
        params += '&kind={}'.format(kind)
    if (start_seq != ''):
        params += '&start_seq={}'.format(start_seq)
    if (end_seq != ''):
        params += '&end_seq={}'.format(end_seq)
    if (count != ''):
        params += '&count={}'.format(count)
    if (include_old != ''):
        params += '&include_old={}'.format(include_old)
    if (sorting != ''):
        params += '&sorting={}'.format(sorting)
    return do_get(params)


def get_last_trades_by_currency_and_time(currency, kind, start_timestamp,
                                         end_timestamp, include_old, sorting):
    params = ('get_last_trades_by_currency_and_time?currency={}&'
              'start_timestamp={}&end_timestamp={}').format(
              currency, start_timestamp, end_timestamp)
    if (kind != ''):
        params += '&kind={}'.format(kind)
    if (include_old != ''):
        params += '&include_old={}'.format(include_old)
    if (sorting != ''):
        params += '&sorting={}'.format(sorting)
    return do_get(params)


def get_last_trades_by_instrument(instrument_name, start_seq, end_seq,
                                  count, include_old, sorting):
    params = 'get_last_trades_by_instrument?instrument_name={}'.format(
              instrument_name)
    if (start_seq != ''):
        params += '&start_seq={}'.format(start_seq)
    if (end_seq != ''):
        params += '&end_seq={}'.format(end_seq)
    if (count != ''):
        params += '&count={}'.format(count)
    if (include_old != ''):
        params += '&include_old={}'.format(include_old)
    if (sorting != ''):
        params += '&sorting={}'.format(sorting)
    return do_get(params)


def get_last_trades_by_instrument_and_time(instrument_name, start_timestamp,
                                           end_timestamp, count, include_old,
                                           sorting):
    params = ('get_last_trades_by_instrument?instrument_name={}'
              '&start_timestamp={}&end_timestamp={}').format(
              instrument_name, start_timestamp, end_timestamp)
    if (count != ''):
        params += '&count={}'.format(count)
    if (include_old != ''):
        params += '&include_old={}'.format(include_old)
    if (sorting != ''):
        params += '&sorting={}'.format(sorting)
    return do_get(params)


def get_order_book(instrument_name, depth):
    params = 'get_order_book?instrument_name={}&depth={}'.format(
             instrument_name, depth)
    return do_get(params)


def get_trade_volumes():
    params = 'get_trade_volumes?'
    return do_get(params)


def ticker(instrument_name):
    params = 'ticker?instrument_name={}'.format(instrument_name)
    return do_get(params)


def request(api, method, params, api_key, secret_key):
    url = "https://www.deribit.com"
    headers = {'Content-Type': 'application/json'}
    timestamp = int(round(time.time(), 3) * 1000)
    nonce = ''.join(random.sample(string.ascii_letters + string.digits, 8))
    uri = '/api/v2/private/{}'.format(api)
    message = '{}\n{}\n{}\n{}\n{}\n'.format(
              timestamp, nonce, method, uri, params)
    signature = hmac.new(bytes(secret_key.encode('utf-8')),
                         msg=bytes(message.encode('utf-8')),
                         digestmod=hashlib.sha256).hexdigest()
    headers['Authorization'] = ('deri-hmac-sha256 id={},ts={},nonce={},'
                                'sig={}').format(api_key, timestamp,
                                                 nonce, signature)
    if method == 'GET':
        url += uri
        response = requests.get(url, headers=headers)
    else:
        response = requests.post(url, headers=headers, data=params)
    true = True
    false = False
    resp = response.content
    resp = resp.decode('utf-8')
    resp = json.loads(resp)
    return resp


def get_account_summary(currency, extended, api_key, secret_key):
    api = 'get_account_summary?currency={}&extended={}'.format(
          currency, extended)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def get_position(instrument_name, api_key, secret_key):
    api = 'get_position?instrument_name={}'.format(instrument_name)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def get_positions(currency, kind, api_key, secret_key):
    api = 'get_positions?currency={}&kind={}'.format(currency, kind)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def trade(side, instrument_name, amount, type, price, api_key, secret_key):
    api = '{}?instrument_name={}&amount={}&type={}&price={}'.format(
          side, instrument_name, amount, type, price)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def cancel(order_id, api_key, secret_key):
    api = 'cancel?order_id={}'.format(order_id)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def cancel_all(api_key, secret_key):
    api = 'cancel_all'
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def close_position(instrument_name, type, price, api_key, secret_key):
    api = 'close_position?instrument_name={}&type={}'.format(
          instrument_name, type)
    if (price != ''):
        api += '&price={}'.format(price)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)


def get_order_state(order_id, api_key, secret_key):
    api = 'get_order_state?order_id={}'.format(order_id)
    method = 'GET'
    params = ''
    return request(api, method, params, api_key, secret_key)
