# coding=utf-8

import os
import time
import datetime
import traceback

from dao_execute.utils import user_api
from dao_execute.exchange_api.okex import trade_ok
from dao_execute.exchange_api.okexf import trade_okf_v5 as trade_okf
from dao_execute.exchange_api.huobi import trade_hb
from dao_execute.exchange_api.huobif import trade_hbf
from dao_execute.exchange_api.binance import trade_ba
from dao_execute.db.dt_models import (User, ExAccount, Order)


def update_orders():
    crypto_ex_list = ['okex', 'huobi', 'binance', 'okexf', 'huobif']
    account_type_list = ExAccount.objects.distinct('ex_account_name')
    orders = Order.objects.filter(account_type__in=account_type_list,
                                  exchange__in=crypto_ex_list,
                                  order_status__in=['pending', 'partial_filled']
                                  ).order_by('-order_timestamp')
    for order in orders:
        try:
            update_one_order(order)
            time.sleep(0.05)
        except Exception as e:
            print(order.user_id, order.user_name, order.order_id, traceback.format_exc())
    return None


def update_one_order(order):
    exchange = order.exchange
    user = User.objects.get(id=order.user_id)
    api_dict = user_api.get_api_dict_fast(user, exchange, order.account_type)
    api_key = api_dict['api_key']
    secret_key = api_dict['secret_key']
    symbol = order.symbol
    order_id = order.order_id
    order_status = 'pending'
    avg_price = 0.0
    try:
        quantity = float(order.quantity)
    except Exception as e:
        quantity = 0.0
    quantity_treaded = 0.0
    order_cancel_timestamp = 0.0
    order_deal_timestamp = 0.0
    quantity_frozen = 0.0
    quantity_canceled = 0.0
    if (exchange == 'okex'):
        id = order_id
        order_dict = trade_ok.fetch_order(symbol, id, api_key, secret_key)
        order_dict = order_dict['orders'][0]
        quantity = order_dict.get('amount', 0)
        quantity_treaded = order_dict['deal_amount']
        avg_price = order_dict['avg_price']
        status = order_dict['status']
        if status == 'canceled':
            order_status = 'cancelled'
            order_cancel_timestamp = time.time()
            if (quantity_treaded > 0):
                order_status = 'filled'
                order_deal_timestamp = order_cancel_timestamp
                quantity_canceled = quantity - quantity_treaded
            else:
                quantity_canceled = quantity
        elif status == 'live':
            order_status = 'pending'
        elif status == 'partially_filled':
            order_status = 'partial_filled'
            quantity_treaded = quantity_treaded
            quantity_frozen = quantity - quantity_treaded
            avg_price = avg_price
        elif status == 'filled':
            order_status = 'filled'
            quantity_treaded = quantity_treaded
            avg_price = avg_price
            order_deal_timestamp = time.time()
        else:
            order_status = 'undefined'
    elif (exchange == 'huobi'):
        order_dict = trade_hb.fetch_order(order_id, api_key, secret_key)
        order_dict = order_dict['data']
        quantity_treaded = float(order_dict['field-amount'])
        try:
            avg_price = float(order_dict['field-cash-amount']) / quantity_treaded
        except Exception as e:
            avg_price = 0
        status = order_dict['state']
        if status == 'canceled':
            order_status = 'cancelled'
            order_cancel_timestamp = time.time()
            quantity_canceled = quantity
        elif status == 'submitted':
            order_status = 'pending'
        elif status == 'partial-filled':
            order_status = 'partial_filled'
            quantity_frozen = quantity - quantity_treaded
        elif ((status == 'filled') or
             (status == 'partial-canceled')):
            order_status = 'filled'
            order_deal_timestamp = time.time()
    elif (exchange == 'binance'):
        orderId = order_id
        recvWindow = 10000000
        order_dict = trade_ba.query_order(symbol, orderId, recvWindow,
                                          api_key, secret_key)
        quantity_treaded = float(order_dict['executedQty'])
        try:
            avg_price = float(order_dict['cummulativeQuoteQty']) / quantity_treaded
        except Exception as e:
            pass
        status = order_dict['status']
        if status == 'CANCELED':
            order_status = 'cancelled'
            order_cancel_timestamp = time.time()
            quantity_canceled = quantity
        elif status == 'NEW':
            order_status = 'pending'
        elif status == 'PARTIALLY_FILLED':
            order_status = 'partial_filled'
            quantity_frozen = quantity - quantity_treaded
            avg_price = avg_price
        elif status == 'FILLED':
            order_status = 'filled'
            order_deal_timestamp = time.time()
    elif (exchange == 'okexf'):
        order_dict = trade_okf.fetch_order(symbol, order_id, api_key, secret_key)
        order_dict = order_dict['orders'][0]
        quantity = order_dict['amount']
        quantity_treaded = order_dict['deal_amount']
        avg_price = order_dict['price_avg']
        status = order_dict['status']
        if status == 'canceled':
            order_status = 'cancelled'
            order_cancel_timestamp = time.time()
            if (quantity_treaded > 0):
                order_status = 'filled'
                order_deal_timestamp = order_cancel_timestamp
                quantity_canceled = quantity - quantity_treaded
            else:
                quantity_canceled = quantity
        elif status == 'live':
            order_status = 'pending'
        elif status == 'partially_filled':
            order_status = 'partial_filled'
            quantity_treaded = quantity_treaded
            quantity_frozen = quantity - quantity_treaded
            avg_price = avg_price
        elif status == 'filled':
            order_status = 'filled'
            quantity_treaded = quantity_treaded
            avg_price = avg_price
            order_deal_timestamp = time.time()
        else:
            order_status = 'undefined'
    elif (exchange == 'huobif'):
        symbol_ = symbol.split('_')[0].upper()
        order_dict = trade_hbf.contract_order_info(symbol_, api_key, secret_key, order_id)
        order_dict = order_dict['data'][0]
        quantity_treaded = float(order_dict['trade_volume'])
        try:
            avg_price = float(order_dict['trade_avg_price'])
        except Exception as e:
            avg_price = 0
        status = order_dict['status']
        if status == 7:
            order_status = 'cancelled'
            order_cancel_timestamp = time.time()
            quantity_canceled = quantity
        elif status in [1, 2, 3]:
            order_status = 'pending'
        elif status == 4:
            order_status = 'partial_filled'
            quantity_frozen = quantity - quantity_treaded
        elif ((status == 6) or
             (status == 5)):
            order_status = 'filled'
            order_deal_timestamp = time.time()
    order.order_status = order_status
    order.avg_price = avg_price
    order.quantity_treaded = quantity_treaded
    order.quantity_frozen = quantity_frozen
    order.quantity_canceled = quantity_canceled
    order.order_cancel_timestamp = order_cancel_timestamp
    order.order_deal_timestamp = order_deal_timestamp
    order.save()
    return order


def main():
    while True:
        try:
            update_orders()
        except Exception as e:
            dt = str(datetime.datetime.now()).split('.')[0]
            print('[*] {}, {}'.format(dt, traceback.format_exc()))
        time.sleep(0.1)
