# coding=utf-8

import json

from django.shortcuts import render
from django.views.decorators.csrf import (csrf_exempt, csrf_protect)
from django.http import (HttpResponse, StreamingHttpResponse)

from dao_quote.util import process_quote


# Create your views here.
@csrf_exempt
def web_api_v1(request):
    method = request.POST.get('method', None)

    status = 1
    data = []

    if (method == 'get_kline_db'):
        status, data = process_quote.get_kline_db(request)
    elif (method == 'get_backtest_kline_db'):
        status, data = process_quote.get_backtest_kline_db(request)
    elif (method == 'get_sqlite_klines_df'):
        status, data = process_quote.get_sqlite_klines_df(request)
    elif (method == 'get_hfd'):
        status, data = process_quote.get_hfd(request)
    elif (method == 'get_trade_dict_list'):
        status, data = process_quote.get_trade_dict_list(request)
    elif (method == 'download_dao_quote'):
        status, data = process_quote.download_dao_quote(request)
    else:
        status, data = (None, None)

    info = {}
    info['status'] = status
    info['data'] = data

    response = HttpResponse()
    response['Access-Control-Allow-Origin'] = '*'
    rjson = json.dumps(info)
    response.write(rjson)
    return response
