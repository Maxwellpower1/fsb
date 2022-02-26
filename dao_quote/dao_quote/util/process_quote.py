#coding=utf-8

import json
import hmac
import redis
import pickle
import base64
import hashlib
import traceback

from dao_quote.settings import config_x
from dao_quote.util.convert import convert
from dao_quote.util.quote_save import save_mongo
from dao_quote.util.quote_fetch import (quote_fetch, quote_manage)


def check_req_sig(request):
    param_dict = request.POST.dict()
    api_key = param_dict.get('api_key', None)
    signature = param_dict.get('signature', None)
    if ((api_key is None) or (signature is None)):
        status = 0
        data = '提交未认证~'
        return status, data
    secret_key = config_x.API_KEY_DICT.get(api_key, None)
    if (secret_key is None):
        status = 0
        data = '拒绝请求, 服务未注册!'
        return status, data
    del param_dict['signature']
    content = json.dumps(param_dict)
    sig = hmac.new(secret_key.encode("utf8"), msg=content.encode("utf8"),
                   digestmod=hashlib.sha256).hexdigest()
    if (sig != signature):
        status = 0
        data = '拒绝请求, 签名错误~'
        return status, data
    status = 1
    data = 1
    return status, data


def get_kline_db(request):
    status, data = check_req_sig(request)
    if status == 0:
        return status, data
    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    period = request.POST.get('period', None)
    num = request.POST.get('num', None)
    end_timestamp = request.POST.get('end_timestamp', None)
    num = int(num)
    end_timestamp = int(end_timestamp)

    status = 1
    data = quote_fetch.get_kline_db(exchange, symbol, period, num, end_timestamp)
    data = json.dumps(data)
    return status, data


def get_backtest_kline_db(request):
    status, data = check_req_sig(request)
    if status == 0:
        return status, data

    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    period = request.POST.get('period', None)
    begin_timestamp = request.POST.get('begin_timestamp', None)
    end_timestamp = request.POST.get('end_timestamp', None)
    begin_timestamp = int(begin_timestamp)
    end_timestamp = int(end_timestamp)

    status = 1
    data = quote_fetch.get_backtest_kline_db(exchange, symbol, period, begin_timestamp, end_timestamp)
    data = json.dumps(data)
    return status, data


def get_sqlite_klines_df(request):
    status, data = check_req_sig(request)
    if status == 0:
        return status, data

    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    begin_timestamp = request.POST.get('begin_timestamp', None)
    end_timestamp = request.POST.get('end_timestamp', None)
    begin_timestamp = int(begin_timestamp)
    end_timestamp = int(end_timestamp)

    status = 1
    df = quote_fetch.get_sqlite_klines_df(exchange, symbol, begin_timestamp, end_timestamp)
    data = df.to_json(orient='split', force_ascii=False)
    return status, data


def get_hfd(request):
    status, data = check_req_sig(request)
    if status == 0:
        return status, data

    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    type_list = request.POST.get('type_list', None)
    begin_timestamp = request.POST.get('begin_timestamp', None)
    end_timestamp = request.POST.get('end_timestamp', None)

    type_list = json.loads(type_list)
    status = 1
    try:
        db = save_mongo.get_db()
        data = quote_fetch.get_hfd(db, exchange, symbol, type_list, begin_timestamp, end_timestamp)
    except Exception as e:
        status = 0
        data = ['error: {}'.format(traceback.format_exc())]
    return status, data


def get_trade_dict_list(request):
    status, data = check_req_sig(request)
    if status == 0:
        return status, data

    exchange = request.POST.get('exchange', None)
    symbol = request.POST.get('symbol', None)
    begin_timestamp = request.POST.get('begin_timestamp', None)
    end_timestamp = request.POST.get('end_timestamp', None)
    status = 1
    try:
        db = save_mongo.get_db()
        data = quote_fetch.get_trade_dict_list(db, exchange, symbol, begin_timestamp, end_timestamp)
    except Exception as e:
        status = 0
        data = ['error: {}'.format(traceback.format_exc())]
    return status, data


def download_dao_quote(request):
    status, data = check_req_sig(request)
    if status == 0:
        return status, data

    begin_time = request.POST.get('begin_time', '')
    end_time = request.POST.get('end_time', '')
    begin_timestamp = int(convert.to_timestamp(begin_time)) * 1000
    end_timestamp = int(convert.to_timestamp(end_time)) * 1000
    db_name, shasum = quote_manage.get_db(begin_timestamp, end_timestamp)
    status = 1
    data = {}
    data['url'] = db_name
    data['shasum'] = shasum
    return status, data
