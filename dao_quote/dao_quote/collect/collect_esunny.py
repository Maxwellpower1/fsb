import re
import sys
import json
import time
import redis
import traceback
from ctypes import c_double, c_ulonglong

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.exchange_api.esunny import EsunnyApi as esapi


class EsQuote(esapi.ITapQuoteAPINotify):

    def get_tick_dict(self, timestamp, tapAPIQuoteWhole):
        QAskPrice = list((c_double * 20).from_address(int(tapAPIQuoteWhole.QAskPrice)))
        QAskQty = list((c_ulonglong * 20).from_address(int(tapAPIQuoteWhole.QAskQty)))
        QBidPrice = list((c_double * 20).from_address(int(tapAPIQuoteWhole.QBidPrice)))
        QBidQty = list((c_ulonglong * 20).from_address(int(tapAPIQuoteWhole.QBidQty)))

        tick_dict = {}
        tick_dict['ask'] = QAskPrice[0]
        tick_dict['a_v'] = QAskQty[0]
        tick_dict['bid'] = QBidPrice[0]
        tick_dict['b_v'] = QBidQty[0]

        tick_dict['last'] = tapAPIQuoteWhole.QLastPrice
        tick_dict['open'] = tapAPIQuoteWhole.QOpeningPrice
        tick_dict['high'] = tapAPIQuoteWhole.QHighPrice
        tick_dict['low'] = tapAPIQuoteWhole.QLowPrice
        tick_dict['pre_close'] = tapAPIQuoteWhole.QPreClosingPrice
        tick_dict['vol'] = tapAPIQuoteWhole.QTotalQty
        tick_dict['amt'] = tapAPIQuoteWhole.QTotalTurnover
        tick_dict['inst'] = tapAPIQuoteWhole.QPositionQty
        tick_dict['up_limit'] = tapAPIQuoteWhole.QLimitUpPrice
        tick_dict['down_limit'] = tapAPIQuoteWhole.QLimitDownPrice

        tick_dict['ask_2'] = QAskPrice[1]
        tick_dict['ask_3'] = QAskPrice[2]
        tick_dict['ask_4'] = QAskPrice[3]
        tick_dict['ask_5'] = QAskPrice[4]

        tick_dict['bid_2'] = QBidPrice[1]
        tick_dict['bid_3'] = QBidPrice[2]
        tick_dict['bid_4'] = QBidPrice[3]
        tick_dict['bid_5'] = QBidPrice[4]

        tick_dict['a_v_2'] = QAskQty[1]
        tick_dict['a_v_3'] = QAskQty[2]
        tick_dict['a_v_4'] = QAskQty[3]
        tick_dict['a_v_5'] = QAskQty[4]

        tick_dict['b_v_2'] = QBidQty[1]
        tick_dict['b_v_3'] = QBidQty[2]
        tick_dict['b_v_4'] = QBidQty[3]
        tick_dict['b_v_5'] = QBidQty[4]

        tick_dict['ts'] = timestamp
        return tick_dict

    def update_tick(self, symbol, tick_data):
        bar_ret = []
        new_minute = False
        bar = self.bar_dict[symbol].get('bar', [])
        last_tick = self.bar_dict[symbol].get('last_tick', {})

        if not tick_data['last']:
            return bar_ret

        if not bar:
            new_minute = True
        elif int(bar[0]/60000) != int(tick_data['ts']/60000):
            bar_ret = bar
            new_minute = True

        if new_minute:
            bar = [int(tick_data['ts']/60000) * 60000,
                   tick_data['last'],
                   tick_data['last'],
                   tick_data['last'],
                   tick_data['last'],
                   0.0]
        else:
            # bar[0] = int(tick_data['ts']/60000) * 60000
            bar[2] = max(bar[2], tick_data['last'])
            bar[3] = min(bar[3], tick_data['last'])
            bar[4] = tick_data['last']

        if last_tick:
            volume_change = tick_data['vol'] - last_tick['vol']
            bar[5] += max(volume_change, 0)

        last_tick = tick_data
        self.bar_dict[symbol]['bar'] = bar
        self.bar_dict[symbol]['last_tick'] = last_tick
        return bar_ret

    def send_event(self, key_name, data, event_dict):
        event_dict = json.dumps(event_dict)
        self.r[key_name] = str(data)
        self.r.publish(self.channel, event_dict)
        self.r.publish(key_name, event_dict)
        self.r.lpush(self.lpush_record_mq, event_dict)

    def send_tick(self, symbol, tick_dict):
        event_type = 'ticker'
        key_name = '{}_{}_{}'.format(self.exchange, symbol, event_type)
        event_dict = {}
        event_dict['key_name'] = key_name
        event_dict['event_type'] = event_type
        event_dict['exchange'] = self.exchange
        event_dict['symbol'] = symbol
        event_dict['data'] = json.dumps(tick_dict)
        self.send_event(key_name, tick_dict, event_dict)

    def send_kline(self, symbol, tick_dict):
        kline = self.update_tick(symbol, tick_dict)
        if kline:
            kline_list = [kline, [kline[0]+60000, kline[4], kline[4], kline[4], kline[4], 0]]
            event_type = 'kline'
            key_name = '{}_{}_{}'.format(self.exchange, symbol, event_type)
            event_dict = {}
            event_dict['key_name'] = key_name
            event_dict['event_type'] = event_type
            event_dict['exchange'] = self.exchange
            event_dict['symbol'] = symbol
            event_dict['data'] = json.dumps(kline_list)
            self.send_event(key_name, kline_list, event_dict)

    def send_depth(self, symbol, timestamp, tapAPIQuoteWhole):
        event_type = 'depth'
        key_name = '{}_{}_{}'.format(self.exchange, symbol, event_type)
        event_dict = {}
        event_dict['key_name'] = key_name
        event_dict['event_type'] = event_type
        event_dict['exchange'] = self.exchange
        event_dict['symbol'] = symbol

        QAskPrice = list((c_double * 20).from_address(int(tapAPIQuoteWhole.QAskPrice)))
        QAskQty = list((c_ulonglong * 20).from_address(int(tapAPIQuoteWhole.QAskQty)))
        QBidPrice = list((c_double * 20).from_address(int(tapAPIQuoteWhole.QBidPrice)))
        QBidQty = list((c_ulonglong * 20).from_address(int(tapAPIQuoteWhole.QBidQty)))

        depth_dict = {}
        asks = []
        bids = []
        for i in range(0, 5):
            asks.append([QAskPrice[i], QAskQty[i]])
            bids.append([QBidPrice[i], QBidQty[i]])
        asks.reverse()
        depth_dict['asks'] = asks
        depth_dict['bids'] = bids

        depth_dict['ts'] = timestamp
        event_dict['data'] = json.dumps(depth_dict)
        self.send_event(key_name, depth_dict, event_dict)

    def send_trade(self, symbol, timestamp, tick_dict):
        last_tick = self.bar_dict[symbol].get('last_tick', {})
        if last_tick:
            event_type = 'trade'
            key_name = '{}_{}_{}'.format(self.exchange, symbol, event_type)
            event_dict = {}
            event_dict['key_name'] = key_name
            event_dict['event_type'] = event_type
            event_dict['exchange'] = self.exchange
            event_dict['symbol'] = symbol

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
            # userful later
            # if (open_interest_delta_forward != 'none'):
            #     print('ask {}, {}, {}, {} | bid: {}, {}, {}, {}'.format(
            #         tick_dict['ask'], ask_price_delta_str, tick_dict['a_v'], ask_vol_delta_str,
            #         tick_dict['bid'], bid_price_delta_str, tick_dict['b_v'], bid_vol_delta_str))
            #
            #     print('ts: {}, last: {}{}, trade: {}, add: {}, {},{}'.format(
            #         timestamp, tick_dict['last'], last_price_delta_str, volume_delta,
            #         inst_delta, tick_type[0], tick_type[1]))
            #
            #     tick_type_type = tick_type[0]
            #     if (tick_type_type in self.handicap_dict.keys()):
            #         order_opposite, order_similar = self.get_order_combination(inst_delta, volume_delta)
            #         print('match_order: {} {}, {} {}'.format(self.handicap_dict[tick_type_type]['opposite'], order_opposite, self.handicap_dict[tick_type_type]['similar'], order_similar))
            if (volume_delta == 0):
                return None
            if (tick_type[1] == 'red'):
                side = 'buy'
            elif (tick_type[1] == 'green'):
                side = 'sell'
            else:
                side = 'none'
            trade_dict = {}
            trade_dict['trade_id'] = int(timestamp)
            trade_dict['price'] = tick_dict['last']
            trade_dict['size'] = volume_delta
            trade_dict['side'] = side
            trade_dict['ts'] = timestamp
            event_dict['data'] = json.dumps(trade_dict)
            self.send_event(key_name, trade_dict, event_dict)

    def OnRspLogin(self, errorCode, info):
        self.log('OnRspLogin errorCode: {}, info: '.format(errorCode, info))

    def OnAPIReady(self):
        self.log('API准备就绪')
        for symbol in self.symbol_list:
            try:
                split_symbol = re.findall(r'[0-9]+|[a-zA-Z]+', symbol)
                tac = esapi.TapAPIContract()
                tac.Commodity.CommodityNo = split_symbol[0]
                tac.ContractNo1 = split_symbol[1]

                tac.Commodity.ExchangeNo = 'ZCE'
                tac.Commodity.CommodityType = 'F'
                tac.CallOrPutFlag1 = 'N'
                tac.CallOrPutFlag2 = 'N'
                self.ctqa_z.SubscribeQuote(0, tac)
            except Exception as e:
                print(traceback.fromat_exc())

    def OnDisconnect(self, reasonCode):
        self.log('OnDisconnect reasonCode: {}'.format(reasonCode))
        sys.exit(0)

    def OnRspSubscribeQuote(self, sessionID, errorCode, isLast, info):
        self.log('OnRspSubscribeQuote: {} {}'.format(info.Contract.Commodity.CommodityNo, info.Contract.ContractNo1))

    def OnRtnQuote(self, tapAPIQuoteWhole):
        try:
            symbol = '{}{}'.format(tapAPIQuoteWhole.Contract.Commodity.CommodityNo, tapAPIQuoteWhole.Contract.ContractNo1)
            timestamp = convert.to_timestamp_es(tapAPIQuoteWhole.DateTimeStamp)

            tick_dict = self.get_tick_dict(timestamp, tapAPIQuoteWhole)
            if self.gen_ticker:
                self.send_tick(symbol, tick_dict)
            if self.gen_trade:
                self.send_trade(symbol, timestamp, tick_dict)
            if self.gen_kline:
                self.send_kline(symbol, tick_dict)
            if self.gen_depth:
                self.send_depth(symbol, timestamp, tapAPIQuoteWhole)
        except Exception as e:
            print(traceback.format_exc())
        return None

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
        self.tick_type_dict['none'] = {
            'up': ('no_change', 'white'),
            'down': ('no_change', 'white'),
            'middle': ('no_change', 'white')
        }
        self.tick_type_dict['ex'] = {
            'up': ('ex_long', 'red'),
            'down': ('ex_short', 'green'),
            'middle': ('ex_none', 'white')
        }
        self.tick_type_dict['open_double'] = {
            'up': ('open_double', 'red'),
            'down': ('open_double', 'green'),
            'middle': ('open_double', 'white')
        }
        self.tick_type_dict['open'] = {
            'up': ('open_long', 'red'),
            'down': ('open_short', 'green'),
            'middle': ('open_none', 'white')
        }
        self.tick_type_dict['close_double'] = {
            'up': ('close_double', 'red'),
            'down': ('close_double', 'green'),
            'middle': ('close_double', 'white')
        }
        self.tick_type_dict['close'] = {
            'up': ('close_short', 'red'),
            'down': ('close_long', 'green'),
            'middle': ('close_none', 'white')
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

    def log(self, msg):
        print('[*] {}'.format(msg))

    def main(self):
        redis_host = config.REDIS_HOST
        redis_port = config.REDIS_PORT
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
        self.r = redis.StrictRedis(connection_pool=pool)

        self.exchange = 'ctp'
        COLLECT_DICT = config.COLLECT_DICT
        self.symbol_list = COLLECT_DICT['esunny_md_symbols']
        self.channel = COLLECT_DICT['channel']
        self.lpush_record_mq = COLLECT_DICT['lpush_record_mq']
        type_list = COLLECT_DICT['type_list']

        if 'kline' in type_list:
            self.gen_kline = True
        else:
            self.gen_kline = False
        if 'ticker' in type_list:
            self.gen_ticker = True
        else:
            self.gen_ticker = False
        if 'depth' in type_list:
            self.gen_depth = True
        else:
            self.gen_depth = False
        if 'trade' in type_list:
            self.gen_trade = True
        else:
            self.gen_trade = False
        self.get_tick_type_dict()
        self.get_handicap_dict()
        self.bar_dict = {}
        for symbol in self.symbol_list:
            self.bar_dict[symbol] = {'bar': [], 'last_tick': {}}

        taai = esapi.TapAPIApplicationInfo()
        taai.AuthCode = ''
        taai.KeyOperationLogPath = ''

        i = 0
        ctqa = esapi.CreateTapQuoteAPI(taai, i)

        taqla = esapi.TapAPIQuoteLoginAuth()
        taqla.ISModifyPassword = 'N'
        taqla.ISDDA = 'N'

        ctqa[0].SetHostAddress('61.163.243.173', 6161)
        ctqa[0].SetAPINotify(self)
        ctqa[0].Login(taqla)
        self.ctqa_z = ctqa[0]

        while True:
            time.sleep(3)


def main():
    eq = EsQuote()
    eq.main()
