# coding=utf-8

import pymongo
from bson.objectid import ObjectId

from dao_quote.settings import config_x


def create_db():
    con = pymongo.MongoClient(config_x.MONGODB_HOST, config_x.MONGODB_PORT)
    db = con[config_x.MONGODB_NAME]  # new a database
    db.add_user(config_x.MONGODB_USER, config_x.MONGODB_PWD)


def get_db():
    con = pymongo.MongoClient(config_x.MONGODB_HOST, config_x.MONGODB_PORT)
    db = con[config_x.MONGODB_NAME]
    db.authenticate(config_x.MONGODB_USER, config_x.MONGODB_PWD)
    return db


def save_db(db, collection, collection_dict):
    rst = db[collection].save(collection_dict)
    return rst


def insert_many_db(db, collection, collection_dict_list):
    rst = db[collection].insert_many(collection_dict_list, ordered=True)
    return rst


def create_index(db, collection, index_dict):
    rst = db[collection].create_index(index_dict)
    return rst
