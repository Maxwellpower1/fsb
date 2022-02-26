import time
import json
import hmac
import base64
import hashlib
import datetime
import requests


class ApiOkf(object):

    def __init__(self):
        self.base_url = 'https://www.okex.com'
        self.symbol_dict = {}
        self.fresh_symbol_dict()

    def instruments(self, instType='FUTURES'):
        api = '/api/v5/public/instruments?instType={}'.format(instType)
        params = {}
        resp = self.do_get(api, params)
        instrument_list = resp['data']
        return instrument_list

    def tickers(self, instType='FUTURES'):
        api = '/api/v5/market/tickers?instType={}'.format(instType)
        params = {}
        resp = self.do_get(api, params)
        return resp['data']

    def ticker(self, symbol, instType='FUTURES'):
        instId = self.process_symbol(symbol)
        api = '/api/v5/market/ticker?instId={}'.format(instId)
        params = {}
        resp = self.do_get(api, params)
        return resp['data']

    def books(self, symbol, size=9):
        instId = self.process_symbol(symbol)
        api = '/api/v5/market/books?instId={}&sz={}'.format(instId, size)
        params = {}
        resp = self.do_get(api, params)
        return resp['data']

    def candles(self, symbol, period='1m', num='100'):
        instId = self.process_symbol(symbol)
        api = '/api/v5/market/candles?instId={}&bar={}&limit={}'.format(
              instId, period, num)
        params = {}
        resp = self.do_get(api, params)
        return resp['data']

    def do_get(self, api, params):
        url = self.base_url + api
        resp = requests.get(url)
        return resp.json()

    def request(self, api, method, params, api_key, secret_key):
        secret_key, passphrase = secret_key.split('-')
        request_path = api
        timestamp = self.shift_time_v3(time.time())
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['OK-ACCESS-KEY'] = api_key
        headers['OK-ACCESS-TIMESTAMP'] = timestamp
        headers['OK-ACCESS-PASSPHRASE'] = passphrase

        if str(params) == '{}' or str(params) == 'None':
            params = ''
        if method == 'GET':
            params = ''
            url = self.base_url + request_path
        if method == 'POST':
            request_path += '?'
            for key, value in params.items():
                request_path = request_path + str(key) + '=' + str(value) + '&'
            request_path = request_path[0:-1]
            params = json.dumps(params)

        message = '{timestamp}{method}{request_path}{params}'.format(
                   timestamp=timestamp, method=method,
                   request_path=request_path, params=params)

        signature = hmac.new(bytes(secret_key.encode('utf-8')),
                             msg=bytes(message.encode('utf-8')),
                             digestmod=hashlib.sha256).digest()

        headers['OK-ACCESS-SIGN'] = base64.b64encode(signature)

        if method == 'GET':
            resp = requests.get(url, headers=headers)
        if method == 'POST':
            url = self.base_url + request_path
            resp = requests.post(url, headers=headers, data=params)
        return resp.json()

    def balances(self, api_key, secret_key, coin=''):
        api = '/api/v5/asset/balances'
        if coin != '':
            api += '?ccy={}'.format(coin)
        method = 'GET'
        params = {}
        resp = self.request(api, method, params, api_key, secret_key)
        return resp['data']

    def balance(self, api_key, secret_key, coin=''):
        api = '/api/v5/account/balance'
        if coin != '':
            api += '?ccy={}'.format(coin)
        method = 'GET'
        params = {}
        resp = self.request(api, method, params, api_key, secret_key)
        return resp['data']

    def positions(self, api_key, secret_key, symbol='', instType='FUTURES'):
        api = '/api/v5/account/positions'
        if instType != '':
            api += '?instType={}'.format(instType)
        if symbol != '':
            instId = self.process_symbol(symbol)
            api += '&instId={}'.format(instId)
        method = 'GET'
        params = {}
        resp = self.request(api, method, params, api_key, secret_key)
        return resp['data']

    def future_trade(self, symbol, type, price, size, api_key, secret_key):
        api = '/api/v5/trade/order'
        method = 'POST'

        type_list = type.split('_')
        posSide = type_list[-1]
        if 'going_long' in type:
            side = 'buy'
        elif 'close_long' in type:
            side = 'sell'
        elif 'going_short' in type:
            side = 'sell'
        elif 'close_short' in type:
            side = 'buy'

        params = {}
        params['instId'] = self.process_symbol(symbol)
        params['tdMode'] = 'isolated'
        params['side'] = side
        params['posSide'] = posSide
        params['ordType'] = type_list[0]
        params['sz'] = size
        params['px'] = price
        resp = self.request(api, method, params, api_key, secret_key)
        return resp['data']

    def future_cancel(self, symbol, order_id, api_key, secret_key):
        api = '/api/v5/trade/cancel-order'
        method = 'POST'
        params = {}
        params['instId'] = self.process_symbol(symbol)
        params['ordId'] = order_id
        resp = self.request(api, method, params, api_key, secret_key)
        return resp['data']

    def fetch_order(self, symbol, order_id, api_key, secret_key):
        api = '/api/v5/trade/order'
        api += '?instId={}'.format(self.process_symbol(symbol))
        api += '&ordId={}'.format(order_id)
        method = 'GET'
        params = {}
        resp = self.request(api, method, params, api_key, secret_key)
        return resp['data']

    def fresh_symbol_dict(self):
        instrument_list = self.instruments()
        expTime = time.time()* 1000
        for instrument in instrument_list:
            alias = instrument['alias']
            key = '{}-{}'.format(instrument['uly'].lower().replace('-', '_'), alias)
            instrument_id = instrument['instId']
            self.symbol_dict[key] = instrument_id
            if (alias == 'this_week'):
                expTime = instrument['expTime']
        self.symbol_dict['expire_time'] = int(expTime)

    def process_symbol(self, symbol):
        try:
            expire_time = self.symbol_dict['expire_time']
            if (time.time()*1000 > expire_time):
                self.fresh_symbol_dict()
            symbol = self.symbol_dict[symbol]
        except Exception as e:
            self.fresh_symbol_dict()
            symbol = self.symbol_dict[symbol]
        return symbol

    def shift_time_v3(self, timestamp):
        format = '%Y-%m-%dT%H:%M:%S.%fZ'
        iso_time = datetime.datetime.utcfromtimestamp(timestamp).strftime(format)
        iso_time = iso_time[:-4] + 'Z'
        return iso_time
