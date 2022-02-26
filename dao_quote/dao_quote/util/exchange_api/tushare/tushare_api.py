import json
import requests


class tuShare(object):

    def __init__(self):
        self.api_url = 'http://api.waditu.com'
        self.token = '65e55c7246c3fe4c97cae99e3f27d22cbec7207d7888b6377a166ec4'

    def get(self, exchange, symbol, start_date, end_date):
        params = {}
        params['ts_code'] = '{}.{}'.format(symbol, exchange)
        params['start_date'] = start_date
        params['end_date'] = end_date
        data = {}
        data['api_name'] = 'daily'
        data['token'] = self.token
        data['params'] = params
        data['fields'] = 'ts_code,trade_date,open,high,low,close,pre_close,' \
                         'change,pct_chg,vol,amount'
        data = json.dumps(data)
        resp = requests.post(self.api_url, data=data)
        data = resp.json()
        data = data['data']['items']
        return data

    def get_pkg(self, exchange, symbol, start_date, end_date):
        # pip install tushare
        import tushare as ts
        pro = ts.pro_api(self.token)
        df = pro.daily(**{
            "ts_code": '{}.{}'.format(symbol, exchange),
            "start_date": start_date,
            "end_date": end_date
        }, fields=[
            "ts_code",
            "trade_date",
            "open",
            "high",
            "low",
            "close",
            "pre_close",
            "change",
            "pct_chg",
            "vol",
            "amount"
        ])
        for i in df.iterrows():
            print(list(i[1]))
        print(df)
