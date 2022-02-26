# coding=utf-8

import ast
import random
import binascii
import traceback
from Crypto.Cipher import AES

from dao_execute.settings.config import cfg
from dao_execute.db.dt_models import ExAccount


def decrypt_aes(msg, aes_key):
    msg = binascii.unhexlify(msg)
    aes_key = aes_key.encode('utf-8')
    decipher = AES.new(aes_key[:24], AES.MODE_ECB)
    msg = decipher.decrypt(msg)
    msg = msg.decode('utf-8').replace('\x10', '')
    return msg


def get_api_dict_fast(user, exchange, ex_account_name):
    ex_aes_key = user.ex_aes_key
    ex_account_list = ExAccount.objects.filter(
        user_id=user.id, ex_account_name=ex_account_name,
        exchange=exchange)
    api_dict = {}
    api_dict['api_key'] = None
    api_dict['secret_key'] = None
    if (len(ex_account_list) > 0) and (ex_aes_key is not None) and (str(ex_aes_key) != ''):
        ex_account = ex_account_list[0]
        aes_root_key = cfg['aes_root_key']
        ex_aes_key = decrypt_aes(ex_aes_key, aes_root_key)
        api_key = ex_account.api_key
        secret_key = ex_account.secret_key
        api_dict['api_key'] = decrypt_aes(api_key, ex_aes_key)
        api_dict['secret_key'] = decrypt_aes(secret_key, ex_aes_key)
        if (ex_account.exchange == 'ctp'):
            api_dict['broker_id'] = ex_account.broker_id
            api_dict['td_address'] = ex_account.td_address
            api_dict['ctp_app_id'] = ex_account.ctp_app_id
            api_dict['ctp_auth_code'] = ex_account.ctp_auth_code
    return api_dict
