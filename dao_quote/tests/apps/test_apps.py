# coding=utf-8

import json
import hmac
import hashlib
import requests
import pathmagic

from dao_quote.util.convert import convert
from dao_quote.settings import (config, config_x)


class testRestAPI(object):
    def __init__(self):
        self.dao_quote_url = 'http://127.0.0.1:8003/dao_quote/api/v1/'
        self.api_key = 'dao_backtest'
        self.secret_key = config_x.API_KEY_DICT[self.api_key]

    def do_post(self, quote_param):
        import time
        quote_param['api_key'] = self.api_key
        content = json.dumps(quote_param)
        sig = hmac.new(self.secret_key.encode("utf8"),
                       msg=content.encode("utf8"),
                       digestmod=hashlib.sha256).hexdigest()
        quote_param['signature'] = sig
        r = requests.post(url=self.dao_quote_url, data=quote_param)
        info = r.json()
        data = json.loads(info['data'])
        return data

    def test_get_trade_dict_list(self):
        method = 'get_trade_dict_list'
        # exchange = 'okexf'
        # symbol = 'btc_usd-quarter'
        exchange = 'ctp'
        symbol = 'FG105'
        begin_time = '2021-02-03 09:00:00'
        end_time = '2021-02-03 09:01:00'
        begin_timestamp = int(convert.to_timestamp(begin_time))
        end_timestamp = int(convert.to_timestamp(end_time))

        quote_param = {}
        quote_param['exchange'] = exchange
        quote_param['symbol'] = symbol
        quote_param['begin_timestamp'] = str(begin_timestamp)
        quote_param['end_timestamp'] = str(end_timestamp)
        quote_param['method'] = method
        trade_dict_list = self.do_post(quote_param)
        for trade_dict in trade_dict_list:
            print(trade_dict)


def main():
    test_rest_api = testRestAPI()
    test_rest_api.test_get_trade_dict_list()


if __name__ == '__main__':
    main()
