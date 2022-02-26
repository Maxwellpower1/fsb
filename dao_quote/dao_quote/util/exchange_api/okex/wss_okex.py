# coding=utf-8

import json
import zlib
import redis
import websocket

from dao_quote.util.convert import convert
from dao_quote.settings import config_collect


def okex_inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def okex_on_message(ws, message):
    message = okex_inflate(message)
    data = message.decode('utf-8')
    data = json.loads(data)
    if ('data' not in data):
        return None
    table = data['table']
    if (table == 'spot/trade'):
        type = 'trade'
        trade_list = data['data']
        for data in trade_list:
            send_event_dict(type, data)
    else:
        data = data['data'][0]
        if (table == 'spot/ticker'):
            type = 'ticker'
            tick_dict = {}
            tick_dict['ask'] = float(data['best_ask'])
            tick_dict['a_v'] = float(data['best_ask_size'])
            tick_dict['bid'] = float(data['best_bid'])
            tick_dict['b_v'] = float(data['best_bid_size'])
            tick_dict['last'] = float(data['last'])
            tick_dict['open'] = float(data['open_24h'])
            tick_dict['high'] = float(data['high_24h'])
            tick_dict['low'] = float(data['low_24h'])
            tick_dict['vol'] = float(data['base_volume_24h'])
            tick_dict['amt'] = float(data['quote_volume_24h'])
            tick_dict['instrument_id'] = data['instrument_id']
            tick_dict['timestamp'] = data['timestamp']
            data = tick_dict
        elif (table == 'spot/depth5'):
            data['asks'].reverse()
            type = 'depth'
        elif (table == 'spot/depth'):
            data['asks'].reverse()
            type = 'depthall'
        send_event_dict(type, data)


def send_event_dict(type, data):
    global exchange
    global pool

    iso_time = data['timestamp']
    del data['timestamp']
    timestamp = convert.to_timestamp_v3(iso_time) * 1000
    instrument_id = data['instrument_id']
    del data['instrument_id']
    data['ts'] = timestamp
    coin, basecoin = instrument_id.lower().split('-')
    symbol = '{}_{}'.format(coin, basecoin)
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
        coin, basecoin = symbol.upper().split('_')
        symbol = '{}-{}'.format(coin, basecoin)
        channel_list = []
        for type in type_list:
            if (type == 'ticker'):
                channel = 'spot/{}:{}'.format(type, symbol)
            elif (type == 'depth'):
                channel = 'spot/{}5:{}'.format(type, symbol)
            elif (type == 'depthall'):
                channel = 'spot/{}:{}'.format('depth', symbol)
            elif (type == 'trade'):
                channel = 'spot/{}:{}'.format(type, symbol)
            channel_list.append(channel)
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
    url = 'wss://real.okex.com:8443/ws/v3'
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=okex_on_message,
                                on_error=okex_on_error,
                                on_close=okex_on_close)
    ws.on_open = okex_on_open
    ws.run_forever(ping_timeout=3)
