import ast
import sys
import json
import time
import uuid
import hmac
import hashlib
import datetime
import thriftpy2
import traceback
from bson.objectid import ObjectId
from thriftpy2.rpc import make_server

from dao_execute.utils import user_api
from dao_execute.settings.config import cfg
from dao_execute.db.dt_models import (User, Order, ComplexOrder)
from dao_execute.exchange_api.okex import trade_ok
from dao_execute.exchange_api.okexf import trade_okf_v5 as trade_okf
from dao_execute.exchange_api.huobi import trade_hb
from dao_execute.exchange_api.huobif import trade_hbf
from dao_execute.exchange_api.binance import trade_ba
from dao_execute.exchange_api.ctp.trade_ctpc import TradeCtp


class Dispatcher(object):

    def __init__(self):
        self.api_key_dict = cfg['rpc_token']
        if self.api_key_dict == {}:
            print('[*] api_key_dict is null !')
            sys.exit(0)

    def check_sig(self, *args):
        req_sig = args[0]
        if req_sig == '':
            return False
        api_key, req_sig = req_sig.split('.')
        secret_key = self.api_key_dict[api_key]
        content = ','.join(args[1:])

        sig = hmac.new(secret_key.encode("utf8"),
                       msg=content.encode("utf8"),
                       digestmod=hashlib.sha256).hexdigest()
        if req_sig == sig:
            return True
        else:
            return False

    def ret_resp(self, status, data):
        resp = {}
        resp['status'] = status
        resp['data'] = data
        return json.dumps(resp)

    def execute_order(self, sig, user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num, exec_ts, strategy_instance_id, close_today):
        if not self.check_sig(sig, 'execute_order', user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num, exec_ts, strategy_instance_id, str(close_today)):
            data = 'wrong sig'
            return self.ret_resp(0, data)
        status = 1
        data = {}
        user = User.objects.get(id=user_id)
        try:
            if exchange != 'ctp':
                amount = float(amount)
            else:
                if '.' in amount:
                    amount = int(float(amount))
                else:
                    amount = int(amount)
        except Exception as e:
            data = '输入数量不是数字!'
            return self.ret_resp(0, data)
        complex_order_type_list = ['ifo', 'ifd', 'oco']
        if (order_type in complex_order_type_list):
            data = '暂不支持'
            return self.ret_resp(0, data)
        elif ('spread' in order_type):
            data = '暂不支持'
            return self.ret_resp(0, data)
        try:
            price = float(price)
        except Exception as e:
            data = '输入价格不是数字!'
            return self.ret_resp(0, data)
        try:
            money_num = float(money_num)
        except Exception as e:
            data = '输入金额不是数字!'
            return self.ret_resp(0, data)
        try:
            exec_ts = float(exec_ts)
        except Exception as e:
            data = '输入 exec_ts 不是数字!'
            return self.ret_resp(0, data)
        if (account_type == 'reg_emulator'):
            data = '暂不支持'
            return self.ret_resp(0, data)
        elif (account_type == 'reg_trade'):
            data = '暂不支持'
            return self.ret_resp(0, data)
        elif (account_type == 'reg_backtest'):
            status, data = self.execute_backtest_order(user_id, exchange,
                           account_type, symbol, order_type, strategy_name,
                           price, amount, exec_ts, strategy_instance_id, user)
            return self.ret_resp(status, data)
        try:
            # account_type 进入实盘api交易
            if (exchange == 'okex'):
                if (order_type == 'buy_limit'):
                    order_type_ = 'buy'
                elif (order_type == 'buy_market'):
                    symbol_price = trade_ok.ticker(symbol)['ticker']['last']
                    price = float(symbol_price) * amount
                    amount = ''
                    order_type_ = 'buy_market'
                elif (order_type == 'sell_limit'):
                    order_type_ = 'sell'
                elif (order_type == 'sell_market'):
                    price = ''
                    order_type_ = 'sell_market'
                else:
                    data = '输入订单类型不正确'
                    return self.ret_resp(0, data)
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                order_id = trade_ok.trade(symbol, order_type_,
                           api_dict['api_key'], api_dict['secret_key'],
                           price, amount)
                if (int(order_id) != 0):
                    price_ = price
                    if (order_type == 'buy_market'):
                        price_ = '市价'
                    elif (order_type == 'sell_market'):
                        price_ = '市价'
                    data['order_id'] = order_id
                    data['data'] = ('下单成功, 交易所: {}, 标的: {}, '
                                    '价格: {}, 数量: {}').format(
                                    exchange, symbol, price_, amount)
                else:
                    data = '下单失败！'
                    return self.ret_resp(0, data)
            elif (exchange == 'huobi'):
                amount_ = amount
                if (symbol == 'btc_usdt'):
                    price = round(price, 2)
                    amount_ = round(amount_, 6)
                if (order_type == 'buy_limit'):
                    order_type_ = 'buy-limit'
                elif (order_type == 'buy_market'):
                    price = ''
                    amount_ = amount * float(trade_hb.market_detail_merged(symbol)['tick']['ask'][0])
                    amount_ = round(amount_, 8)
                    if (symbol in ['eth_btc', 'eth_btc', 'eth_btc', 'eth_btc']):
                        amount_ = round(amount_, 4)
                    order_type_ = 'buy-market'
                elif (order_type == 'sell_limit'):
                    order_type_ = 'sell-limit'
                elif (order_type == 'sell_market'):
                    price = ''
                    order_type_ = 'sell-market'
                else:
                    data = '输入订单类型不正确'
                    return self.ret_resp(0, data)
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                type_id = 'spot'
                account_id = trade_hb.account_id_by_type(type_id,
                             api_dict['api_key'], api_dict['secret_key'])
                source = 'api'
                type_ = order_type_
                amount_ = str(amount_)
                order_id = trade_hb.orders_place(symbol, type_, price, amount_,
                           account_id, source, api_dict['api_key'],
                           api_dict['secret_key'])
                if (int(order_id) != 0):
                    price_ = price
                    if (order_type == 'buy_market'):
                        price_ = '市价'
                    elif (order_type == 'sell_market'):
                        price_ = '市价'
                    data['order_id'] = order_id
                    data['data'] = ('下单成功, 交易所: {}, 标的: {}, '
                                    '价格: {}, 数量: {}').format(
                                    exchange, symbol, price_, amount)
                else:
                    data = '下单失败！'
                    return self.ret_resp(0, data)
            elif (exchange == 'binance'):
                if (order_type == 'buy_limit'):
                    order_type_ = 'BUY_LIMIT'
                elif (order_type == 'buy_market'):
                    price = ''
                    order_type_ = 'BUY_MARKET'
                elif (order_type == 'sell_limit'):
                    order_type_ = 'SELL_LIMIT'
                elif (order_type == 'sell_market'):
                    price = ''
                    order_type_ = 'SELL_MARKET'
                else:
                    data = '输入订单类型不正确!'
                    return self.ret_resp(0, data)

                side = order_type_.split('_')[0]
                type_ = order_type_.split('_')[1]
                quantity = amount
                timeInForce = 'GTC'
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                order_id = trade_ba.new_order(symbol, side, type_, price,
                           quantity, timeInForce, api_dict['api_key'],
                           api_dict['secret_key'])
                if (int(order_id) != 0):
                    price_ = price
                    if (order_type == 'buy_market'):
                        price_ = '市价'
                    elif (order_type == 'sell_market'):
                        price_ = '市价'
                    data['order_id'] = order_id
                    data['data'] = ('下单成功, 交易所: {}, 标的: {}, '
                                    '价格: {}, 数量: {}').format(
                                    exchange, symbol, price_, amount)
                else:
                    data = '下单失败！'
                    return self.ret_resp(0, data)
            elif (exchange == 'okexf'):
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                order_id = trade_okf.future_trade(symbol, order_type,
                           api_dict['api_key'], api_dict['secret_key'],
                           int(amount), price)
                if (order_id != 0 and order_id != ''):
                    price_ = price
                    if ('market' in order_type):
                        price_ = '对手价'
                    else:
                        pass
                    data['order_id'] = order_id
                    data['data'] = ('下单成功, 交易所: {}, 标的: {}, '
                                    '价格: {}, 数量: {}').format(
                                    exchange, symbol, price_, amount)
                else:
                    data = '下单失败！'
                    return self.ret_resp(0, data)
            elif (exchange == 'huobif'):
                if (order_type == 'limit_going_long'):
                    direction = 'buy'  # sell
                    offset = 'open'  # close
                    order_price_type = 'limit'  # opponent
                elif (order_type == 'limit_going_short'):
                    direction = 'sell'
                    offset = 'open'
                    order_price_type = 'limit'
                elif (order_type == 'market_going_long'):
                    direction = 'buy'
                    offset = 'open'
                    order_price_type = 'opponent'
                elif (order_type == 'market_going_short'):
                    direction = 'sell'
                    offset = 'open'
                    order_price_type = 'opponent'
                elif (order_type == 'limit_close_long'):
                    direction = 'sell'
                    offset = 'close'
                    order_price_type = 'limit'
                elif (order_type == 'limit_close_short'):
                    direction = 'buy'
                    offset = 'close'
                    order_price_type = 'limit'
                elif (order_type == 'market_close_long'):
                    direction = 'sell'
                    offset = 'close'
                    order_price_type = 'opponent'
                elif (order_type == 'market_close_short'):
                    direction = 'buy'
                    offset = 'close'
                    order_price_type = 'opponent'
                else:
                    data = '输入订单类型不正确!'
                    return self.ret_resp(0, data)
                symbol_, contract_type = (symbol.split('_')[0].upper(),
                                          symbol.split('-')[1])
                contract_code = ''
                volume = int(amount)
                lever_rate = '10'
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                order_id = trade_hbf.contract_order(symbol_, contract_type,
                           contract_code, price, volume, direction, offset,
                           lever_rate, order_price_type,
                           api_dict['api_key'], api_dict['secret_key'])
                if (int(order_id) != 0):
                    price_ = price
                    if ('market' in order_type):
                        price_ = '对手价'
                    else:
                        pass
                    data['order_id'] = order_id
                    data['data'] = ('下单成功, 交易所: {}, 标的: {}, '
                                    '价格: {}, 数量: {}').format(
                                    exchange, symbol_, price_, amount)
                else:
                    data = '下单失败！'
                    return self.ret_resp(0, data)
            elif (exchange == 'ctp'):
                trade_ctp = TradeCtp()
                status, data = trade_ctp.execute_order(user_id, exchange,
                               account_type, strategy_name, symbol, order_type,
                               str(price), str(amount), str(money_num),
                               str(exec_ts), strategy_instance_id, close_today)
            else:
                data = '暂不支持的交易所!'
                return self.ret_resp(0, data)
            if ((status == 1) and (exchange != 'ctp')):
                order = Order()
                order.user_name = user.user_name
                order.user_id = user.id
                order.phone_num = user.phone_num
                order.exchange = exchange
                order.account_type = account_type
                if (strategy_instance_id != ''):
                    order.strategy_instance_id = ObjectId(strategy_instance_id)
                order.strategy_name = strategy_name
                order.symbol = symbol
                order.order_type = order_type
                order.order_id = str(order_id)
                order.price = str(price)
                order.avg_price = 0.0
                order.quantity = str(amount)
                order.quantity_treaded = 0.0
                order.quantity_frozen = 0.0
                order.quantity_canceled = 0.0
                order.order_cancel_timestamp = 0.0
                order.order_deal_timestamp = 0.0
                order.order_status = 'pending'
                order.save()
            print(user_id, exchange, account_type, strategy_name, symbol,
                  order_type, price, amount, money_num, exec_ts,
                  strategy_instance_id, close_today)
        except Exception as e:
            data = 'err: {}'.format(traceback.format_exc())
            return self.ret_resp(0, data)
        return self.ret_resp(status, data)

    def gen_local_order_id(self):
        return str(uuid.uuid4())

    def execute_backtest_order(self, user_id, exchange, account_type, symbol, order_type, strategy_name, price, amount, exec_ts, strategy_instance_id, user=None):
        order_id = gen_local_order_id()
        status = 1
        data = {}
        data['order_id'] = order_id
        data['data'] = 'ok'
        timestamp = exec_ts
        order_datetime = datetime.datetime.fromtimestamp(timestamp)
        order_timestamp = timestamp
        order_deal_timestamp = timestamp
        if user is None:
            user = User.objects.get(id=user_id)
        order = Order()
        order.order_datetime = order_datetime
        order.order_timestamp = order_timestamp
        order.user_name = user.user_name
        order.user_id = user.id
        order.phone_num = user.phone_num
        order.exchange = exchange
        order.account_type = account_type
        if (strategy_instance_id != ''):
            order.strategy_instance_id = ObjectId(strategy_instance_id)
        order.strategy_name = strategy_name
        order.symbol = symbol
        order.order_type = order_type
        order.order_id = str(order_id)
        order.price = str(price)
        order.avg_price = float(price)
        order.quantity = str(amount)
        order.quantity_treaded = float(amount)
        order.quantity_frozen = 0.0
        order.quantity_canceled = 0.0
        order.order_cancel_timestamp = 0.0
        order.order_deal_timestamp = order_deal_timestamp
        order.order_status = 'filled'
        order.save()
        return status, data

    def fetch_open_orders(self, sig, user_id, exchange, account_type, strategy_name, symbol):
        if not self.check_sig(sig, 'fetch_open_orders', user_id, exchange,
                              account_type, strategy_name, symbol):
            data = 'wrong sig'
            return self.ret_resp(0, data)
        order_status_list = ['pending', 'partial_filled']
        orders = Order.objects.filter(user_id=user_id,
                                      exchange=exchange.lower(),
                                      account_type=account_type,
                                      strategy_name=strategy_name,
                                      order_status__in=order_status_list,
                                      symbol=symbol
                                      ).order_by('-order_timestamp')
        order_list = [order.to_dict() for order in orders]
        data = {}
        data['order_list'] = order_list
        return self.ret_resp(1, data)

    def fetch_orders(self, sig, user_id, exchange, account_type, strategy_name, symbol, order_id):
        if not self.check_sig(sig, 'fetch_orders', user_id, exchange,
                              account_type, strategy_name, symbol,
                              order_id):
            data = 'wrong sig'
            return self.ret_resp(0, data)
        orders = Order.objects.filter(user_id=user_id, exchange=exchange.lower(), account_type=account_type, strategy_name=strategy_name, order_id=order_id, symbol=symbol)
        data = [order.to_dict() for order in orders]
        return self.ret_resp(1, data)

    def get_orders(self, sig, user_id, exchange, account_type, strategy_name, symbol, order_status, page_num, page_limit):
        if not self.check_sig(sig, 'get_orders', user_id, exchange,
                              account_type, strategy_name, symbol,
                              order_status, page_num, page_limit):
            data = 'wrong sig'
            return self.ret_resp(0, data)
        page_limit = int(page_limit)
        page_num = int(page_num)
        offset = (page_num - 1) * page_limit
        if (order_status == 'order_pending'):
            order_status_list = ['pending', 'partial_filled']
        elif (order_status == 'order_filled'):
            order_status_list = ['filled']
        elif (order_status == 'order_cancel'):
            order_status_list = ['cancelled']
        else:
            order_status_list = ['filled']
        if (len(strategy_name) == 24):
            total_count = Order.objects.filter(user_id=user_id, account_type=account_type, strategy_name=strategy_name, order_status__in=order_status_list).count()
            orders = Order.objects.filter(user_id=user_id, account_type=account_type, strategy_name=strategy_name, order_status__in=order_status_list).skip(offset).limit(page_limit).order_by('-order_timestamp')
        else:
            total_count = Order.objects.filter(user_id=user_id, exchange=exchange.lower(), account_type=account_type, strategy_name=strategy_name, order_status__in=order_status_list, symbol=symbol).count()
            orders = Order.objects.filter(user_id=user_id, exchange=exchange.lower(), account_type=account_type, strategy_name=strategy_name, order_status__in=order_status_list, symbol=symbol).skip(offset).limit(page_limit).order_by('-order_timestamp')
        order_list = [order.to_dict() for order in orders]
        total_pages = total_count / page_limit
        shift = 1
        if total_pages % 1 > 0:
            shift = 2
        total_pages = int(total_pages)
        page_num_list = list(range(1, total_pages+shift))
        if (total_pages > 5):
            if (page_num-2 < 1):
                page_num_list = list(range(1, 6))
            elif (page_num+2 > total_pages):
                page_num_list = list(range(page_num-4, page_num+1))
            else:
                page_num_list = list(range(page_num-2, page_num+3))
        data = {}
        data['page_num'] = page_num
        data['page_num_list'] = page_num_list
        data['order_list'] = order_list
        return self.ret_resp(1, data)

    def get_strategy_orders(self, sig, user_id, strategy_instance_id, order_status, page_num, page_limit):
        if not self.check_sig(sig, 'get_strategy_orders', user_id,
                              strategy_instance_id, order_status,
                              page_num, page_limit):
            data = 'wrong sig'
            return self.ret_resp(0, data)
        page_limit = int(page_limit)
        page_num = int(page_num)
        offset = (page_num - 1) * page_limit
        if (order_status == 'order_pending'):
            order_status_list = ['pending', 'partial_filled']
        elif (order_status == 'order_filled'):
            order_status_list = ['filled']
        elif (order_status == 'order_cancel'):
            order_status_list = ['cancelled']
        else:
            order_status_list = ['filled']
        total_count = Order.objects.filter(user_id=user_id, strategy_instance_id=strategy_instance_id, order_status__in=order_status_list).count()
        orders = Order.objects.filter(user_id=user_id, strategy_instance_id=strategy_instance_id, order_status__in=order_status_list).skip(offset).limit(page_limit).order_by('-order_timestamp')
        order_list = [order.to_dict() for order in orders]
        total_pages = total_count / page_limit
        shift = 1
        if total_pages % 1 > 0:
            shift = 2
        total_pages = int(total_pages)
        page_num_list = list(range(1, total_pages+shift))
        if (total_pages > 5):
            if (page_num-2 < 1):
                page_num_list = list(range(1, 6))
            elif (page_num+2 > total_pages):
                page_num_list = list(range(page_num-4, page_num+1))
            else:
                page_num_list = list(range(page_num-2, page_num+3))
        data = {}
        data['page_num'] = page_num
        data['page_num_list'] = page_num_list
        data['order_list'] = order_list
        return self.ret_resp(1, data)

    def cancel_order(self, sig, user_id, exchange, account_type, strategy_name, symbol, order_id):
        if not self.check_sig(sig, 'cancel_order', user_id, exchange,
                              account_type, strategy_name, symbol, order_id):
            data = 'wrong sig'
            return self.ret_resp(0, data)
        status = 1
        data = {}
        if (account_type == 'reg_emulator'):
            exchange = exchange.lower()
            order = Order.objects.get(user_id=user_id, exchange=exchange, account_type=account_type, strategy_name=strategy_name, symbol=symbol, order_id=order_id)
            order_status_ = order.order_status
            if (order_status_ == 'pending'):
                order_status = 'cancelled'
                order.order_status = order_status
                order.save()
                data['result'] = True
                data['data'] = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
            else:
                data = '订单撤销失败！'
                self.ret_resp(0, data)
        elif (account_type == 'reg_trade'):
            data = '暂不支持！'
            self.ret_resp(0, data)
        # 进入实盘api撤单
        try:
            user = User.objects.get(id=user_id)
            if (exchange == 'okex'):
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                api_key = api_dict['api_key']
                secret_key = api_dict['secret_key']
                id = order_id
                result = trade_ok.cancel_order(symbol, id, api_key, secret_key)
                if (result is True):
                    data['result'] = True
                    data['data'] = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
                else:
                    data = '订单撤销失败！'
                    self.ret_resp(0, data)
            elif (exchange == 'huobi'):
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                api_key = api_dict['api_key']
                secret_key = api_dict['secret_key']
                result = trade_hb.submit_cancel(order_id, api_key, secret_key)
                if (result is True):
                    data['result'] = True
                    data['data'] = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
                else:
                    data = '订单撤销失败！'
                    self.ret_resp(0, data)
            elif (exchange == 'binance'):
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                api_key = api_dict['api_key']
                secret_key = api_dict['secret_key']
                orderId = order_id
                recvWindow = 10000000
                result = trade_ba.cancel_order(symbol, orderId, recvWindow,
                                               api_key, secret_key)
                if (result is True):
                    data['result'] = True
                    data['data'] = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
                else:
                    data = '订单撤销失败！'
                    self.ret_resp(0, data)
            elif (exchange == 'okexf'):
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                api_key = api_dict['api_key']
                secret_key = api_dict['secret_key']
                result = trade_okf.future_cancel(symbol, order_id, api_key, secret_key)
                if (result is True):
                    data['result'] = True
                    data['data'] = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
                else:
                    data = '订单撤销失败！'
                    self.ret_resp(0, data)
            elif (exchange == 'huobif'):
                api_dict = user_api.get_api_dict_fast(user, exchange, account_type)
                api_key = api_dict['api_key']
                secret_key = api_dict['secret_key']
                symbol_ = symbol.split('_')[0].upper()
                result = trade_hbf.contract_cancel(symbol_, api_key,
                         secret_key, order_id)
                if (result is True):
                    data['result'] = True
                    data = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
                else:
                    data = '订单撤销失败！'
                    self.ret_resp(0, data)
            elif (exchange == 'ctp'):
                trade_ctp = TradeCtp()
                status, data = trade_ctp.cancel_order(user_id, exchange,
                               account_type, strategy_name, symbol, order_id)
            else:
                data = '暂不支持的交易所!'
                self.ret_resp(0, data)
        except Exception as e:
            data = 'err: {}'.format(traceback.format_exc())
            self.ret_resp(0, data)
        return self.ret_resp(1, data)


def run():
    rpc_node = cfg['rpc_node']
    host = rpc_node['ip']
    port = rpc_node['port']
    print('[*] {}:{}, server running'.format(host, port))
    de_thrift = thriftpy2.load("dao_execute/rpc/dao_execute.thrift", module_name="de_thrift")
    server = make_server(de_thrift.DaoExecute, Dispatcher(), host, port, client_timeout=10000)
    server.serve()
