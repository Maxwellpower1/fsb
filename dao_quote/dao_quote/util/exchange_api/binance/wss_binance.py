# coding=utf-8

import json
import time
import redis
import websocket

from dao_quote.util.convert import convert
from dao_quote.settings import config_collect
from dao_quote.util.exchange_api.binance import api_ba


def binance_on_message(ws, message):
    data = json.loads(message)
    if ('ping' in data):
        sub_param = {'pong': data['ping']}
        req = json.dumps(sub_param)
        ws.send(req)
    else:
        channel = data['stream']
        data = data['data']
        exchange = 'binance'
        channel_list = channel.split('@')
        symbol = channel_list[0]
        symbol = '{}_usdt'.format(symbol.split('USDT')[0].lower())
        type = channel_list[1]
        if (type == 'depth10'):
            type = 'depth'
            del data['lastUpdateId']
            data['asks'].reverse()
            data['ts'] = time.time()*1000
        elif (type == 'depth'):
            type = 'depthall'
            depth_dict = {}
            depth_dict['ts'] = data['E']
            depth_dict['asks'] = data['a']
            depth_dict['bids'] = data['b']
            data = depth_dict
        elif (type == 'ticker'):
            tick_dict = {}
            tick_dict['last'] = float(data['c'])
            tick_dict['high'] = float(data['h'])
            tick_dict['low'] = float(data['l'])
            tick_dict['vol'] = float(data['v'])
            tick_dict['ask'] = float(data['a'])
            tick_dict['bid'] = float(data['b'])
            tick_dict['ts'] = data['E']
            data = tick_dict
        elif (type == 'trade'):
            trade_dict = {}
            trade_dict['trade_id'] = data['t']
            trade_dict['price'] = data['p']
            trade_dict['size'] = data['q']
            if (data['m']):
                trade_dict['side'] = 'sell'
            else:
                trade_dict['side'] = 'buy'
            trade_dict['ts'] = data['E']
            data = trade_dict
        send_event_dict(symbol, type, data)

def send_event_dict(symbol, type, data):
    global exchange
    global pool

    key_name = '{}_{}_{}'.format(exchange, symbol, type)
    r = redis.StrictRedis(connection_pool=pool)
    event_type = type
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['key_name'] = key_name
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    event_dict = json.dumps(event_dict)
    r.publish(key_name, event_dict)
    r.publish(config_collect.CHANNEL, event_dict)
    r[key_name] = str(data)
    r.lpush(config_collect.LPUSH_RECORD_MQ, event_dict)


def binance_on_error(ws, error):
    print('error {}'.format(error))


def binance_on_close(ws):
    print("Connection binance closed ……")


def binance_on_open(ws):
    pass


def main(symbol_list_, type_list_):
    global exchange
    global symbol_list
    global type_list
    global pool
    exchange = 'binance'
    symbol_list = symbol_list_
    type_list = type_list_
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    url = 'wss://stream.binance.com:9443/stream?streams='

    for symbol in symbol_list:
        coin, basecoin = symbol.split('_')
        symbol = '{}{}'.format(coin, basecoin).upper()
        for type in type_list:
            channel = '{}@{}'.format(symbol.lower(), type)
            if (type == 'depth'):
                channel += '10'
            elif (type == 'depthall'):
                channel = channel[:-3]

                data = api_ba.depth(symbol, 1000)
                data['ts'] = time.time()
                symbol_ = '{}_usdt'.format(symbol.split('USDT')[0].lower())
                send_event_dict(symbol_, type, data)
                time.sleep(0.1)
            url += '{}/'.format(channel)
    url = url[:-1]
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=binance_on_message,
                                on_error=binance_on_error,
                                on_close=binance_on_close)
    ws.on_open = binance_on_open
    ws.run_forever(ping_timeout=3)
