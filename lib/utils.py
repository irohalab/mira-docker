import json
from os.path import exists, expanduser, join

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


config_path = '../.config.json'
config_dict = {}


def save_config():
    write_json(config_path, config_dict)


def ask_target_folder():
    home = expanduser('~')
    mira = join(home, 'mira')
    config_dict['target_folder'] = input('Enter the base folder for docker-compose files, '
                                         'web assets and other configs, (press ENTER to use default: {0}) '.format(mira))
    if not config_dict['target_folder']:
        config_dict['target_folder'] = mira


if exists(config_path):
    with open(config_path, 'r') as config_fd:
        config_dict = json.load(config_fd)
    print(fg(10) + 'Found config file' + attr('reset'))

    use_saved_target_folder = None
    target_folder = config_dict.get('target_folder')
    if target_folder is not None:
        while use_saved_target_folder != 'y' and use_saved_target_folder != 'n':
            use_saved_target_folder = prompt('Do you want to use last used target folder path: {0}'.format(target_folder))
    if use_saved_target_folder == 'n':
        ask_target_folder()
        save_config()
else:
    ask_target_folder()
    save_config()
