import json
import time
import random

import pathmagic

from dao_execute.rpc.dao_execute import DaoExecute


class testDaoExecute(object):

    def __init__(self):
        self.dao_execute = DaoExecute()

    def test_execute_order(self):
        user_id = '5cb452702a0aa544cd9e0bca'
        exchange = 'okexf'
        # exchange = 'ctp'
        # account_type = 'api_bind'
        account_type = 'api_v5'
        strategy_name = 'strategy_1'
        symbol = 'btc_usd-quarter'
        # symbol = 'FG201'
        # order_type = 'market_going_long'
        order_type = 'limit_going_long'
        # order_type = 'market_close_long'
        # price = '2700'
        price = '49000'
        amount = '1'
        money_num = '0'
        exec_ts = str(time.time())
        strategy_instance_id = ''
        close_today = True
        status, data = self.dao_execute.execute_order(user_id, exchange,
                       account_type, strategy_name, symbol, order_type,
                       price, amount, money_num, exec_ts,
                       strategy_instance_id, close_today)
        print(status, data)
        # order_id = str(data['order_id'])
        order_id = data['order_id']
        return order_id

    def test_get_orders(self):
        user_id = '5cb452702a0aa544cd9e0bca'
        exchange = 'okexf'
        account_type = 'api_bind'
        strategy_name = 'strategy_1'
        symbol = 'btc_usd-quarter'
        order_status = 'order_pending' # 'filled'
        page_num = '1'
        page_limit = '10'
        status, data = self.dao_execute.get_orders(user_id, exchange, account_type, strategy_name, symbol, order_status, page_num, page_limit)
        print(status, data)

    def test_get_strategy_orders(self):
        user_id = '5cb452702a0aa544cd9e0bca'
        strategy_instance_id = '5da2e7fb2a0aa51c34785d48'
        order_status = 'filled'
        page_num = '1'
        page_limit = '10'
        status, data = self.dao_execute.get_strategy_orders(user_id, strategy_instance_id, order_status, page_num, page_limit)
        print(status, data)

    def test_cancel_order(self, order_id):
        user_id = '5cb452702a0aa544cd9e0bca'
        exchange = 'okexf'
        # exchange = 'ctp'
        # account_type = 'api_bind'
        account_type = 'api_v5'
        strategy_name = 'strategy_1'
        symbol = 'btc_usd-quarter'
        # symbol = 'FG201'
        if order_id == '':
            order_id = '7393417036223488'
            print('[*] cancel_order id: {}'.format(order_id))
        status, data = self.dao_execute.cancel_order(user_id, exchange, account_type, strategy_name, symbol, order_id)
        print(status, data)

    def test_batch_execute_order(self):
        user_id = '5cb452702a0aa544cd9e0bca'
        exchange = 'ctp'
        account_type = 'ddqh'
        strategy_name = 'manual_trading'
        symbol = 'FG205'
        order_type = 'limit_going_long'
        # price = '2199'
        # amount = '1'
        money_num = '0'
        exec_ts = str(time.time())
        strategy_instance_id = ''
        close_today = True

        for i in range(0, 119):
            price = str(2199+random.randint(1, 20))
            amount = str(random.randint(1, 2))
            status, data = self.dao_execute.execute_order(user_id, exchange,
                           account_type, strategy_name, symbol, order_type,
                           price, amount, money_num, exec_ts,
                           strategy_instance_id, close_today)
            print(status, data)
            if i < 50:
                time.sleep(0.02)
            else:
                time.sleep(0.1)

    def main(self):
        # order_id = self.test_execute_order()
        # self.test_get_orders()
        # self.test_get_strategy_orders()
        # time.sleep(3)
        # self.test_cancel_order(order_id)
        self.test_batch_execute_order()
        print('test_pass')


def main():
    tdu = testDaoExecute()
    tdu.main()


if __name__ == '__main__':
    main()
