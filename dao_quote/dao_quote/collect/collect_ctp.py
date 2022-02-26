# coding=utf-8

import json
import time
import redis
import traceback

from dao_quote.settings import config
from dao_quote.util.convert import convert
from dao_quote.util.exchange_api.ctp import thostmduserapi as mdapi


class CFtdcMdSpi(mdapi.CThostFtdcMdSpi):

    def __init__(self, tapi, subID, BrokerID, UserID, Password, redis_host, redis_port, channel, lpush_record_mq, type_list):
        mdapi.CThostFtdcMdSpi.__init__(self)
        self.tapi = tapi
        self.subID = subID
        self.BrokerID = BrokerID
        self.UserID = UserID
        self.Password = Password
        self.redis_host = redis_host
        self.redis_port = redis_port
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
        self.r = redis.StrictRedis(connection_pool=pool)
        self.exchange = 'ctp'
        self.channel = channel
        self.lpush_record_mq = lpush_record_mq
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
        for symbol in self.subID:
            self.bar_dict[symbol] = {'bar': [], 'last_tick': {}}

    def get_tick_dict(self, timestamp, pDepthMarketData):
        tick_dict = {}
        tick_dict['ask'] = pDepthMarketData.AskPrice1
        tick_dict['a_v'] = pDepthMarketData.AskVolume1
        tick_dict['bid'] = pDepthMarketData.BidPrice1
        tick_dict['b_v'] = pDepthMarketData.BidVolume1
        tick_dict['last'] = pDepthMarketData.LastPrice
        tick_dict['open'] = pDepthMarketData.OpenPrice
        tick_dict['high'] = pDepthMarketData.HighestPrice
        tick_dict['low'] = pDepthMarketData.LowestPrice
        tick_dict['pre_close'] = pDepthMarketData.PreClosePrice
        tick_dict['vol'] = pDepthMarketData.Volume
        tick_dict['amt'] = pDepthMarketData.Turnover
        tick_dict['inst'] = pDepthMarketData.OpenInterest
        tick_dict['up_limit'] = pDepthMarketData.UpperLimitPrice
        tick_dict['down_limit'] = pDepthMarketData.LowerLimitPrice
        tick_dict['trading_day'] = pDepthMarketData.TradingDay
        tick_dict['action_day'] = pDepthMarketData.ActionDay

        if pDepthMarketData.AskVolume2 or pDepthMarketData.BidVolume2:
            tick_dict['ask_2'] = pDepthMarketData.AskPrice2
            tick_dict['ask_3'] = pDepthMarketData.AskPrice3
            tick_dict['ask_4'] = pDepthMarketData.AskPrice4
            tick_dict['ask_5'] = pDepthMarketData.AskPrice5

            tick_dict['bid_2'] = pDepthMarketData.BidPrice2
            tick_dict['bid_3'] = pDepthMarketData.BidPrice3
            tick_dict['bid_4'] = pDepthMarketData.BidPrice4
            tick_dict['bid_5'] = pDepthMarketData.BidPrice5

            tick_dict['a_v_2'] = pDepthMarketData.AskVolume2
            tick_dict['a_v_3'] = pDepthMarketData.AskVolume3
            tick_dict['a_v_4'] = pDepthMarketData.AskVolume4
            tick_dict['a_v_5'] = pDepthMarketData.AskVolume5

            tick_dict['b_v_2'] = pDepthMarketData.BidVolume2
            tick_dict['b_v_3'] = pDepthMarketData.BidVolume3
            tick_dict['b_v_4'] = pDepthMarketData.BidVolume4
            tick_dict['b_v_5'] = pDepthMarketData.BidVolume5
        # ts_time = pDepthMarketData.TradingDay+pDepthMarketData.UpdateTime
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

    def send_depth(self, symbol, timestamp, pDepthMarketData):
        event_type = 'depth'
        key_name = '{}_{}_{}'.format(self.exchange, symbol, event_type)
        event_dict = {}
        event_dict['key_name'] = key_name
        event_dict['event_type'] = event_type
        event_dict['exchange'] = self.exchange
        event_dict['symbol'] = symbol

        depth_dict = {}
        depth_dict['asks'] = [[pDepthMarketData.AskPrice1, pDepthMarketData.AskVolume1]]
        depth_dict['bids'] = [[pDepthMarketData.BidPrice1, pDepthMarketData.BidVolume1]]

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

    def OnFrontConnected(self) -> "void":
        print ("OnFrontConnected")
        loginfield = mdapi.CThostFtdcReqUserLoginField()
        loginfield.BrokerID = self.BrokerID
        loginfield.UserID = self.UserID
        loginfield.Password = self.Password
        loginfield.UserProductInfo = "python dll"
        self.tapi.ReqUserLogin(loginfield, 0)

    def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
        print (f"OnRspUserLogin, SessionID={pRspUserLogin.SessionID},ErrorID={pRspInfo.ErrorID},ErrorMsg={pRspInfo.ErrorMsg}")
        ret = self.tapi.SubscribeMarketData([id.encode('utf-8') for id in self.subID], len(self.subID))

    def OnRtnDepthMarketData(self, pDepthMarketData: 'CThostFtdcDepthMarketDataField') -> "void":
        try:
            symbol = pDepthMarketData.InstrumentID
            ts_time = '{} {}'.format(convert.ctp_date(), pDepthMarketData.UpdateTime)
            timestamp = convert.ctp_timestamp(ts_time)
            now_timestamp = time.time()
            if (abs(now_timestamp-timestamp) > 30):
                print('[*] {} not trade time'.format(symbol))
                return None
            timestamp = timestamp*1000 + \
                        pDepthMarketData.UpdateMillisec

            tick_dict = self.get_tick_dict(timestamp, pDepthMarketData)
            if self.gen_ticker:
                self.send_tick(symbol, tick_dict)
            if self.gen_trade:
                self.send_trade(symbol, timestamp, tick_dict)
            if self.gen_kline:
                self.send_kline(symbol, tick_dict)
            if self.gen_depth:
                self.send_depth(symbol, timestamp, pDepthMarketData)

        except Exception as e:
            print(traceback.format_exc())
        return None

    def OnRspSubMarketData(self, pSpecificInstrument: 'CThostFtdcSpecificInstrumentField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
        print("OnRspSubMarketData")
        print("InstrumentID=", pSpecificInstrument.InstrumentID)
        print("ErrorID=", pRspInfo.ErrorID)
        print("ErrorMsg=", pRspInfo.ErrorMsg)

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


def main():
    md_address = config.CTP_MD_ADDRESS
    BrokerID = config.CTP_MD_BROKER_ID
    UserID = config.CTP_MD_USER_ID
    Password = config.CTP_MD_PASSWORD
    redis_host = config.REDIS_HOST
    redis_port = config.REDIS_PORT

    COLLECT_DICT = config.COLLECT_DICT
    subID = COLLECT_DICT['ctp_md_symbols']
    channel = COLLECT_DICT['channel']
    lpush_record_mq = COLLECT_DICT['lpush_record_mq']
    type_list = COLLECT_DICT['type_list']

    mduserapi = mdapi.CThostFtdcMdApi_CreateFtdcMdApi()
    mduserspi = CFtdcMdSpi(mduserapi, subID, BrokerID, UserID, Password,
                redis_host, redis_port, channel, lpush_record_mq, type_list)
    mduserapi.RegisterFront(md_address)
    mduserapi.RegisterSpi(mduserspi)
    mduserapi.Init()
    mduserapi.Join()
