# coding=utf-8

import json
import zlib
import redis
import websocket

from dao_quote.util.convert import convert
from dao_quote.settings import config_collect


def huobi_on_message(ws, message):
    message = str(zlib.decompressobj(31).decompress(message), encoding="utf-8")
    data = json.loads(message)
    if ('ping' in data):
        sub_param = {'pong': data['ping']}
        req = json.dumps(sub_param)
        ws.send(req)
    elif ('ch' in data):
        channel = data['ch']
        ts = data['ts']
        data = data['tick']
        channel_list = channel.split('.')
        symbol = channel_list[1]
        symbol = '{}_usdt'.format(symbol.split('usdt')[0])
        # need process xxx_btc
        type = channel_list[2]
        if (type == 'trade'):
            trade_list = data['data']
            for data in trade_list:
                data['size'] = data['amount']
                del data['amount']
                data['side'] = data['direction']
                del data['direction']
                data['trade_id'] = data['tradeId']
                del data['tradeId']
                send_event_dict(symbol, type, data)
        else:
            if (type == 'detail'):
                type = 'ticker'
                data['last'] = data['close']
                data['ask'] = data['close']
                data['bid'] = data['close']
                del data['id']
                del data['open']
                del data['close']
                del data['amount']
                del data['version']
                del data['count']
                data['ts'] = ts
            elif (type == 'depth'):
                del data['version']
                data['asks'].reverse()
            elif (type == 'mbp'):
                del data['seqNum']
                del data['prevSeqNum']
                type = 'depthall'
                data['ts'] = ts
            send_event_dict(symbol, type, data)


def send_event_dict(symbol, type, data):
    global exchange
    global pool

    data['ts'] = data['ts']
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


def huobi_on_error(ws, error):
    print('error: {}'.format(error))


def huobi_on_close(ws):
    print("Connection huobi closed ……")


def huobi_on_open(ws):
    global symbol_list
    global type_list
    for symbol in symbol_list:
        coin, basecoin = symbol.split('_')
        symbol = '{}{}'.format(coin, basecoin)
        for type in type_list:
            if (type == 'ticker'):
                channel = 'market.{}.{}'.format(symbol, 'detail')
            elif (type == 'depth'):
                channel = 'market.{}.{}.step1'.format(symbol, type)
            elif (type == 'depthall'):
                channel = 'market.{}.mbp.150'.format(symbol)
                sub_param = {'sub': channel, 'id': 'id2'}
                req = json.dumps(sub_param)
                ws.send(req)
            elif (type == 'trade'):
                channel = 'market.{}.{}.detail'.format(symbol, type)
            sub_param = {'sub': channel, 'id': 'id1'}
            req = json.dumps(sub_param)
            ws.send(req)


def main(symbol_list_, type_list_):
    global exchange
    global symbol_list
    global type_list
    global pool
    exchange = 'huobi'
    symbol_list = symbol_list_
    type_list = type_list_
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    url = 'wss://api.huobi.pro/ws'
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=huobi_on_message,
                                on_error=huobi_on_error,
                                on_close=huobi_on_close)
    ws.on_open = huobi_on_open
    ws.run_forever(ping_timeout=3)
