import api_key_x
import pathmagic

from dao_execute.exchange_api.okexf import api_okf


class testApiOkf(object):

    def __init__(self):
        self.api_key = api_key_x.API_KEY_V3
        self.secret_key = api_key_x.SECRET_KEY_V3
        self.api_okf = api_okf

    def test_instruments(self):
        resp = self.api_okf.instruments()
        print(resp)


def main():
    tao = testApiOkf()
    tao.test_instruments()


if __name__ == '__main__':
    main()
