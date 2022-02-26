import os
import ast
import sys
import hmac
import json
import uuid
import hashlib
import thriftpy2
import traceback

from thriftpy2.rpc import make_client

from dao_execute.settings.config import cfg


class DaoExecute(object):

    def __init__(self):
        self.source = 'dao_web'
        rpc_node = cfg['rpc_node']
        file_path = os.path.split(os.path.realpath(__file__))[0]
        filename = '{}/dao_execute.thrift'.format(file_path)
        de_thrift = thriftpy2.load(filename, module_name='de_thrift')
        self.de_thrift = make_client(de_thrift.DaoExecute, rpc_node['ip'], rpc_node['port'], timeout=10000)
        self.rpc_token = cfg['rpc_token']['dao_web']

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

    def execute_order(self, user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num, exec_ts, strategy_instance_id, close_today):
        status = 1
        try:
            sig = self.make_sig('execute_order', user_id, exchange,
                                account_type, strategy_name, symbol,
                                order_type, price, amount, money_num,
                                exec_ts, strategy_instance_id, str(close_today))
            resp = self.de_thrift.execute_order(sig, user_id, exchange,
                   account_type, strategy_name, symbol, order_type, price,
                   amount, money_num, exec_ts, strategy_instance_id,
                   close_today)
            status, data = self.load_resp(resp)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def fetch_orders(self, user_id, exchange, account_type, strategy_name, symbol, order_id):
        status = 1
        try:
            sig = self.make_sig('fetch_orders', user_id, exchange,
                                account_type, strategy_name, symbol, order_id)
            resp = self.de_thrift.fetch_orders(sig, user_id, exchange,
                                account_type, strategy_name, symbol, order_id)
            status, data = self.load_resp(resp)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def get_orders(self, user_id, exchange, account_type, strategy_name, symbol, order_status, page_num, page_limit):
        status = 1
        try:
            sig = self.make_sig('get_orders', user_id, exchange,
                                account_type, strategy_name, symbol,
                                order_status, page_num, page_limit)
            resp = self.de_thrift.get_orders(sig, user_id, exchange,
                   account_type, strategy_name, symbol,
                   order_status, page_num, page_limit)
            status, data = self.load_resp(resp)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def get_strategy_orders(self, user_id, strategy_instance_id, order_status, page_num, page_limit):
        status = 1
        try:
            sig = self.make_sig('get_strategy_orders', user_id,
                                strategy_instance_id, order_status,
                                page_num, page_limit)
            resp = self.de_thrift.get_strategy_orders(sig, user_id,
                   strategy_instance_id, order_status, page_num, page_limit)
            status, data = self.load_resp(resp)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def cancel_order(self, user_id, exchange, account_type, strategy_name, symbol, order_id):
        status = 1
        try:
            sig = self.make_sig('cancel_order', user_id, exchange,
                                account_type, strategy_name, symbol, order_id)
            resp = self.de_thrift.cancel_order(sig, user_id, exchange,
                   account_type, strategy_name, symbol, order_id)
            status, data = self.load_resp(resp)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data
