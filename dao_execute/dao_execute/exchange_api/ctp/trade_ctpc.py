import os
import time
import json
import traceback
import thriftpy2

from thriftpy2.rpc import make_client

from dao_execute.settings.config import cfg


class TradeCtp(object):

    def __init__(self):
        ctp_rpc = cfg['ctp_rpc']
        file_path = os.path.split(os.path.realpath(__file__))[0]
        filename = '{}/trade_ctp.thrift'.format(file_path)
        ctp_thrift = thriftpy2.load(filename, module_name='ctp_thrift')
        self.ctp_thrift = make_client(ctp_thrift.TradeCtp, ctp_rpc['host'], ctp_rpc['port'], timeout=10000)

    def load_resp(self, resp):
        resp = json.loads(resp)
        status = resp['status']
        data = resp['data']
        return status, data

    def execute_order(self, user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num, exec_ts, strategy_instance_id, close_today):
        status = 1
        try:
            resp = self.ctp_thrift.execute_order(user_id, exchange,
                   account_type, strategy_name, symbol, order_type, price,
                   amount, money_num, exec_ts, strategy_instance_id,
                   close_today)
            status, data = self.load_resp(resp)
            print(status, data)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data

    def cancel_order(self, user_id, exchange, account_type, strategy_name, symbol, order_id):
        status = 1
        try:
            resp = self.ctp_thrift.cancel_order(user_id, exchange,
                   account_type, strategy_name, symbol, order_id)
            status, data = self.load_resp(resp)
        except Exception as e:
            status = 0
            data = 'err: {}'.format(traceback.format_exc())
        return status, data
