import io
import json
import os
import subprocess
from os import mkdir
from os.path import join, exists, expanduser
from secrets import token_hex
from shutil import copyfile
from time import sleep

from ruamel.yaml import YAML
import configparser

home = expanduser('~')
mira = join(home, 'mira')

dm_docker_tag = input('version tag of download manager image: ')
vm_docker_tag = input('version tag of video manager image: ')
albireo_docker_tag = input('version tag of albireo image: ')

default_download_manager_conf_dir = join(mira, 'download-manager')
tip_dm_config = 'location for download-manager config files (current: {0}): '.format(default_download_manager_conf_dir)
download_manager_conf_dir = input(tip_dm_config)
if not download_manager_conf_dir:
    download_manager_conf_dir = default_download_manager_conf_dir

default_video_manager_conf_dir = join(mira, 'video-manager')
tip_vm_config = 'location for video-manager config files (current: {0}): '.format(default_video_manager_conf_dir)
video_manager_conf_dir = input(tip_vm_config)
if not video_manager_conf_dir:
    video_manager_conf_dir = default_video_manager_conf_dir

default_albireo_conf_dir = join(mira, 'albireo')
tip_albireo_config = 'location for albireo config files (current: {0}): '.format(default_albireo_conf_dir)
albireo_conf_dir = input(tip_albireo_config)
if not albireo_conf_dir:
    albireo_conf_dir = default_albireo_conf_dir

default_nginx_conf_dir = join(mira, 'nginx')
tip_nginx_config = 'location for nginx config files (current: {0}): '.format(default_nginx_conf_dir)
nginx_conf_dir = input(tip_nginx_config)
if not nginx_conf_dir:
    nginx_conf_dir = default_nginx_conf_dir

default_qb_conf_dir = join(mira, 'qb')
tip_qb_config = 'location for qBittorrent config files (current: {0}): '.format(default_qb_conf_dir)
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
qb_user = input('qbittorrent username (press enter to use admin: ')
if not qb_user:
    qb_user = 'admin'

qb_password = input('qbittorent password (press enter to generate a random one): ')
if not qb_password:
    qb_password = token_hex(nbytes=16)

download_location = input('data path for albireo, default is /data/albireo: ')
if not download_location:
    download_location = '/data/albireo'

use_postgres_docker = None
while use_postgres_docker != 'y' and use_postgres_docker != 'n':
    use_postgres_docker = input('Do you want to use the postgres service in the docker-compos file? y for yes, n for no: ')

postgres_host = 'postgres'
postgres_port = 5432
if use_postgres_docker == 'n':
    postgres_host = input('Please enter your postgres server host: ')
    postgres_port = int(input('Please enter your postgres server port: '))

postgres_user = input('username for postgres (press ENTER to use postgres): ')
if not postgres_user:
    postgres_user = 'postgres'

postgres_password = input('password for postgres (press ENTER to use randomly generated password): ')
if not postgres_password:
    postgres_password = token_hex(nbytes=16)

db_name_albireo = input('database name for albireo (default is albireo): ')
db_name_vm = input('database name for video manager (default is mira-video): ')
db_name_dm = input('database name for download manager (default is mira-download): ')

location_for_postgres_data = input('location for postgres data (press ENTER to use /var/mira/data): ')
if not location_for_postgres_data:
    location_for_postgres_data = '/var/mira/data'

dm_enable_https = None
while dm_enable_https != 'y' and dm_enable_https != 'n':
    dm_enable_https = input('Enable https for download manager server? y for yes, n for no: ')

vm_enable_https = None
while vm_enable_https != 'y' and vm_enable_https != 'n':
    vm_enable_https = input('Enable https for video manager server? y for yes, n for no: ')

default_admin_albireo = input('Enter the default admin user for albireo (Enter to use admin): ')
default_admin_password_albireo = input('Enter the default admin user password for albireo (Enter to use generated password): ')
if not default_admin_albireo:
    default_admin_albireo = 'admin'
    default_admin_password_albireo = token_hex(nbytes=16)

docker_network = input('docker network for docker-compose services, (default will be mira): ')
if not docker_network:
    docker_network = 'mira'

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

if not exists(location_for_postgres_data):
    os.makedirs(location_for_postgres_data)

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
dm_ormconf_dict['host'] = postgres_host
dm_ormconf_dict['port'] = postgres_port
dm_ormconf_dict['username'] = postgres_user
dm_ormconf_dict['password'] = postgres_password
if db_name_dm:
    dm_ormconf_dict['database'] = db_name_dm
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
vm_ormconf_dict['host'] = postgres_host
vm_ormconf_dict['port'] = postgres_port
vm_ormconf_dict['username'] = postgres_user
vm_ormconf_dict['password'] = postgres_password
if db_name_vm:
    vm_ormconf_dict['database'] = db_name_vm
write_json(video_manager_ormconf, vm_ormconf_dict)

# update albireo config

albireo_conf_dict = load_yaml(albireo_conf)
albireo_conf_dict['database']['host'] = postgres_host
albireo_conf_dict['database']['port'] = postgres_port
albireo_conf_dict['database']['username'] = postgres_user
albireo_conf_dict['database']['password'] = postgres_password
if db_name_albireo:
    albireo_conf_dict['database']['database'] = db_name_albireo
if dm_enable_https == 'y':
    albireo_conf_dict['download_manager_url'] = enable_https_on_url(albireo_conf_dict['download_manager_url'])

if vm_enable_https == 'y':
    albireo_conf_dict['video_manager_url'] = enable_https_on_url(albireo_conf_dict['video_manager_url'])

write_yaml(albireo_conf, albireo_conf_dict)

# update albireo ormconf.json
alembic_conf_dict = configparser.ConfigParser()
alembic_conf_dict.read(albireo_alembic_ini)
if use_postgres_docker == 'y':
    postgres_host = 'postgres'
    postgres_port = 5432
alembic_conf_dict['alembic']['sqlalchemy.url'] = 'postgres://{0}:{1}@{2}:{3}/{4}'.format(
    postgres_host, postgres_port, postgres_user, postgres_password, albireo_conf_dict['database']['database']
)

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
    'DOWNLOAD_DATA=' + download_location,
    'DOWNLOAD_MANAGER_TAG=' + dm_docker_tag,
    'VIDEO_MANAGER_TAG=' + vm_docker_tag,
    'ALBIREO_TAG=' + albireo_docker_tag
]

if use_postgres_docker == 'y':
    env_list.append('POSTGRES_USER=' + postgres_user)
    env_list.append('POSTGRES_PASSWORD=' + postgres_password)
    env_list.append('POSTGRES_DATA=' + location_for_postgres_data)


with open(join(mira, '.env'), 'w') as env_fd:
    env_fd.write('\n'.join(env_list))

print('init database, you admin account is {0}, password is {1}'.format(default_admin_albireo, default_admin_password_albireo))

init_docker_compose = load_yaml('./docker-compose.init.yml')
init_docker_compose['services']['albireo-init']['command'] = 'bash -c "/usr/bin/python /usr/app/tools.py --db-init'\
                                                 ' && /usr/bin/python /usr/app/tools.py --user-add {0} {1}'\
                                                 ' && /usr/bin/python /usr/app/tools.py --user-promote {0} 3"'.format(
    default_admin_albireo, default_admin_password_albireo)

init_docker_compose['services']['video-manager-init']['command'] = '/app/node_modules/.bin/typeorm schema:sync' \
                                                       ' -f /etc/mira/ormconfig.json'

init_docker_compose['services']['download-manager-init']['command'] = '/app/node_modules/.bin/typeorm schema:sync' \
                                                          ' -f /etc/mira/ormconfig.json'

write_yaml(join(mira, 'docker-compose.init.yml'), init_docker_compose)

print('create docker network: ' + docker_network)

return_code = subprocess.call('docker network create -d bridge {0}'.format(docker_network), shell=True)
if return_code != 0:
    print('failed to create network')
    exit(-1)

postgres_proc = subprocess.Popen([
    'docker-compose', '-f', join(mira, 'docker-compose.yml'), '--profile', 'db', 'up', '-d'],
                        cwd=mira,
                        shell=True)

print('waiting for postgres ready...')
while True:
    sleep(5)
    return_code = subprocess.call(
        'docker run --rm --network mira --env-file .env postgres:12.8 pg_isready -h postgres -d albireo',
        cwd=mira,
        shell=True)
    if return_code == 0:
        break

subprocess.call('docker-compose -f {0} --profile init up'.format(join(mira, 'docker-compose.init.yml')),
                cwd=mira,
                shell=True)

postgres_proc.terminate()
print('All done! Don\'t forget to update the host in site section of albireo config file and nginx server_name')
