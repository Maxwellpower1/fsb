# coding=utf-8

import json
import redis
import aioredis


async def async_set_redis(key_name, value):
    conn = await aioredis.create_connection(('localhost', 6379))
    # conn = await aioredis.create_pool('redis://localhost')
    await conn.execute('set', key_name, str(value))
    conn.close()
    # await conn.wait_closed()
    return True


async def async_send_event(key_name, data):
    channel = 'quote'
    params = key_name.split('_')
    exchange = params[0]
    event_type = params[-1]
    if (len(params) == 4):
        symbol = '{}_{}'.format(params[1], params[2])
    elif (len(params) == 5):
        symbol = '{}_{}_{}'.format(params[1], params[2], params[3])
    else:
        symbol = params[1]
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    pub = await aioredis.create_redis(address='redis://localhost:6379', db=0)
    # pub = await aioredis.create_pool('redis://localhost')
    await pub.publish(channel, json.dumps(event_dict))
    pub.close()
    # await pub.wait_closed()
    return True


def set_redis(key_name, value):
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    r[key_name] = str(value)
    return True


def get_redis(key_name):
    key_name = key_name.lower()
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    value = r[key_name]
    value = value.decode('utf-8')
    return value


def get_redis_orig(key_name):
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    value = r[key_name]
    value = value.decode('utf-8')
    return value


def send_event(key_name, data):
    channel = 'quote'
    params = key_name.split('_')
    exchange = params[0]
    event_type = params[-1]
    if (len(params) == 4):
        symbol = '{}_{}'.format(params[1], params[2])
    elif (len(params) == 5):
        symbol = '{}_{}_{}'.format(params[1], params[2], params[3])
    else:
        symbol = params[1]
    event_dict = {}
    event_dict['event_type'] = event_type
    event_dict['exchange'] = exchange
    event_dict['symbol'] = symbol
    event_dict['data'] = json.dumps(data)
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    r.publish(channel, json.dumps(event_dict))
    return True
