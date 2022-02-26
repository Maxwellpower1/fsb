#coding=utf-8

import pathmagic

from dao_quote.util.verify.sms import send_sms
from dao_quote.settings import config_x


def test_send_vcode():
    nationCode = config_x.PHONE_ZONE
    phoneNumber = config_x.ADMIN_PHONE
    code = '111111'
    rst = send_sms.send_vcode(nationCode, phoneNumber, code)
    print(rst)


def main():
    test_send_vcode()


if __name__ == '__main__':
    main()
