import os
import ast
import hmac
import json
import hashlib
import thriftpy2
import traceback

from thriftpy2.rpc import make_client

from dao_web.settings.config import cfg
from dao_web.db.redis import RedisClient


class DaoQuote(object):

    def __init__(self):
        self.source = 'dao_web'
        rpc_cfg = cfg['rpc']['dao_quote']
        self.rpc_enable = rpc_cfg['enable']
        if self.rpc_enable:
            file_path = os.path.split(os.path.realpath(__file__))[0]
            filename = '{}/dao_quote.thrift'.format(file_path)
            dq_thrift = thriftpy2.load(filename, module_name='dq_thrift')
            host, port = rpc_cfg['addr'].split(':')
            self.dq_thrift = make_client(dq_thrift.DaoQuote, host, int(port))
            self.rpc_token = cfg['rpc']['dao_quote']['token']
        self.redis = RedisClient(cfg['redis']['dao_quote'])

    def make_sig(self, *args):
        content = ','.join(args)
        sig = hmac.new(self.rpc_token.encode("utf8"),
                       msg=content.encode("utf8"),
                       digestmod=hashlib.sha256).hexdigest()
        sig = '{}.{}'.format(self.source, sig)
        return sig

    def load_resp(self, resp):
        resp = json.loads(resp)
        status = resp['status']
        data = resp['data']
        return status, data

    def get_ticker(self, exchange, symbol):
        status = 1
        try:
            if self.rpc_enable:
                sig = self.make_sig('get_ticker', exchange, symbol)
                resp = self.dq_thrift.get_ticker(sig, exchange, symbol)
                status, data = self.load_resp(resp)
            else:
                key_name = '{}_{}_{}'.format(exchange, symbol, 'ticker')
                value = self.redis.get_value(key_name)
                data = ast.literal_eval(value)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def get_kline(self, exchange, symbol):
        status = 1
        try:
            if self.rpc_enable:
                sig = self.make_sig('get_kline', exchange, symbol)
                resp = self.dq_thrift.get_kline(sig, exchange, symbol)
                status, data = self.load_resp(resp)
            else:
                key_name = '{}_{}_{}'.format(exchange, symbol, 'kline')
                value = self.redis.get_value(key_name)
                data = ast.literal_eval(value)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def get_depth(self, exchange, symbol):
        status = 1
        try:
            if self.rpc_enable:
                sig = self.make_sig('get_depth', exchange, symbol)
                resp = self.dq_thrift.get_depth(sig, exchange, symbol)
                status, data = self.load_resp(resp)
            else:
                key_name = '{}_{}_{}'.format(exchange, symbol, 'depth')
                value = self.redis.get_value(key_name)
                data = ast.literal_eval(value)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def get_spread_line(self, exchange_a, symbol_a, exchange_b, symbol_b, period):
        status = 1
        try:
            if self.rpc_enable:
                sig = self.make_sig('get_spread_line', exchange_a, symbol_a, exchange_b, symbol_b, period)
                resp = self.dq_thrift.get_spread_line(sig, exchange_a, symbol_a, exchange_b, symbol_b, period)
                status, data = self.load_resp(resp)
            else:
                data = []
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def get_backtest_kline_db(self, exchange, symbol, period, begin_timestamp, end_timestamp):
        status = 1
        try:
            if self.rpc_enable:
                sig = self.make_sig('get_backtest_kline_db', exchange, symbol, period, begin_timestamp, end_timestamp)
                resp = self.dq_thrift.get_backtest_kline_db(sig, exchange, symbol, period, begin_timestamp, end_timestamp)
                status, data = self.load_resp(resp)
            else:
                data = []
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data
