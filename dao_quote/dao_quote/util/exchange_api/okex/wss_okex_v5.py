# coding=utf-8

import json
import redis
import websocket

from dao_quote.util.convert import convert
from dao_quote.settings import config_collect


def okex_on_message(ws, message):
    data = json.loads(message)
    table = data['arg']['channel']
    symbol = data['arg']['instId'].lower().replace('-', '_')
    if (table == 'trades'):
        type = 'trade'
        trade_list = data['data']
        for data in trade_list:
            trade_dict = {}
            trade_dict['ts'] = int(data['ts'])
            trade_dict['trade_id'] = data['tradeId']
            trade_dict['price'] = data['px']
            trade_dict['size'] = data['sz']
            trade_dict['side'] = data['side']
            send_event_dict(symbol, type, trade_dict)
    elif (table == 'tickers'):
        data = data['data'][0]
        type = 'ticker'
        tick_dict = {}
        tick_dict['ts'] = int(data['ts'])
        tick_dict['ask'] = float(data['askPx'])
        tick_dict['a_v'] = float(data['askSz'])
        tick_dict['bid'] = float(data['bidPx'])
        tick_dict['b_v'] = float(data['bidSz'])
        tick_dict['last'] = float(data['last'])
        tick_dict['open'] = float(data['open24h'])
        tick_dict['high'] = float(data['high24h'])
        tick_dict['low'] = float(data['low24h'])
        tick_dict['vol'] = float(data['vol24h'])
        tick_dict['amt'] = float(data['volCcy24h'])
        send_event_dict(symbol, type, tick_dict)
    elif (table == 'books5'):
        type = 'depth'
        data = data['data'][0]
        data['asks'].reverse()
        data['ts'] = int(data['ts'])
        send_event_dict(symbol, type, data)
    elif (table == 'books-l2-tbt'):
        type = 'depthall'
        instId = data['arg']['instId']
        data = data['data'][0]
        data['asks'].reverse()
        data['ts'] = int(data['ts'])
        send_event_dict(symbol, type, data)
    elif (table == 'candle1m'):
        type = 'kline'
        data = data['data']
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


def okex_on_error(ws, error):
    print('error: {}'.format(error))


def okex_on_close(ws):
    print("Connection okex closed ……")


def okex_on_open(ws):
    global symbol_list
    global type_list
    for symbol in symbol_list:
        symbol = symbol.upper().replace('_', '-')
        channel_list = []
        for type in type_list:
            channel_dict = {}
            if (type == 'ticker'):
                channel_dict['channel'] = 'tickers'
                channel_dict['instId'] = symbol
            elif (type == 'depth'):
                channel_dict['channel'] = 'books5'
                channel_dict['instId'] = symbol
            elif (type == 'depthall'):
                channel_dict['channel'] = 'books-l2-tbt'
                channel_dict['instId'] = symbol
            elif (type == 'trade'):
                channel_dict['channel'] = 'trades'
                channel_dict['instId'] = symbol
            elif (type == 'kline'):
                channel_dict['channel'] = 'candle1m'
                channel_dict['instId'] = symbol
            channel_list.append(channel_dict)
        sub_param = {"op": "subscribe", "args": channel_list}
        req = json.dumps(sub_param)
        ws.send(req)


def main(symbol_list_, type_list_):
    global exchange
    global symbol_list
    global type_list
    global pool
    exchange = 'okex'
    symbol_list = symbol_list_
    type_list = type_list_
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    url = 'wss://ws.okex.com:8443/ws/v5/public'
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=okex_on_message,
                                on_error=okex_on_error,
                                on_close=okex_on_close)
    ws.on_open = okex_on_open
    ws.run_forever(ping_timeout=3)
