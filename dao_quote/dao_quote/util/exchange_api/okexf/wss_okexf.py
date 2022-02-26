# coding=utf-8

import json
import time
import zlib
import redis
import datetime
import websocket
import traceback

from dao_quote.util.convert import convert
from dao_quote.settings import config_collect
from dao_quote.util.exchange_api.okexf import api_okf_v3


def process_okexf_symbol(symbol):
    global symbol_dict
    global r_symbol_dict
    limit = 5
    while True:
        try:
            expire_time = symbol_dict['expire_time']
            if (time.time() > expire_time):
                symbol_dict, r_symbol_dict = api_okf_v3.convert_wss_symbol()
            symbol = symbol_dict[symbol]
            break
        except Exception as e:
            try:
                symbol_dict, r_symbol_dict = api_okf_v3.convert_wss_symbol()
                print(symbol_dict)
                symbol = symbol_dict[symbol]
                print(traceback.format_exc())
                break
            except Exception as e:
                limit -= 1
                if limit < 0:
                    raise
                    break
                else:
                    time.sleep(3)
    return symbol


def process_okexf_r_symbol(symbol):
    global symbol_dict
    global r_symbol_dict
    try:
        expire_time = symbol_dict['expire_time']
        if (time.time() > expire_time):
            symbol_dict, r_symbol_dict = api_okf_v3.convert_wss_symbol()
        symbol = r_symbol_dict[symbol]
    except Exception as e:
        symbol_dict, r_symbol_dict = api_okf_v3.convert_wss_symbol()
        symbol = r_symbol_dict[symbol]
        print(traceback.format_exc())
    return symbol


def okexf_inflate(data):
    decompress = zlib.decompressobj(-zlib.MAX_WBITS)
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated


def okexf_on_message(ws, message):
    global exchange
    global symbol_dict

    message = okexf_inflate(message)
    data = message.decode('utf-8')
    data = json.loads(data)
    if ('data' not in data):
        print(data)
        return None
    table = data['table']
    if (table == 'futures/trade'):
        type = 'trade'
        trade_list = data['data']
        for data in trade_list:
            data['price'] = float(data['price'])
            data['size'] = float(data['qty'])
            del data['qty']
            send_event_dict(type, data)
    else:
        data = data['data'][0]
        if (table == 'futures/ticker'):
            type = 'ticker'
            try:
                tick_dict = {}
                tick_dict['ask'] = float(data['best_ask'])
                tick_dict['a_v'] = float(data['best_ask_size'])
                tick_dict['bid'] = float(data['best_bid'])
                tick_dict['b_v'] = float(data['best_bid_size'])
                tick_dict['last'] = float(data['last'])
                tick_dict['open'] = float(data['open_24h'])
                tick_dict['high'] = float(data['high_24h'])
                tick_dict['low'] = float(data['low_24h'])
                tick_dict['vol'] = float(data['volume_24h'])
                tick_dict['amt'] = float(data['volume_token_24h'])
                tick_dict['inst'] = float(data['open_interest'])
                tick_dict['instrument_id'] = data['instrument_id']
                tick_dict['timestamp'] = data['timestamp']
                data = tick_dict
            except Exception as e:
                print(data)
                print(traceback.format_exc())
                return None
        elif (table == 'futures/depth5'):
            data['asks'].reverse()
            type = 'depth'
        elif (table == 'futures/depth_l2_tbt'):
            data['asks'].reverse()
            type = 'depthall'
        elif (table == 'futures/candle60s'):
            type = 'kline'
        send_event_dict(type, data)


def send_event_dict(type, data):
    global exchange
    global bar_dict
    global time_format

    instrument_id = data['instrument_id']
    del data['instrument_id']
    symbol = process_okexf_r_symbol(instrument_id)
    if type != 'kline':
        iso_time = data['timestamp']
        del data['timestamp']
        dt = datetime.datetime.strptime(iso_time, time_format)
        timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
        data['ts'] = timestamp
    else:
        candle = data['candle']
        iso_time = candle[0]
        close = float(candle[4])
        dt = datetime.datetime.strptime(iso_time, time_format)
        timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000
        bar = [timestamp, float(candle[1]), float(candle[2]),
               float(candle[3]), close,
               float(candle[5]), float(candle[6])]
        last_bar = bar_dict[symbol].get('bar', [])
        if last_bar == []:
            last_bar = [timestamp-60000, close, close, close, close, 0, 0]
        last_bar_ts = last_bar[0]
        bar_dict[symbol]['bar'] = bar
        if timestamp > last_bar_ts:
            data = [last_bar, bar]
            print(datetime.datetime.now(), symbol, data[0])
        else:
            return None

    key_name = '{}_{}_{}'.format(exchange, symbol, type)

    event_type = type
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['key_name'] = key_name
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    event_dict = json.dumps(event_dict)
    send_event(key_name, data, event_dict)


def send_event(key_name, data, event_dict):
    global pool

    r = redis.StrictRedis(connection_pool=pool)
    r.publish(key_name, event_dict)
    r.publish(config_collect.CHANNEL, event_dict)
    r[key_name] = str(data)
    r.lpush(config_collect.LPUSH_RECORD_MQ, event_dict)


def okexf_on_error(ws, error):
    print('error: {}'.format(error))


def okexf_on_close(ws):
    print("Connection okexf closed ……")


def okexf_on_open(ws):
    global symbol_list
    global type_list
    for symbol in symbol_list:
        symbol = process_okexf_symbol(symbol)
        channel_list = []
        for type in type_list:
            if (type == 'ticker'):
                # BTC-USD-170310
                channel = 'futures/{}:{}'.format(type, symbol)
            elif (type == 'depth'):
                channel = 'futures/{}5:{}'.format(type, symbol)
            elif (type == 'depthall'):
                channel = 'futures/{}:{}'.format('depth_l2_tbt', symbol)
            elif (type == 'trade'):
                channel = 'futures/{}:{}'.format(type, symbol)
            elif (type == 'kline'):
                channel = 'futures/candle60s:{}'.format(symbol)
            channel_list.append(channel)
        sub_param = {"op": "subscribe", "args": channel_list}
        req = json.dumps(sub_param)
        ws.send(req)


def main(symbol_list_, type_list_):
    global exchange
    global symbol_list
    global type_list
    global pool
    global bar_dict
    global time_format
    exchange = 'okexf'
    symbol_list = symbol_list_
    type_list = type_list_

    bar_dict = {}
    for symbol in symbol_list:
        bar_dict[symbol] = {'bar': [], 'last_trade': {}}

    time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    pool = redis.ConnectionPool(host=config_collect.REDIS_HOST, port=config_collect.REDIS_PORT, db=0)
    url = 'wss://real.okex.com:8443/ws/v3'
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=okexf_on_message,
                                on_error=okexf_on_error,
                                on_close=okexf_on_close)
    ws.on_open = okexf_on_open
    ws.run_forever(ping_timeout=3)
