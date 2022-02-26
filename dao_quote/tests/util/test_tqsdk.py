import tqsdk


def test_kline():
    api = tqsdk.TqApi()
    klines = api.get_kline_serial("DCE.c2009", 60)
    api.close()
    print(klines)


def main():
    test_kline()


if __name__ == '__main__':
    main()
