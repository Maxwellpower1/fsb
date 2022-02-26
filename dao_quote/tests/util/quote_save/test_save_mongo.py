#coding=utf-8

import pathmagic

from dao_quote.util.quote_fetch import quote_fetch
from dao_quote.util.quote_save import save_mongo


def test_save_db():
    db = save_mongo.get_db()
    collection = 'test'
    for i in range(0, 1000):
        collection_dict = {}
        collection_dict['_id'] = 'value{}'.format(i)
        collection_dict['test_key_{}'.format(i)] = 'value{}'.format(i)
        rst = save_mongo.save_db(db, collection, collection_dict)
    # collection_dict = {'test_key_1': 'value1', 'test_key_2': 'value2'}
    # rst = save_mongo.save_db(db, collection, collection_dict)
    print(rst)


def test_insert_many_db():
    db = save_mongo.get_db()
    collection = 'test'
    collection_dict_list = []
    for i in range(0, 1000):
        collection_dict = {}
        # collection_dict['_id'] = 'value{}'.format(i)
        collection_dict['test_key_{}'.format(i)] = 'value{}'.format(i)
        collection_dict_list.append(collection_dict)
    rst = save_mongo.insert_many_db(db, collection, collection_dict_list)
    print(rst)


def test_resave_ticks():
    exchange = 'okexf'
    symbol = 'btc_usd-quarter'
    begin_time = '2020-01-15 00:00:00'
    end_time = '2020-01-15 23:59:59'
    tick_dict_list = quote_fetch.get_ticks(exchange, symbol, begin_time, end_time)
    # with open('test.txt', 'w+') as f:
    #     f.write(str(tick_dict_list))
    db = save_mongo.get_db()
    collection = '{}_{}_hfd'.format(exchange, symbol)
    rst = save_mongo.insert_many_db(db, collection, tick_dict_list)
    print(rst)


def test_resave_depths():
    exchange = 'okexf'
    symbol = 'btc_usd-quarter'
    begin_time = '2020-01-15 00:00:00'
    end_time = '2020-01-15 23:59:59'
    depth_dict_list = quote_fetch.get_depths(exchange, symbol, begin_time, end_time)
    db = save_mongo.get_db()
    collection = '{}_{}_hfd'.format(exchange, symbol)
    rst = save_mongo.insert_many_db(db, collection, depth_dict_list)
    print(rst)


def main():
    test_save_db()
    # test_insert_many_db()
    # test_resave_ticks()
    # test_resave_depths()


if __name__ == '__main__':
    main()
