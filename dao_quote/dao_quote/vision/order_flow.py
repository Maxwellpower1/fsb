# coding=utf-8

import time
import json
import redis
import datetime
from colorama import Fore

from dao_quote.settings import config


class OrderFlow(object):

    def __init__(self, print_msg=True):
        self.print_msg = print_msg
        if self.print_msg:
            host = config.REDIS_HOST
            port = config.REDIS_PORT
            pool = redis.ConnectionPool(host=host, port=port, db=0)
            self.redis = redis.StrictRedis(connection_pool=pool)

        COMPUTE_DICT = config.COMPUTE_DICT
        self.last_tick = {}
        self.get_tick_type_dict()
        self.get_handicap_dict()

    def red(self, data_str):
        return Fore.RED + data_str + Fore.RESET

    def green(self, data_str):
        return Fore.GREEN + data_str + Fore.RESET

    def main(self, key_name):
        p = self.redis.pubsub()
        p.subscribe(key_name)
        for item in p.listen():
            if item['type'] == 'message':
                event_dict = item['data']
                self.redis.set('s', 32)
                event_dict = json.loads(event_dict)
                event_type = event_dict['event_type']
                # key_name = event_dict['key_name']
                data = json.loads(event_dict['data'])
                if event_type == 'ticker':
                    self.analyze_tick(data)
                elif event_type == 'trade':
                    self.analyze_trade(data)
                else:
                    print(data)

    def analyze_trade(self, data):
        ts = data['ts'] / 1000
        dt = datetime.datetime.fromtimestamp(ts)
        msg = '{} : {} {}'.format(data['price'], data['size'], data['side'])
        if data['side'] == 'buy':
            msg = self.red(msg)
        elif data['side'] == 'sell':
            msg = self.green(msg)
        msg = '{}, {}'.format(dt, msg)
        print(msg)

    def analyze_tick(self, tick_dict):
        trade_dict = {}
        if self.last_tick != {}:
            last_tick = self.last_tick
            last_vol = last_tick['vol']
            vol = tick_dict['vol']
            last_inst = last_tick['inst']
            inst = tick_dict['inst']

            ask_price_delta = last_tick['ask'] - tick_dict['ask']
            ask_vol_delta = last_tick['a_v'] - tick_dict['a_v']
            bid_price_delta = last_tick['bid'] - tick_dict['bid']
            bid_vol_delta = last_tick['b_v'] - tick_dict['b_v']
            last_price_delta = last_tick['last'] - tick_dict['last']
            volume_delta = tick_dict['vol'] - last_tick['vol']
            inst_delta = tick_dict['inst'] - last_tick['inst']

            ask_price_delta_str = self.get_delta_str(last_tick['ask'], tick_dict['ask'])
            ask_vol_delta_str = self.get_delta_str(last_tick['a_v'], tick_dict['a_v'])
            bid_price_delta_str = self.get_delta_str(last_tick['bid'], tick_dict['bid'])
            bid_vol_delta_str = self.get_delta_str(last_tick['b_v'], tick_dict['b_v'])
            last_price_delta_str = self.get_delta_str(last_tick['last'], tick_dict['last'])

            if ask_price_delta != 0:
                ask_vol_delta_str = ''
            if bid_price_delta != 0:
                bid_vol_delta_str = ''

            order_forward = self.get_order_forward(
                tick_dict['last'], tick_dict['ask'],
                tick_dict['bid'], last_tick['last'],
                last_tick['ask'], last_tick['bid'])
            open_interest_delta_forward = self.get_open_interest_delta_forward(inst_delta, volume_delta)
            tick_type = self.tick_type_dict[open_interest_delta_forward][order_forward]
            trade_dict = {}
            if (open_interest_delta_forward != 'none'):
                # print('ask {}, {}, {}, {} | bid: {}, {}, {}, {}'.format(
                #     tick_dict['ask'], ask_price_delta_str, tick_dict['a_v'], ask_vol_delta_str,
                #     tick_dict['bid'], bid_price_delta_str, tick_dict['b_v'], bid_vol_delta_str))
                # msg = 'last: {}{}, trade: {}, add: {}, {}'.format(
                #     tick_dict['last'], last_price_delta_str, volume_delta,
                #     inst_delta, tick_type[0])

                if self.print_msg:
                    ts = tick_dict['ts'] / 1000
                    dt = datetime.datetime.fromtimestamp(ts)
                    msg = '{}, vol: {}, inst: {}, {} | {}:{} {}:{}'.format(
                        tick_dict['last'], volume_delta, inst_delta, tick_type[0],
                        tick_dict['ask'], tick_dict['a_v'], tick_dict['bid'],
                        tick_dict['b_v'])
                    if tick_type[1] == 'red':
                        msg = self.red(msg)
                    elif tick_type[1] == 'green':
                        msg = self.green(msg)
                    msg = '{}, {}'.format(dt, msg)
                    print(msg)
                    tick_type_type = tick_type[0]
                    if (tick_type_type in self.handicap_dict.keys()):
                        order_opposite, order_similar = self.get_order_combination(inst_delta, volume_delta)
                        print('match_order: {} {}, {} {}'.format(self.handicap_dict[tick_type_type]['opposite'], order_opposite, self.handicap_dict[tick_type_type]['similar'], order_similar))
                else:
                    trade_dict['ts'] = tick_dict['ts']
                    trade_dict['last'] = tick_dict['last']
                    trade_dict['vol'] = volume_delta
                    trade_dict['inst'] = inst_delta
                    trade_dict['type'] = tick_type[0]
                    trade_dict['color'] = tick_type[1]
                    trade_dict['ask'] = tick_dict['ask']
                    trade_dict['a_v'] = tick_dict['a_v']
                    trade_dict['bid'] = tick_dict['bid']
                    trade_dict['b_v'] = tick_dict['b_v']
        self.last_tick = tick_dict
        return trade_dict

    def tick_2_trade_list(self, tick_dict_list):
        trade_dict_list = []
        for tick_dict in tick_dict_list:
            try:
                trade_dict = self.analyze_tick(tick_dict)
                trade_dict_list.append(trade_dict)
            except Exception as e:
                pass
        return trade_dict_list

    def float_ge(self, greater, smaller):
        rst = False
        if abs(greater - smaller) < 0.00001:
            rst = True
        elif greater > smaller:
            rst = True
        return rst

    def float_le(self, smaller, greater):
        return self.float_ge(greater, smaller)

    def get_delta_str(self, pre, num):
        delta_str = ''
        if num > pre:
            delta_str = '(+' + str(num - pre) + ")"
        elif num < pre:
            delta_str = '(-' + str(pre - num) + ")"
        else:
            pass
        return delta_str

    def get_order_forward(self, last_price, ask_price1, bid_price1, pre_last_price, pre_ask_price1, pre_bid_price1):
        if self.float_ge(last_price, pre_ask_price1):
            local_order_forward = 'up'
        elif not self.float_le(last_price, pre_bid_price1):
            local_order_forward = 'down'
        else:
            if self.float_ge(last_price, ask_price1):
                local_order_forward = 'up'
            elif self.float_le(last_price, bid_price1):
                local_order_forward = 'down'
            else:
                local_order_forward = 'middle'
        return local_order_forward

    def get_open_interest_delta_forward(self, open_interest_delta, volume_delta):
        local_open_interest_delta_forward = 'none'
        if open_interest_delta == 0 and volume_delta == 0:
            local_open_interest_delta_forward = 'none'
        elif open_interest_delta == 0 and volume_delta > 0:
            local_open_interest_delta_forward = 'ex'
        elif open_interest_delta > 0:
            if open_interest_delta - volume_delta == 0:
                local_open_interest_delta_forward = 'open_double'
            else:
                local_open_interest_delta_forward = 'open'
        elif open_interest_delta < 0:
            if open_interest_delta + volume_delta == 0:
                local_open_interest_delta_forward = 'close_double'
            else:
                local_open_interest_delta_forward = 'close'
        return local_open_interest_delta_forward

    def get_order_combination(self, open_interest_delta, volume_delta):
        open_interest_delta = open_interest_delta if open_interest_delta > 0 else -open_interest_delta
        volume_delta_single_side = volume_delta / 2.0
        open_close_delta = open_interest_delta - volume_delta_single_side + 0.0
        order_similar = volume_delta_single_side / 2 + open_close_delta / 2
        order_opposite = volume_delta_single_side / 2 - open_close_delta / 2
        return int(order_opposite), int(order_similar)

    def get_tick_type_dict(self):
        self.tick_type_dict = {}
        # self.tick_type_dict['none'] = {
        #     'up': ('no_change', 'white'),
        #     'down': ('no_change', 'white'),
        #     'middle': ('no_change', 'white')
        # }
        # self.tick_type_dict['ex'] = {
        #     'up': ('ex_long', 'red'),
        #     'down': ('ex_short', 'green'),
        #     'middle': ('ex_none', 'white')
        # }
        # self.tick_type_dict['open_double'] = {
        #     'up': ('open_double', 'red'),
        #     'down': ('open_double', 'green'),
        #     'middle': ('open_double', 'white')
        # }
        # self.tick_type_dict['open'] = {
        #     'up': ('open_long', 'red'),
        #     'down': ('open_short', 'green'),
        #     'middle': ('open_none', 'white')
        # }
        # self.tick_type_dict['close_double'] = {
        #     'up': ('close_double', 'red'),
        #     'down': ('close_double', 'green'),
        #     'middle': ('close_double', 'white')
        # }
        # self.tick_type_dict['close'] = {
        #     'up': ('close_short', 'red'),
        #     'down': ('close_long', 'green'),
        #     'middle': ('close_none', 'white')
        # }
        self.tick_type_dict['none'] = {
            'up': ('不变', 'white'),
            'down': ('不变', 'white'),
            'middle': ('不变', 'white')
        }
        self.tick_type_dict['ex'] = {
            'up': ('多换', 'red'),
            'down': ('空换', 'green'),
            'middle': ('换手', 'white')
        }
        self.tick_type_dict['open_double'] = {
            'up': ('双开', 'red'),
            'down': ('双开', 'green'),
            'middle': ('双开', 'white')
        }
        self.tick_type_dict['open'] = {
            'up': ('多开', 'red'),
            'down': ('空开', 'green'),
            'middle': ('不变', 'white')
        }
        self.tick_type_dict['close_double'] = {
            'up': ('双平', 'red'),
            'down': ('双平', 'green'),
            'middle': ('双平', 'white')
        }
        self.tick_type_dict['close'] = {
            'up': ('空平', 'red'),
            'down': ('多平', 'green'),
            'middle': ('不变', 'white')
        }
        return None

    def get_handicap_dict(self):
        self.handicap_dict = {}
        self.handicap_dict['open_long'] = {
            'opposite': 'close_long',
            'similar': 'open_short'
        }
        self.handicap_dict['open_short'] = {
            'opposite': 'close_short',
            'similar': 'open_long'
        }
        self.handicap_dict['close_long'] = {
            'opposite': 'open_long',
            'similar': 'close_short'
        }
        self.handicap_dict['close_short'] = {
            'opposite': 'open_short',
            'similar': 'close_long'
        }
        return None
