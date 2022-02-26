import time

import pathmagic

from dao_execute.exchange_api.ctp.trade_ctpc import TradeCtp


class testTradeCtp(object):

    def __init__(self):
        self.tc = TradeCtp()

    def test_execute_order(self):
        user_id = '5cb452702a0aa544cd9e0bca'
        exchange = 'ctp'
        account_type = 'haqh'
        strategy_name = 'strategy_1'
        symbol = 'FG201'
        order_type = 'limit_going_long'
        # order_type = 'market_close_long'
        price = '2900'
        amount = '1'
        money_num = '0'
        exec_ts = str(time.time())
        strategy_instance_id = ''
        close_today = True
        status, data = self.tc.execute_order(user_id, exchange,
                       account_type, strategy_name, symbol, order_type,
                       price, amount, money_num, exec_ts,
                       strategy_instance_id, close_today)
        print(status, data)
        return data['order_id']

    def test_cancel_order(self, order_id=''):
        user_id = '5cb452702a0aa544cd9e0bca'
        exchange = 'ctp'
        account_type = 'haqh'
        strategy_name = 'strategy_1'
        symbol = 'FG201'
        if order_id == '':
            order_id = '7393417036223488'
        status, data = self.tc.cancel_order(user_id, exchange, account_type, strategy_name, symbol, order_id)
        print(status, data)

    def main(self):
        order_id = self.test_execute_order()
        time.sleep(3)
        self.test_cancel_order(order_id)
        print('test pass')


def main():
    ttc = testTradeCtp()
    ttc.main()


if __name__ == '__main__':
    main()
