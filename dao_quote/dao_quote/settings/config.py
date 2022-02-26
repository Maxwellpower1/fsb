
import os
import yaml

from dao_quote.settings import config_x


SDKAPPID = config_x.SDKAPPID
APPKEY = config_x.APPKEY
PHONE_ZONE = config_x.PHONE_ZONE
ADMIN_PHONE = config_x.ADMIN_PHONE

CTP_MD_ADDRESS = config_x.CTP_MD_ADDRESS
CTP_MD_BROKER_ID = config_x.CTP_MD_BROKER_ID
CTP_MD_USER_ID = config_x.CTP_MD_USER_ID
CTP_MD_PASSWORD = config_x.CTP_MD_PASSWORD

MONGODB_NAME = config_x.MONGODB_NAME
MONGODB_HOST = config_x.MONGODB_HOST
MONGODB_PWD = config_x.MONGODB_PWD
MONGODB_USER = config_x.MONGODB_USER

REDIS_HOST = config_x.REDIS_HOST
REDIS_PORT = config_x.REDIS_PORT
REDIS_PWD = config_x.REDIS_PWD

SECRET_KEY = config_x.SECRET_KEY

API_KEY_DICT = config_x.API_KEY_DICT

HFT_TICKER = 't'
HFT_DEPTH = 'd'
HFT_DEPTHALL = 'a'
HFT_TRADE = 'e'
HFT_BAR = 'b'


def get_yaml():
    file_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = '/config_full.yaml'
    full_name = file_path + file_name
    f = open(full_name)
    y = yaml.load(f, Loader=yaml.SafeLoader)
    f.close()
    return y


config_dict = get_yaml()

COLLECT_DICT = config_dict['collect']
RESAVE_DICT = config_dict['resave']
COMPUTE_DICT = config_dict['compute']
