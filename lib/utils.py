import json
from os.path import exists

from colored import fg, attr
from ruamel.yaml import YAML


def prompt(desc):
    return input(fg('wheat_1') + desc + attr('reset'))


def load_yaml(conf_path):
    yaml = YAML()
    with open(conf_path) as fd:
        return yaml.load(fd)


def write_yaml(conf_path, conf_dict):
    yaml = YAML()
    fd = open(conf_path, 'w')
    yaml.dump(conf_dict, fd)


def load_json(conf_path):
    fd = open(conf_path)
    return json.load(fd)


def write_json(conf_path, conf_dict):
    fd = open(conf_path, 'w')
    json.dump(conf_dict, fd, indent=2)


config_path = './.config.json'
config_dict = {}

if exists(config_path):
    with open(config_path, 'r') as config_fd:
        config_dict = json.load(config_fd)
    print(fg(10) + 'Found config file' + attr('reset'))

