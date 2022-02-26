# coding=utf-8

import time
import json
import zlib
import redis
import traceback
import websocket

from dao_quote.settings import config_collect


def fcoin_on_message(ws, message):
    global exchange
    global timer
    try:
        timestamp = time.time()
        if (timer < timestamp):
            sub_param = {"cmd": "ping", "args": [int(timestamp)], "id": "hahaha"}
            req = json.dumps(sub_param)
            ws.send(req)
            timer = timestamp + 30
        data = json.loads(message)
        type = data['type']
        type_list = type.split('.')
        type = type_list[0]
        symbol = type_list[-1]
        symbol = '{}_usdt'.format(symbol.split('usdt')[0])
        if (type == 'trade'):
            data['size'] = data['amount']
            del data['amount']
            data['trade_id'] = data['id']
            del data['id']
            del data['type']
            data['ts'] = data['ts']
            send_event_dict(symbol, type, data)
        else:
            if (type == 'ticker'):
                data = data['ticker']
                tick_dict = {}
                tick_dict['ask'] = float(data[2])
                tick_dict['bid'] = float(data[4])
                tick_dict['last'] = float(data[0])
                tick_dict['high'] = float(data[7])
                tick_dict['low'] = float(data[8])
                tick_dict['vol'] = float(data[10])
                tick_dict['ts'] = timestamp * 1000
                data = tick_dict
            elif (type == 'depth'):
                asks_ = data['asks']
                bids_ = data['bids']
                asks = []
                bids = []
                if (type_list[1] == 'L150'):
                    type = 'depthall'
                    for i in range(0, len(asks_)):
                        if (i % 2 == 0):
                            asks.append([asks_[i], asks_[i+1]])
                    for i in range(0, len(bids_)):
                        if (i % 2 == 0):
                            bids.append([bids_[i], bids_[i+1]])
                else:
                    for i in range(0, len(asks_)):
                        if (i % 2 == 0):
                            asks.append([asks_[i], asks_[i+1]])
                            bids.append([bids_[i], bids_[i+1]])
                asks.reverse()
                data['asks'] = asks
                data['bids'] = bids
                data['ts'] = data['ts']
                del data['seq']
                del data['type']
            send_event_dict(symbol, type, data)
    except Exception as e:
        print(symbol, bids_)
        print(traceback.format_exc())


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


def fcoin_on_error(ws, error):
    print(error)


def fcoin_on_close(ws):
    print("Connection fcoin closed ……")


def fcoin_on_open(ws):
    global symbol_list
    global type_list
    for symbol in symbol_list:
        coin, basecoin = symbol.lower().split('_')
        symbol = '{}{}'.format(coin, basecoin)
        channel_list = []
        for type in type_list:
            if (type == 'ticker'):
                channel = '{}.{}'.format(type, symbol)
            elif (type == 'depth'):
                channel = '{}.L20.{}'.format(type, symbol)
            elif (type == 'depthall'):
                channel = '{}.L150.{}'.format('depth', symbol)
            elif (type == 'trade'):
                channel = '{}.{}'.format(type, symbol)
            channel_list.append(channel)
        sub_param = {"cmd": "sub", "args": channel_list, "id": "hahaha"}
        req = json.dumps(sub_param)
        ws.send(req)


def main(symbol_list_, type_list_):
    global exchange
    global symbol_list
    global type_list
    global pool
    global timer
    timer = time.time() + 30
    exchange = 'fcoin'
    symbol_list = symbol_list_
    type_list = type_list_
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    url = 'wss://api.fcoin.com/v2/ws'
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=fcoin_on_message,
                                on_error=fcoin_on_error,
                                on_close=fcoin_on_close)
    ws.on_open = fcoin_on_open
    ws.run_forever(ping_timeout=30)
