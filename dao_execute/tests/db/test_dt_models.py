import pathmagic

from dao_execute.db.dt_models import (User, ExAccount, Order, ComplexOrder, DaoLog)


def test_user():
    users = User.objects.filter()
    for user in users:
        print(user.created_time, user.user_name, user.feishu_api, user.agree)
        print(user.to_json())
        if user.user_name == '155302999':
            user.agree = '1'
            user.save()


def test_ex_account():
    ex_accounts = ExAccount.objects.filter().limit(10)
    for ex_account in ex_accounts:
        print(ex_account.to_json())


def test_order():
    orders = Order.objects.filter().limit(5)
    for order in orders:
        print(order.to_json())


def test_complex_order():
    c_orders = ComplexOrder.objects.filter().limit(5)
    for c_order in c_orders:
        print(c_order.to_json())


def test_dao_log():
    dao_logs = DaoLog.objects.filter().limit(5)
    for dao_log in dao_logs:
        print(dao_log.to_json())


def main():
    test_user()
    test_ex_account()
    test_order()
    test_complex_order()
    test_dao_log()


if __name__ == '__main__':
    main()
