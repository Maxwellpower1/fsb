
import os
import yaml


def get_yaml():
    file_path = os.path.split(os.path.realpath(__file__))[0]
    file_name = '/dev_config.yaml'
    full_name = file_path + file_name
    f = open(full_name)
    y = yaml.load(f, Loader=yaml.SafeLoader)
    f.close()
    return y


cfg = get_yaml()
