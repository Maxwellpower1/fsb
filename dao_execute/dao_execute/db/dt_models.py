import time
import datetime

from bson.objectid import ObjectId
from mongoengine import fields
from mongoengine import connect
from mongoengine import Document, EmbeddedDocument

from dao_execute.settings.config import cfg


def get_connect():
    db_name = 'dao_trade'
    mongo_cfg = cfg['mongo'][db_name]
    mode = mongo_cfg['mode']
    connstr = mongo_cfg['connstr']
    db_name = mongo_cfg['db_name']
    db_user = mongo_cfg['db_user']
    db_pwd = mongo_cfg['db_pwd']
    if mode == 'ReplicaSet':
        repl_name = mongo_cfg['repl_name']
        connect(repl_name, host=connstr.format(db_user, db_pwd, db_name))
    elif mode == 'single':
        host, port = connstr.split(':')
        connect(db_name, host=host, port=int(port), username=db_user,
                password=db_pwd)
    else:
        print('[*] no db config, exit')
        sys.exit(0)


get_connect()


class User(Document):
    created_time = fields.DateTimeField(
        default=datetime.datetime.now, editable=False,
    )
    user_name = fields.StringField(max_length=250)
    phone_num = fields.StringField(max_length=250)
    phone_zone_code = fields.StringField(max_length=250)
    password = fields.StringField(max_length=64)
    sms_vcode = fields.StringField(default='')
    img_vcode = fields.StringField(default='')
    ex_aes_key = fields.StringField(default='', max_length=64)
    invitor = fields.StringField(max_length=250)
    feishu_api = fields.StringField(default='', max_length=250)
    agree = fields.StringField(max_length=250)
    google_auth_secret = fields.StringField(default='', max_length=250)
    exchange = fields.DictField()

    def __unicode__(self):
        return self.user_name


class ExAccount(Document):
    created_time = fields.DateTimeField(
        default=datetime.datetime.now, editable=False,
    )
    user_id = fields.ObjectIdField(unique_with=['ex_account_name', 'exchange'])
    user_name = fields.StringField(max_length=250)
    phone_num = fields.StringField(max_length=250)
    ex_account_name = fields.StringField(default='', max_length=250)
    exchange = fields.StringField(default='', max_length=250)
    maker = fields.StringField(default='0', max_length=250)
    taker = fields.StringField(default='0', max_length=250)
    api_key = fields.StringField(default='', max_length=250)
    secret_key = fields.StringField(default='', max_length=250)
    broker_id = fields.StringField(default='', max_length=250)
    md_address = fields.StringField(default='', max_length=250)
    td_address = fields.StringField(default='', max_length=250)
    ctp_taker = fields.StringField(default='0', max_length=250)
    ctp_app_id = fields.StringField(default='', max_length=250)
    ctp_auth_code = fields.StringField(default='', max_length=250)

    def __unicode__(self):
        return self.user_name


class Order(Document):
    order_datetime = fields.DateTimeField(
        default=datetime.datetime.now, editable=False,
    )
    order_timestamp = fields.FloatField(
        default=time.time, editable=False,
    )
    user_name = fields.StringField(max_length=250)
    user_id = fields.ObjectIdField()
    phone_num = fields.StringField(max_length=250)
    exchange = fields.StringField(max_length=250)
    account_type = fields.StringField(max_length=250)  # default='api_bind',
    strategy_instance_id = fields.ObjectIdField(default=ObjectId)
    strategy_name = fields.StringField(max_length=250)  # default='manual',
    symbol = fields.StringField(max_length=250)
    order_type = fields.StringField(max_length=250)
    order_id = fields.StringField(max_length=250)
    price = fields.StringField(max_length=250)
    avg_price = fields.FloatField()
    quantity = fields.StringField(max_length=250)
    quantity_treaded = fields.FloatField()
    quantity_frozen = fields.FloatField()
    quantity_canceled = fields.FloatField()
    order_cancel_timestamp = fields.FloatField()
    order_deal_timestamp = fields.FloatField()
    order_status = fields.StringField(max_length=250)
    trading_day = fields.StringField(default='')

    def __unicode__(self):
        return self.order_id

    def to_dict(self):
        order_dict = {}
        order_dict['id'] =str(self.id)
        order_dict['order_datetime'] = str(self.order_datetime)
        order_dict['order_timestamp'] = self.order_timestamp
        order_dict['user_name'] = self.user_name
        order_dict['user_id'] = str(self.user_id)
        order_dict['phone_num'] = self.phone_num
        order_dict['exchange'] = self.exchange
        order_dict['account_type'] = self.account_type
        order_dict['strategy_instance_id'] = str(self.strategy_instance_id)
        order_dict['strategy_name'] = self.strategy_name
        order_dict['symbol'] = self.symbol
        order_dict['order_type'] = self.order_type
        order_dict['order_id'] = self.order_id
        order_dict['price'] = self.price
        order_dict['avg_price'] = self.avg_price
        order_dict['quantity'] = self.quantity
        order_dict['quantity_treaded'] = self.quantity_treaded
        order_dict['quantity_frozen'] = self.quantity_frozen
        order_dict['quantity_canceled'] = self.quantity_canceled
        order_dict['order_cancel_timestamp'] = self.order_cancel_timestamp
        order_dict['order_deal_timestamp'] = self.order_deal_timestamp
        order_dict['order_status'] = self.order_status
        return order_dict


class ComplexOrder(Document):
    order_datetime = fields.DateTimeField(
        default=datetime.datetime.now, editable=False,
    )
    order_timestamp = fields.FloatField(
        default=time.time, editable=False,
    )
    user_name = fields.StringField(max_length=250)
    user_id = fields.ObjectIdField()
    phone_num = fields.StringField(max_length=250)
    exchange = fields.StringField(max_length=250)
    account_type = fields.StringField(max_length=250)  # default='api_bind',
    strategy_name = fields.StringField(max_length=250)  # default='manual',
    symbol = fields.StringField(max_length=250)
    order_type = fields.StringField(max_length=250)
    order_id = fields.StringField(max_length=250)
    sub_order_type = fields.StringField(max_length=250)  # if/oco1
    execution_type_1 = fields.StringField(max_length=250)
    price = fields.StringField(max_length=250)
    quantity = fields.StringField(max_length=250)

    order_id_1 = fields.StringField(default='0', max_length=250)
    timeout_1 = fields.FloatField()

    price_2 = fields.FloatField()  # done/oco2
    order_id_2 = fields.StringField(default='0', max_length=250)
    execution_type_2 = fields.StringField(
        default='', max_length=250
    )
    timeout_2 = fields.FloatField(default=0.0)

    price_3 = fields.FloatField(default=0.0) # ifo(oco1)
    order_id_3 = fields.StringField(default='0', max_length=250)
    quantity_treaded_3 = fields.FloatField(default=0.0)

    quantity_treaded = fields.FloatField(default=0.0)
    quantity_frozen = fields.FloatField(default=0.0)
    quantity_canceled = fields.FloatField(default=0.0)
    order_cancel_timestamp = fields.FloatField(default=0.0)
    order_deal_timestamp = fields.FloatField(default=0.0)
    order_status = fields.StringField(max_length=250)

    def __unicode__(self):
        return self.order_id


class DaoLog(Document):
    log_datetime = fields.DateTimeField(
        default=datetime.datetime.now, editable=False,
    )
    log_timestamp = fields.FloatField(
        default=time.time, editable=False,
    )
    log_level = fields.StringField(max_length=250)
    log_type = fields.StringField(max_length=250)
    user_name = fields.StringField(max_length=250)
    user_id = fields.ObjectIdField()
    phone_num = fields.StringField(max_length=250)
    log_message = fields.StringField()
    strategy_name = fields.StringField(max_length=250)
    strategy_instance_id = fields.StringField(max_length=250)
    strategy_type = fields.StringField(max_length=250)
    account_type = fields.StringField(max_length=250)
    exchange = fields.StringField(max_length=250)
    symbol = fields.StringField(max_length=250)

    def __unicode__(self):
        return self.log_level
