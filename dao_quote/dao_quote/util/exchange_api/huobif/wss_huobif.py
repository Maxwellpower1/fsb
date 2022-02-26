# coding=utf-8

import json
import zlib
import redis
import websocket

from dao_quote.util.convert import convert
from dao_quote.settings import config_collect


def huobif_on_message(ws, message):
    global exchange
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
        coin, contract_type = channel_list[1].split('_')
        if (contract_type == 'CW'):
            contract_type = 'this_week'
        elif (contract_type == 'NW'):
            contract_type = 'next_week'
        elif (contract_type == 'CQ'):
            contract_type = 'quarter'
        symbol = '{}_usd-{}'.format(coin.lower(), contract_type)
        type = channel_list[2]
        if (type == 'trade'):
            trade_list = data['data']
            for data in trade_list:
                data['size'] = data['amount']
                del data['amount']
                data['side'] = data['direction']
                del data['direction']
                data['trade_id'] = data['id']
                del data['id']
                send_event_dict(symbol, type, data)
        else:
            if (type == 'detail'):
                type = 'ticker'
                data['last'] = data['close']
                data['ask'] = data['close']
                data['bid'] = data['close']
                del data['id']
                del data['mrid']
                del data['open']
                del data['close']
                del data['amount']
                del data['count']
                data['ts'] = ts
            elif (type == 'depth'):
                if (channel_list[-1] == 'step0'):
                    type = 'depthall'
                else:
                    pass
                del data['ch']
                del data['version']
                del data['mrid']
                del data['id']
                data['asks'].reverse()
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


def huobif_on_error(ws, error):
    print('error: {}'.format(error))


def huobif_on_close(ws):
    print("Connection huobif closed ……")


def huobif_on_open(ws):
    global symbol_list
    global type_list
    for symbol in symbol_list:
        contract_type = symbol.split('-')[1]
        symbol = symbol.split('_')[0].upper()
        if (contract_type == 'this_week'):
            contract_type = 'CW'
        elif (contract_type == 'next_week'):
            contract_type = 'NW'
        elif (contract_type == 'quarter'):
            contract_type = 'CQ'
        symbol = '{}_{}'.format(symbol, contract_type)
        for type in type_list:
            if (type == 'ticker'):
                channel = 'market.{}.{}'.format(symbol, 'detail')
            elif (type == 'depth'):
                channel = 'market.{}.{}.step1'.format(symbol, type)
            elif (type == 'depthall'):
                channel = 'market.{}.{}.step0'.format(symbol, 'depth')
            elif (type == 'trade'):
                channel = 'market.{}.{}.detail'.format(symbol, type)
            sub_param = {'sub': channel}
            req = json.dumps(sub_param)
            ws.send(req)


def main(symbol_list_, type_list_):
    global exchange
    global symbol_list
    global type_list
    global pool
    exchange = 'huobif'
    symbol_list = symbol_list_
    type_list = type_list_
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    url = 'wss://www.hbdm.com/ws'
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=huobif_on_message,
                                on_error=huobif_on_error,
                                on_close=huobif_on_close)
    ws.on_open = huobif_on_open
    ws.run_forever(ping_timeout=3)
