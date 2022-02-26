# coding=utf-8

import json
import math
import redis


class ComputeDepth(object):

    def __init__(self, setting_dict):
        self.exchange = setting_dict['exchange']
        self.symbol = setting_dict['symbol']
        self.depth = setting_dict['depth']
        if ('.' in str(self.depth)):
            self.float_num = len(str(self.depth).split('.')[1])
        else:
            self.float_num = 0
        self.depthall_dict = {}
        self.depthall_dict['asks'] = {}
        self.depthall_dict['bids'] = {}
        self.depthall_combine_dict = {}
        self.depthall_combine_dict['asks'] = {}
        self.depthall_combine_dict['bids'] = {}

    def main(self):
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
        r = redis.StrictRedis(connection_pool=pool)
        p = r.pubsub()
        key_name = '{}_{}_depthall'.format(self.exchange, self.symbol)
        p.subscribe(key_name)
        for item in p.listen():
            if item['type'] == 'message':
                event_dict = item['data']
                r.set('s', 32)
                event_dict = json.loads(event_dict)
                event_type = event_dict['event_type']
                event_exchange = event_dict['exchange']
                event_symbol = event_dict['symbol']
                data = json.loads(event_dict['data'])
                if event_type == 'depthall':
                    self.on_depthall(data)

    def on_depthall(self, data):
        for i in data['asks']:
            price = float(i[0])
            if (float(i[1]) == 0.0):
                try:
                    del self.depthall_dict['asks'][price]
                except Exception as e:
                    pass
            else:
                self.depthall_dict['asks'][price] = float(i[1])
        for i in data['bids']:
            price = float(i[0])
            if (float(i[1]) == 0.0):
                try:
                    del self.depthall_dict['bids'][price]
                except Exception as e:
                    pass
            else:
                self.depthall_dict['bids'][price] = float(i[1])

        ask_price_list = sorted(self.depthall_dict['asks'].keys(), reverse=True)
        bid_price_list = sorted(self.depthall_dict['bids'].keys())
        for ask_price in ask_price_list:
            price = math.floor(ask_price / self.depth) * self.depth
            self.depthall_combine_dict['asks'][price] = \
                self.depthall_combine_dict['asks'].get(price, 0) + \
                self.depthall_dict['asks'][ask_price]
        for bid_price in bid_price_list:
            price = math.floor(bid_price / self.depth) * self.depth
            self.depthall_combine_dict['bids'][price] = \
                self.depthall_combine_dict['bids'].get(price, 0) + \
                self.depthall_dict['bids'][bid_price]

        ask_price_list = sorted(self.depthall_combine_dict['asks'].keys())
        bid_price_list = sorted(self.depthall_combine_dict['bids'].keys(), reverse=True)
        length = max(len(ask_price_list), len(bid_price_list))
        print('*'*30)
        print('bids  |   asks')
        for i in range(0, length):
            try:
                bid_price = bid_price_list[i]
                bid_vol = self.depthall_combine_dict['bids'][bid_price_list[length-i-1]]
            except Exception as e:
                bid_price = ''
                bid_vol = ''
            try:
                ask_price = ask_price_list[i]
                ask_vol = self.depthall_combine_dict['asks'][ask_price_list[i]]
            except Exception as e:
                ask_price = ''
                ask_vol = ''
            print('{}:{}  |  {}:{}'.format(bid_price, bid_vol, ask_price, ask_vol))
