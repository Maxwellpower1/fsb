# coding=utf-8

import time
import pymongo
import sqlite3
import traceback


def get_db_name():
    timestamp = time.time()
    format = '%Y%m%d'
    value = time.localtime(timestamp)
    date = time.strftime(format, value)
    db_name = 'quote_{}.db'.format(date)
    return db_name


def get_db_conn(db_name):
    conn = sqlite3.connect(db_name, timeout=21)
    return conn


def create_index(conn, key_name, index_name):
    c = conn.cursor()
    try:
        c.execute('''CREATE INDEX "{}" ON "{}"(TIMESTAMP);'''.format(
                  index_name, key_name))
        conn.commit()
    except Exception as e:
        if ('no such table' in str(e)):
            pass
        else:
            print(key_name, traceback.format_exc())


def create_table_tick(conn, table_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASK       FLOAT    NOT NULL,
                  A_V       FLOAT    NOT NULL,
                  BID       FLOAT    NOT NULL,
                  B_V       FLOAT    NOT NULL,
                  LAST      FLOAT    NOT NULL,
                  OPEN      FLOAT    NOT NULL,
                  HIGH      FLOAT    NOT NULL,
                  LOW       FLOAT    NOT NULL,
                  VOL       FLOAT    NOT NULL,
                  AMT       FLOAT    NOT NULL,
                  INST      FLOAT    NOT NULL,
                  PRE_CLOSE FLOAT    ,
                  UP_LIMIT  FLOAT    ,
                  DOWN_LIMIT FLOAT   ,
                  ASK_2     FLOAT    ,
                  ASK_3     FLOAT    ,
                  ASK_4     FLOAT    ,
                  ASK_5     FLOAT    ,
                  BID_2     FLOAT    ,
                  BID_3     FLOAT    ,
                  BID_4     FLOAT    ,
                  BID_5     FLOAT    ,
                  A_V_2     FLOAT    ,
                  A_V_3     FLOAT    ,
                  A_V_4     FLOAT    ,
                  A_V_5     FLOAT    ,
                  B_V_2     FLOAT    ,
                  B_V_3     FLOAT    ,
                  B_V_4     FLOAT    ,
                  B_V_5     FLOAT
                  );'''.format(table_name))
    conn.commit()


def create_table_bar(conn, key_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  TIMESTAMP   INTEGER PRIMARY KEY NOT NULL,
                  OPEN        FLOAT    NOT NULL,
                  HIGH        FLOAT    NOT NULL,
                  LOW         FLOAT    NOT NULL,
                  CLOSE       FLOAT    NOT NULL,
                  VOLUME      FLOAT    NOT NULL,
                  VOLUME_COIN FLOAT    NOT NULL
                  );'''.format(key_name))
    conn.commit()


def create_table_depth(conn, table_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASKS      TEXT     NOT NULL,
                  BIDS      TEXT     NOT NULL
                  );'''.format(table_name))
    conn.commit()


def create_table_depthall(conn, table_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASKS      TEXT     NOT NULL,
                  BIDS      TEXT     NOT NULL
                  );'''.format(table_name))
    conn.commit()


def create_table_trade(conn, table_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  TRADE_ID  INTEGER  NOT NULL,
                  PRICE     FLOAT    NOT NULL,
                  SIZE      FLOAT    NOT NULL,
                  SIDE      TEXT    NOT NULL
                  );'''.format(table_name))
    conn.commit()


def get_mongo_db(MONGO_HOST, MONGO_PORT, MONGO_DB_NAME, MONGO_USER, MONGO_PWD):
    con = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
    dao_quote = con[MONGO_DB_NAME]  # new a database
    try:
        dao_quote.authenticate(MONGO_USER, MONGO_PWD)
    except Exception as e:
        if (str(e) == 'Authentication failed.'):
            dao_quote.add_user(MONGO_USER, MONGO_PWD)
            dao_quote.authenticate(MONGO_USER, MONGO_PWD)
    return dao_quote


def save_table_tick(conn, table_name, data):
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASK,A_V,BID,B_V,LAST,OPEN,HIGH,LOW,VOL,AMT,INST,'
               'PRE_CLOSE,UP_LIMIT,DOWN_LIMIT,ASK_2,ASK_3,ASK_4,ASK_5,BID_2,BID_3,BID_4,BID_5,'
               'A_V_2,A_V_3,A_V_4,A_V_5,B_V_2,B_V_3,B_V_4,B_V_5) '
               'VALUES ({},{},{},{},{},{},{},{},{},{},{},{},'
               '{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})').format(
               table_name, data['ts'], data['ask'], data.get('a_v', 0.0),
               data['bid'], data.get('b_v', 0.0), data['last'],
               data.get('open', 0.0), data['high'], data['low'], data['vol'],
               data.get('amt', 0.0), data.get('inst', 0.0),
               data.get('pre_close', 0.0), data.get('up_limit', 0.0), data.get('down_limit', 0.0),
               data.get('ask_2', 0.0), data.get('ask_3', 0.0), data.get('ask_4', 0.0), data.get('ask_5', 0.0),
               data.get('bid_2', 0.0), data.get('bid_3', 0.0), data.get('bid_4', 0.0), data.get('bid_5', 0.0),
               data.get('a_v_2', 0), data.get('a_v_3', 0), data.get('a_v_4', 0), data.get('a_v_5', 0),
               data.get('b_v_2', 0), data.get('b_v_3', 0), data.get('b_v_4', 0), data.get('b_v_5', 0)))
    # conn.commit()


def save_tick(conn, key_name, data):
    table_name = key_name
    try:
        save_table_tick(conn, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            create_table_tick(conn, table_name)
            save_table_tick(conn, table_name, data)
        else:
            print(key_name, e)
            conn.commit()
            raise


def save_table_depth(conn, table_name, data):
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASKS,BIDS) '
               'VALUES ({},"{}","{}")').format(
               table_name, data['ts'], data['asks'], data['bids']))
    # conn.commit()


def save_depth(conn, key_name, data):
    table_name = key_name
    try:
        save_table_depth(conn, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_depth(conn, table_name)
                save_table_depth(conn, table_name, data)
            except Exception as e:
                conn.commit()
                raise
        else:
            print(key_name, e)
            conn.commit()
            raise


def save_table_depthall(conn, table_name, data):
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASKS,BIDS) '
               'VALUES ({},"{}","{}")').format(
               table_name, data['ts'], data.get('asks', []), data.get('bids', [])))
    # conn.commit()


def save_depthall(conn, key_name, data):
    table_name = key_name
    try:
        save_table_depthall(conn, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_depthall(conn, table_name)
                save_table_depthall(conn, table_name, data)
            except Exception as e:
                conn.commit()
                raise
        else:
            print(key_name, e)
            conn.commit()
            raise


def save_table_trade(conn, table_name, data):
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,TRADE_ID,PRICE,SIZE,SIDE) '
               'VALUES ({},{},{},{},"{}")').format(
               table_name, data['ts'], data['trade_id'], data['price'],
               data['size'], data['side']))
    # conn.commit()


def save_trade(conn, key_name, data):
    table_name = key_name
    try:
        save_table_trade(conn, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_trade(conn, table_name)
                save_table_trade(conn, table_name, data)
            except Exception as e:
                conn.commit()
                raise
        else:
            print(key_name, e)
            conn.commit()
            raise


def save_table_bar(conn, key_name, data):
    c = conn.cursor()
    for i in data:
        if (len(i) < 7):
            volume_coin = 0
        else:
            volume_coin = i[6]
        try:
            c.execute(('REPLACE INTO "{}" (TIMESTAMP,OPEN,HIGH,LOW,'
                       'CLOSE,VOLUME,VOLUME_COIN) VALUES '
                       '({},{},{},{},{},{},{})').format(
                       key_name, i[0], i[1], i[2], i[3], i[4], i[5],
                       volume_coin))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                # break
                pass
            else:
                raise
    conn.commit()


def save_bar(conn, key_name, data):
    table_name = key_name
    try:
        save_table_bar(conn, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_bar(conn, table_name)
                save_table_bar(conn, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def save_mongo_bar(mongo_db, key_name, data):
    collection = mongo_db[key_name]
    if (len(data[0]) < 7):
        volume_coin = 0
        for i in data:
            bar_dict = {'_id': i[0], 'open': i[1], 'high': i[2],
                        'low': i[3], 'close': i[4], 'volume': i[5],
                        'volume_coin': volume_coin}
            collection.save(bar_dict)
    else:
        for i in data:
            bar_dict = {'_id': i[0], 'open': i[1], 'high': i[2],
                        'low': i[3], 'close': i[4], 'volume': i[5],
                        'volume_coin': i[6]}
            collection.save(bar_dict)
    return True


def main():
    pass


if __name__ == '__main__':
    main()
