# coding=utf-8

import pathmagic

from dao_quote.util.quote_save import quote_save
from dao_quote.settings import config_compute


def test_get_mongo_db():
    MONGO_HOST = config_compute.MONGO_HOST
    MONGO_PORT = config_compute.MONGO_PORT
    MONGO_DB_NAME = config_compute.MONGO_DB_NAME
    MONGO_USER = config_compute.MONGO_USER
    MONGO_PWD = config_compute.MONGO_PWD

    mongo_db = quote_save.get_mongo_db(MONGO_HOST, MONGO_PORT, MONGO_DB_NAME,
                                       MONGO_USER, MONGO_PWD)
    return mongo_db


def test_save_mongo_bar():
    mongo_db = test_get_mongo_db()
    key_name = 'daotec_btc_usd_kline'
    data = [
        [1561602883000, 110000, 110000, 110000, 110000, 1100, 1100],
        [1561602889000, 700000, 900000, 500000, 700000, 7000, 7000]
    ]
    rst = quote_save.save_mongo_bar(mongo_db, key_name, data)
    print(rst)
    data = [
        [1561602873000, 110000, 110000, 110000, 110000, 1100],
        [1561602879000, 700000, 900000, 500000, 700000, 7000]
    ]
    rst = quote_save.save_mongo_bar(mongo_db, key_name, data)
    print(rst)


def main():
    test_save_mongo_bar()


if __name__ == '__main__':
    main()
