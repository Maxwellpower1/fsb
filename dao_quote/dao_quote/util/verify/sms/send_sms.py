#! /usr/bin/env python
# coding=utf-8

import ast
import time
import json
import random
import hashlib
import http.client

from dao_quote.settings.config_x import (SDKAPPID, APPKEY)


def sms_sender(nationCode, phoneNumber, content):
    url = "https://yun.tim.qq.com/v5/tlssmssvr/sendsms"
    rnd = random.randint(100000, 999999)
    time_sms = int(time.time())
    sig = hashlib.sha256('appkey={}&random={}&time={}&mobile={}'.format(
                         APPKEY, rnd, time_sms, phoneNumber
                         ).encode("utf-8")).hexdigest()
    pkg = {
        "ext": "",
        "extend": "",
        "msg": content,
        "sig": sig,
        "tel": {
            "mobile": phoneNumber,
            "nationcode": nationCode,
        },
        "time": time_sms,
        "type": 0
    }
    con = None
    data = {'fee': 0}
    try:
        con = http.client.HTTPSConnection('yun.tim.qq.com', timeout=5)
        body = json.dumps(pkg)
        wholeUrl = '{}?sdkappid={}&random={}'.format(
                   url, SDKAPPID, rnd)
        con.request('POST', wholeUrl, body)
        response = con.getresponse()
        resp = response.read()
        resp = resp.decode('utf-8')
        data = ast.literal_eval(resp)
        if 'fee' in data:
            pass
        else:
            data['fee'] = 0
    except Exception as e:
        print(e)
    finally:
        if(con):
            con.close()
    return data


def send_vcode(nationCode, phoneNumber, code):
    content = "【道科技DaoTec】您的验证码是：{}，3分钟内有效，切勿将验证码泄露于他人。".format(code)
    return sms_sender(nationCode, phoneNumber, content)


def send_order_reminder(nationCode, phoneNumber, strategy_name, order_info):
    content = ("【道科技DaoTec】尊敬的客户您好！您运行的{}策略有新订单了，"
                "订单细节为{}，更多行情信息请关注道科技。").format(strategy_name, order_info)
    return sms_sender(nationCode, phoneNumber, content)


def send_strategy_reminder(nationCode, phoneNumber, strategy_name, reminder_type):
    if (reminder_type == 'err'):
        reminder_type = '异常'
    else:
        pass
    content = ("【道科技DaoTec】尊敬的客户您好！您运行的策略{}最新状态为{}，"
                "更多信息请登录道科技。").format(strategy_name, reminder_type)
    return sms_sender(nationCode, phoneNumber, content)


def main():
    pass


if __name__ == "__main__":
    main()
