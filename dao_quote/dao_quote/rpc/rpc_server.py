import sys
import json
import hmac
import hashlib
import thriftpy2
import traceback

from thriftpy2.rpc import make_server

from dao_quote.settings import config_x
from dao_quote.util.convert import convert
from dao_quote.util.quote_save import save_mongo
from dao_quote.util.quote_fetch import (quote_fetch, quote_manage)


class Dispatcher(object):

    def __init__(self):
        self.api_key_dict = config_x.API_KEY_DICT
        if self.api_key_dict == {}:
            print('[*] api_key_dict is null !')
            sys.exit(0)

    def check_sig(self, *args):
        req_sig = args[0]
        api_key, req_sig = req_sig.split('.')
        secret_key = self.api_key_dict.get(api_key, '')
        if secret_key == '':
            return False
        content = ','.join(args[1:])
        sig = hmac.new(secret_key.encode("utf8"),
                       msg=content.encode("utf8"),
                       digestmod=hashlib.sha256).hexdigest()
        if req_sig == sig:
            return True
        else:
            return False

    def ret_resp(self, status, data):
        resp = {}
        resp['status'] = status
        resp['data'] = data
        return json.dumps(resp)

    def get_ticker(self, sig, exchange, symbol):
        status = 0
        if self.check_sig(sig, 'get_ticker', exchange, symbol):
            try:
                data = quote_fetch.get_ticker_local(exchange, symbol)
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_kline(self, sig, exchange, symbol):
        status = 0
        if self.check_sig(sig, 'get_kline', exchange, symbol):
            try:
                data = quote_fetch.get_kline_local(exchange, symbol)
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_depth(self, sig, exchange, symbol):
        status = 0
        if self.check_sig(sig, 'get_depth', exchange, symbol):
            try:
                data = quote_fetch.get_depth_local(exchange, symbol)
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_spread_line(self, sig, exchange_a, symbol_a, exchange_b, symbol_b, period):
        status = 0
        if self.check_sig(sig, 'get_spread_line', exchange_a, symbol_a, exchange_b, symbol_b, period):
            try:
                data = quote_fetch.get_spread_line(exchange_a, symbol_a, exchange_b, symbol_b, period)
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_backtest_kline_db(self, sig, exchange, symbol, period, begin_timestamp, end_timestamp):
        status = 0
        if self.check_sig(sig, 'get_backtest_kline_db', exchange, symbol, period, begin_timestamp, end_timestamp):
            try:
                data = quote_fetch.get_backtest_kline_db(exchange, symbol, period, int(begin_timestamp), int(end_timestamp))
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_kline_db(self, sig, exchange, symbol, period, num, end_timestamp=''):
        status = 0
        if self.check_sig(sig, 'get_kline_db', exchange, symbol, period, num, end_timestamp):
            try:
                data = quote_fetch.get_kline_db(exchange, symbol, period, int(num), int(end_timestamp))
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_sqlite_klines_df(self, sig, exchange, symbol, begin_timestamp, end_timestamp):
        status = 0
        if self.check_sig(sig, 'get_sqlite_klines_df', exchange, symbol, begin_timestamp, end_timestamp):
            try:
                df = quote_fetch.get_sqlite_klines_df(exchange, symbol, int(begin_timestamp), int(end_timestamp))
                data = df.to_json(orient='split', force_ascii=False)
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_hfd(self, sig, exchange, symbol, type_list, begin_timestamp, end_timestamp):
        status = 0
        if self.check_sig(sig, 'get_hfd', exchange, symbol, type_list, begin_timestamp, end_timestamp):
            try:
                type_list = json.loads(type_list)
                db = save_mongo.get_db()
                data = quote_fetch.get_hfd(db, exchange, symbol, type_list, begin_timestamp, end_timestamp)
                status = 1
            except Exception as e:
                data = ['error: {}'.format(traceback.format_exc())]
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def get_trade_dict_list(self, sig, exchange, symbol, begin_timestamp, end_timestamp):
        status = 0
        if self.check_sig(sig, 'get_trade_dict_list', exchange, symbol, begin_timestamp, end_timestamp):
            try:
                db = save_mongo.get_db()
                data = quote_fetch.get_trade_dict_list(db, exchange, symbol, begin_timestamp, end_timestamp, json_format=False)
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)

    def download_dao_quote(self, sig, begin_time, end_time):
        status = 0
        if self.check_sig(sig, 'download_dao_quote', begin_time, end_time):
            begin_timestamp = int(convert.to_timestamp(begin_time)) * 1000
            end_timestamp = int(convert.to_timestamp(end_time)) * 1000
            try:
                db_name, shasum = quote_manage.get_db(begin_timestamp, end_timestamp)
                data = {}
                data['url'] = db_name
                data['shasum'] = shasum
                status = 1
            except Exception as e:
                data = 'err: {}'.format(traceback.format_exc())
        else:
            data = 'wrong sig'
        return self.ret_resp(status, data)


def run():
    host = '127.0.0.1'
    port = 9003
    print('[*] {}:{}, server running'.format(host, port))
    dq_thrift = thriftpy2.load("dao_quote/rpc/dao_quote.thrift", module_name="dq_thrift")
    server = make_server(dq_thrift.DaoQuote, Dispatcher(), host, port, client_timeout=10000)
    server.serve()
