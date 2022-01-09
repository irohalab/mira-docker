import json
from os import mkdir
from os.path import join, exists, expanduser
from secrets import token_hex
from shutil import copyfile

from ruamel.yaml import YAML
import configparser

home = expanduser('~')
mira = join(home, 'mira')

default_download_manager_conf_dir = join(mira, 'download-manager')
tip_dm_config = 'location for download-manager config files: (current: {0})'.format(default_download_manager_conf_dir)
download_manager_conf_dir = input(tip_dm_config)
if not download_manager_conf_dir:
    download_manager_conf_dir = default_download_manager_conf_dir

default_video_manager_conf_dir = join(mira, 'video-manager')
tip_vm_config = 'location for video-manager config files: (current: {0})'.format(default_video_manager_conf_dir)
video_manager_conf_dir = input(tip_vm_config)
if not video_manager_conf_dir:
    video_manager_conf_dir = default_video_manager_conf_dir

default_albireo_conf_dir = join(mira, 'albireo')
tip_albireo_config = 'location for albireo config files: (current: {0})'.format(default_albireo_conf_dir)
albireo_conf_dir = input(tip_albireo_config)
if not albireo_conf_dir:
    albireo_conf_dir = default_albireo_conf_dir

default_nginx_conf_dir = join(mira, 'nginx')
tip_nginx_config = 'location for nginx config files: (current: {0})'.format(default_nginx_conf_dir)
nginx_conf_dir = input(tip_nginx_config)
if not nginx_conf_dir:
    nginx_conf_dir = default_nginx_conf_dir

default_qb_conf_dir = join(mira, 'qb')
tip_qb_config = 'location for qBittorrent config files: (current: {0})'.format(default_qb_conf_dir)
qb_conf_dir = input(tip_qb_config)
if not qb_conf_dir:
    qb_conf_dir = default_qb_conf_dir

print('Use amqp url or amqp config object:')
print('1. amqp url')
print('2. amqp object')
amqp_selector = None
while amqp_selector != '1' and amqp_selector != '2':
    amqp_selector = input('Please Enter 1 or 2: ')

if amqp_selector == '1':
    amqp_url = input('You select use amqp url. Please enter amqp url: ')
else:
    amqp_host = input('You select use amqp config object, Please enter amqp host: ')
    amqp_port = input('amqp server port: ')
    amqp_user = input('amqp user: ')
    amqp_password = input('amqp password: ')

print('enter login credentials to connect qbittorrent daemon')
qb_user = input('qbittorrent username: (press enter to use admin')
if not qb_user:
    qb_user = 'admin'

qb_password = input('qbittorent password:(press enter to generate a random one)')
if not qb_password:
    qb_password = token_hex(nbytes=16)

download_location = input('data path for albireo, default is /data/albireo')
if not download_location:
    download_location = '/data/albireo'

use_postgres_docker = None
while use_postgres_docker != 'y' and use_postgres_docker != 'n':
    use_postgres_docker = input('Do you want to use the postgres service in the docker-compos file? y for yes, n for no: ')

postgres_user = input('username for postgres: (press ENTER to use postgres)')
if not postgres_user:
    postgres_user = 'postgres'

postgres_password = input('password for postgres: (press ENTER to use randomly generated password)')
if not postgres_password:
    postgres_password = token_hex(nbytes=16)

location_for_postgres_data = input('location for postgres data: (press ENTER to use /var/mira/data)')
if not location_for_postgres_data:
    location_for_postgres_data = '/var/mira/data'

dm_enable_https = None
while dm_enable_https != 'y' and dm_enable_https != 'n':
    dm_enable_https = input('Enable https for download manager server? y for yes, n for no: ')

vm_enable_https = None
while vm_enable_https != 'y' and vm_enable_https != 'n':
    vm_enable_https = input('Enable https for video manager server? y for yes, n for no: ')

print('All info collected. Start to generate docker-compose and configuration files...')

print('Creating folders for configuration files...')
if not exists(mira):
    mkdir(mira)

if not exists(download_manager_conf_dir):
    mkdir(download_manager_conf_dir)

if not exists(video_manager_conf_dir):
    mkdir(video_manager_conf_dir)

if not exists(albireo_conf_dir):
    mkdir(albireo_conf_dir)

if not exists(nginx_conf_dir):
    mkdir(nginx_conf_dir)

if not exists(qb_conf_dir):
    mkdir(qb_conf_dir)

print('Copying configuration files and docker-compose files...')

download_manager_conf = join(download_manager_conf_dir, 'config.yml')
download_manager_ormconf = join(download_manager_conf_dir, 'ormconfig.json')

copyfile('./download-manager/config.yml', download_manager_conf)
copyfile('./download-manager/ormconfig.json', download_manager_ormconf)

video_manager_conf = join(video_manager_conf_dir, 'config.yml')
video_manager_ormconf = join(video_manager_conf_dir, 'ormconfig.json')
copyfile('./video-manager/config.yml', video_manager_conf)
copyfile('./video-manager/ormconfig.json', video_manager_ormconf)

nginx_conf = join(nginx_conf_dir, 'nginx.conf')
copyfile('./nginx/nginx.conf', nginx_conf)

albireo_conf = join(albireo_conf_dir, 'config.yml')
albireo_sentry = join(albireo_conf_dir, 'sentry.yml')
albireo_alembic_ini = join(albireo_conf_dir, 'alembic.ini')
copyfile('./albireo/config.yml', albireo_conf)
copyfile('./albireo/sentry.yml', albireo_sentry)
copyfile('./albireo/alembic.ini', albireo_alembic_ini)

copyfile('./docker-compose.yml', join(mira, 'docker-compose.yml'))
copyfile('./docker-compose.override.yml', join(mira, 'docker-compose.override.yml'))


def update_amqp(conf_dict):
    if amqp_selector == '1':
        conf_dict['amqpUrl'] = amqp_url
    else:
        conf_dict['amqp']['host'] = amqp_host
        conf_dict['amqp']['port'] = amqp_port
        conf_dict['amqp']['user'] = amqp_user
        conf_dict['amqp']['password'] = amqp_password


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


def enable_https_on_url(url_str):
    return url_str.replace('http://', 'https://')


print('Updating configurations...')

# Update download-manager/config.yml

dm_conf_dict = load_yaml(download_manager_conf)
update_amqp(dm_conf_dict)

dm_conf_dict['qBittorrent']['username'] = qb_user
dm_conf_dict['qBittorrent']['password'] = qb_password

if dm_enable_https == 'y':
    dm_conf_dict['webserver']['enableHttps'] = True
write_yaml(download_manager_conf, dm_conf_dict)

# Update download-manager/ormconfig.json

dm_ormconf_dict = load_json(download_manager_ormconf)
dm_ormconf_dict['username'] = postgres_user
dm_ormconf_dict['password'] = postgres_password
write_json(download_manager_ormconf, dm_ormconf_dict)

# Update video-manager/config.yml

vm_conf_dict = load_yaml(video_manager_conf)
update_amqp(vm_conf_dict)
if dm_enable_https == 'y':
    vm_conf_dict['WebServer']['enableHttps'] = True
    vm_conf_dict['ApiWebServer']['enableHttps'] = True
write_yaml(video_manager_conf, vm_conf_dict)

# update video-manager/ormconfig.json
vm_ormconf_dict = load_json(video_manager_ormconf)
vm_ormconf_dict['username'] = postgres_user
vm_ormconf_dict['password'] = postgres_password
write_json(video_manager_ormconf, vm_ormconf_dict)

# update albireo config

albireo_conf_dict = load_yaml(albireo_conf)
albireo_conf_dict['database']['username'] = postgres_user
albireo_conf_dict['database']['password'] = postgres_password
if dm_enable_https == 'y':
    albireo_conf_dict['download_manager_url'] = enable_https_on_url(albireo_conf_dict['download_manager_url'])

if vm_enable_https == 'y':
    albireo_conf_dict['video_manager_url'] = enable_https_on_url(albireo_conf_dict['video_manager_url'])

write_yaml(albireo_conf, albireo_conf_dict)

# update albireo ormconf.json
alembic_conf_dict = configparser.ConfigParser()
alembic_conf_dict.read(albireo_alembic_ini)
alembic_conf_dict['alembic']['sqlalchemy.url'] = 'postgres://{0}:{1}@postgres/albireo'.format(postgres_user, postgres_password)

with open(albireo_alembic_ini, 'w') as alembic_conf_fd:
    alembic_conf_dict.write(alembic_conf_fd)

print('Generating environment variables file: {0}/env'.format(mira))

env_list = [
    'DM_CONFIG_DIR=' + download_manager_conf_dir,
    'VM_CONFIG_DIR=' + video_manager_conf_dir,
    'ALBIREO_CONFIG_DIR=' + albireo_conf_dir,
    'NGINX_CONFIG=' + nginx_conf_dir,
    'QBT_CONFIG_LOCATION=' + qb_conf_dir,
    'QBT_DOWNLOADS_LOCATION=' + join(download_location, 'downloads'),
    'DOWNLOAD_DATA=' + download_location
]

if use_postgres_docker == 'y':
    env_list.append('POSTGRES_USER=' + postgres_user)
    env_list.append('POSTGRES_PASSWORD=' + postgres_user)
    env_list.append('POSTGRES_DATA=' + location_for_postgres_data)


with open(join(mira, 'env'), 'w') as env_fd:
    env_fd.write('\n'.join(env_list))

print('All done! Don\'t forget to update the host in site section of albireo config file and nginx server_name')
