import pathmagic

from dao_execute.utils import user_api
from dao_execute.db.dt_models import User


def test_get_api_dict_fast():
    user_id = '5cb452702a0aa544cd9e0bca'
    user = User.objects.get(id=user_id)
    exchange = 'ctp'
    ex_account_name = 'haqh'
    api_dict = user_api.get_api_dict_fast(user, exchange, ex_account_name)
    print(api_dict)


def main():
    test_get_api_dict_fast()


if __name__ == '__main__':
    main()
