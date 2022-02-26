import pathmagic

from dao_quote.util.exchange_api.tushare.tushare_api import tuShare


class testTuShare(object):

    def __init__(self):
        self.ts = tuShare()

    def test_get(self):
        print('[*] {} test_get {}'.format('*'*20, '*'*20))
        exchange = 'SZ'
        symbol = '000698'
        start_date = '20011101'
        end_date = '20211126'
        self.ts.get(exchange, symbol, start_date, end_date)


    def test_get_pkg(self):
        print('[*] {} test_get_pkg {}'.format('*'*20, '*'*20))
        exchange = 'SZ'
        symbol = '000698'
        start_date = '20211101'
        end_date = '20211126'
        self.ts.get_pkg(exchange, symbol, start_date, end_date)


def main():
    tts = testTuShare()
    tts.test_get()
    # tts.test_get_pkg()


if __name__ == '__main__':
    main()
