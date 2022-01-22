import os
import subprocess
from os import mkdir
from os.path import join, exists, expanduser
from secrets import token_hex
from shutil import copyfile
from time import sleep

from colored import fg, attr
import configparser

from lib.build_picfit import build_picfit
from lib.init_qb import update_qb
from lib.utils import prompt, load_yaml, load_json, write_yaml, write_json, config_path, config_dict


target_folder = config_dict.get('target_folder')

dm_docker_tag = prompt('version tag of download manager image: ')
vm_docker_tag = prompt('version tag of video manager image: ')
albireo_docker_tag = prompt('version tag of albireo image: ')

download_manager_conf_dir = join(target_folder, 'download-manager')
video_manager_conf_dir = join(target_folder, 'video-manager')
albireo_conf_dir = join(target_folder, 'albireo')
nginx_conf_dir = join(target_folder, 'nginx')
web_folder = join(target_folder, 'web')
qb_conf_dir = join(target_folder, 'qb')
picfit_conf_dir = join(target_folder, 'picfit')

print('Use amqp url or amqp config object:')
print('1. amqp url')
print('2. amqp object')
amqp_selector = None
while amqp_selector != '1' and amqp_selector != '2':
    amqp_selector = prompt('Please Enter 1 or 2: ')

if amqp_selector == '1':
    amqp_url = prompt('You select use amqp url. Please enter amqp url: ')
else:
    amqp_host = prompt('You select use amqp config object, Please enter amqp host: ')
    amqp_port = prompt('amqp server port: ')
    amqp_user = prompt('amqp user: ')
    amqp_password = prompt('amqp password: ')

print('enter login credentials to connect qbittorrent daemon')
qb_user = prompt('qbittorrent username (press enter to use admin): ')
if not qb_user:
    qb_user = 'admin'

qb_password = prompt('qbittorent password (press enter to generate a random one): ')
if not qb_password:
    qb_password = token_hex(nbytes=16)

download_location = prompt('data path for albireo, press enter to use /data/albireo: ')
if not download_location:
    download_location = '/data/albireo'

use_postgres_docker = None
while use_postgres_docker != 'y' and use_postgres_docker != 'n':
    use_postgres_docker = prompt('Do you want to use the postgres service in the docker-compos file? y for yes, n for no: ')

postgres_host = 'postgres'
postgres_port = 5432
if use_postgres_docker == 'n':
    postgres_host = prompt('Please enter your postgres server host: ')
    postgres_port = int(prompt('Please enter your postgres server port: '))

postgres_user = prompt('username for postgres (press ENTER to use postgres): ')
if not postgres_user:
    postgres_user = 'postgres'

postgres_password = prompt('password for postgres (press ENTER to use randomly generated password): ')
if not postgres_password:
    postgres_password = token_hex(nbytes=16)

db_name_albireo = prompt('database name for albireo (default is albireo): ')
db_name_vm = prompt('database name for video manager (default is mira_video): ')
db_name_dm = prompt('database name for download manager (default is mira_download): ')
if not db_name_albireo:
    db_name_albireo = 'albireo'
if not db_name_vm:
    db_name_vm = 'mira_video'
if not db_name_dm:
    db_name_dm = 'mira_download'

location_for_postgres_data = prompt('location for postgres data (press ENTER to use /data/postgres): ')
if not location_for_postgres_data:
    location_for_postgres_data = '/data/postgres'

dm_enable_https = None
while dm_enable_https != 'y' and dm_enable_https != 'n':
    dm_enable_https = prompt('Enable https for download manager server? y for yes, n for no: ')

vm_enable_https = None
while vm_enable_https != 'y' and vm_enable_https != 'n':
    vm_enable_https = prompt('Enable https for video manager server? y for yes, n for no: ')

default_admin_albireo = prompt('Enter the default admin user for albireo (Enter to use admin): ')
default_admin_password_albireo = prompt('Enter the default admin user password for albireo (Enter to use generated password): ')
if not default_admin_albireo:
    default_admin_albireo = 'admin'
    default_admin_password_albireo = token_hex(nbytes=16)

docker_network = prompt('docker network for docker-compose services, (default will be mira): ')
if not docker_network:
    docker_network = 'mira'

init_albireo_db = None
while init_albireo_db != 'y' and init_albireo_db != 'n':
    init_albireo_db = prompt('Do you want to initialize albireo database, '
                            'in case you are migrating from the old Albireo, '
                            'select no (y for yes, n for n): ')

print(fg('chartreuse_2a') + 'All info collected. Start to generate docker-compose and configuration files...' + attr('reset'))

print(fg(33) + 'Creating folders for configuration files...' + attr('reset'))
if not exists(target_folder):
    mkdir(target_folder)

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

if not exists(picfit_conf_dir):
    mkdir(picfit_conf_dir)

if not exists(location_for_postgres_data):
    os.makedirs(location_for_postgres_data)

print(fg(33) + 'Copying configuration files and docker-compose files...' + attr('reset'))

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

picfit_conf = join(picfit_conf_dir, 'config.json')
copyfile('./picfit/config.json', picfit_conf)

albireo_conf = join(albireo_conf_dir, 'config.yml')
albireo_sentry = join(albireo_conf_dir, 'sentry.yml')
albireo_alembic_ini = join(albireo_conf_dir, 'alembic.ini')
copyfile('./albireo/config.yml', albireo_conf)
copyfile('./albireo/sentry.yml', albireo_sentry)
copyfile('./albireo/alembic.ini', albireo_alembic_ini)

copyfile('./docker-compose.yml', join(target_folder, 'docker-compose.yml'))
copyfile('./docker-compose.override.yml', join(target_folder, 'docker-compose.override.yml'))


def update_amqp(conf_dict):
    if amqp_selector == '1':
        conf_dict['amqpUrl'] = amqp_url
    else:
        conf_dict['amqp']['host'] = amqp_host
        conf_dict['amqp']['port'] = amqp_port
        conf_dict['amqp']['user'] = amqp_user
        conf_dict['amqp']['password'] = amqp_password


def enable_https_on_url(url_str):
    return url_str.replace('http://', 'https://')


print(fg(33) + 'Updating configurations...' + attr('reset'))

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
alembic_conf_dict['alembic']['sqlalchemy.url'] = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
    postgres_user, postgres_password, postgres_host, postgres_port, albireo_conf_dict['database']['database']
)

with open(albireo_alembic_ini, 'w') as alembic_conf_fd:
    alembic_conf_dict.write(alembic_conf_fd)

picfit_conf_dict = load_json(picfit_conf)
picfit_conf_dict['storage']['src']['location'] = download_location
picfit_conf_dict['storage']['dst']['location'] = join(download_location, 'thumbnails')

print(fg(33) + 'Generating environment variables file: {0}/env'.format(target_folder) + attr('reset'))

env_list = [
    'DM_CONFIG_DIR=' + download_manager_conf_dir,
    'VM_CONFIG_DIR=' + video_manager_conf_dir,
    'ALBIREO_CONFIG_DIR=' + albireo_conf_dir,
    'NGINX_CONFIG=' + nginx_conf,
    'NGINX_DENEB=' + web_folder,
    'QBT_CONFIG_LOCATION=' + qb_conf_dir,
    'QBT_DOWNLOADS_LOCATION=' + join(download_location, 'downloads'),
    'DOWNLOAD_DATA=' + download_location,
    'DOWNLOAD_MANAGER_TAG=' + dm_docker_tag,
    'VIDEO_MANAGER_TAG=' + vm_docker_tag,
    'ALBIREO_TAG=' + albireo_docker_tag,
    'PICFIT_CONFIG=' + picfit_conf
]

if use_postgres_docker == 'y':
    env_list.append('POSTGRES_USER=' + postgres_user)
    env_list.append('POSTGRES_PASSWORD=' + postgres_password)
    env_list.append('POSTGRES_DATA=' + location_for_postgres_data)

with open(join(target_folder, '.env'), 'w') as env_fd:
    env_fd.write('\n'.join(env_list))

print(fg(33) + '======================================================================================' + attr('reset'))
print(' ')
print(fg(33) + 'init database, you admin account is ' + fg(11) + attr('bold') + default_admin_albireo + attr('reset')
      + fg(33) + ' password is ' + attr('bold') + fg(11) + default_admin_password_albireo + attr('reset'))
print(' ')
print(fg(33) + '======================================================================================' + attr('reset'))

if docker_network != 'mira':
    docker_compose_dict = load_yaml(join(target_folder, 'docker-compose.yml'))
    docker_compose_dict['networks']['mira']['name'] = docker_network
    write_yaml(join(target_folder, 'docker-compose.yml'), docker_compose_dict)

    docker_compose_override_dict = load_yaml(join(target_folder, 'docker-compose.override.yml'))
    docker_compose_override_dict['networks']['mira']['name'] = docker_network
    write_yaml(join(target_folder, 'docker-compose.override.yml'), docker_compose_dict)

init_docker_compose = load_yaml('./docker-compose.init.yml')
if init_albireo_db == 'n':
    del init_docker_compose['services']['albireo-init']
else:
    init_docker_compose['services']['albireo-init']['command'] = 'bash -c "/usr/bin/python /usr/app/tools.py --db-init'\
                                                     ' && /usr/bin/python /usr/app/tools.py --user-add {0} {1}'\
                                                     ' && /usr/bin/python /usr/app/tools.py --user-promote {0} 3"'.\
                                                     format(default_admin_albireo, default_admin_password_albireo)

init_docker_compose['services']['video-manager-init']['command'] = '/app/node_modules/.bin/typeorm schema:sync' \
                                                       ' -f /etc/mira/ormconfig.json'

init_docker_compose['services']['download-manager-init']['command'] = '/app/node_modules/.bin/typeorm schema:sync' \
                                                          ' -f /etc/mira/ormconfig.json'
if docker_network != 'mira':
    init_docker_compose['networks']['mira']['name'] = docker_network

write_yaml(join(target_folder, 'docker-compose.init.yml'), init_docker_compose)

print(fg(33) + 'create docker network: ' + docker_network + attr('reset'))

return_code = subprocess.call('docker network create -d bridge {0}'.format(docker_network), shell=True)
if return_code != 0:
    print(fg(203) + 'failed to create network' + attr('reset'))
    exit(-1)

if use_postgres_docker:
    subprocess.call('docker-compose -f {0} --profile db --profile qbt up -d'.format(join(target_folder, 'docker-compose.yml')), cwd=target_folder,
                    shell=True)

print(fg(159) + 'waiting for postgres ready...' + attr('reset'))
while True:
    sleep(5)
    return_code = subprocess.call(
        'docker run --rm --network {0} --env-file .env postgres:12.8 pg_isready -h {1} -p {2}'.format(
            docker_network, postgres_host, postgres_port),
        cwd=target_folder,
        shell=True)
    if return_code == 0:
        break


print(fg(33) + 'create databases...' + attr('reset'))

psql_statement = 'psql -d postgres://{0}:{1}@{2}:{3}/postgres -c \'CREATE DATABASE "{4}" ENCODING UTF8;\' '\
                 '-c \'CREATE DATABASE "{5}" ENCODING UTF8;\''.format(postgres_user,
                                                                      postgres_password,
                                                                      postgres_host,
                                                                      postgres_port,
                                                                      db_name_vm,
                                                                      db_name_dm)
if init_albireo_db == 'y':
    psql_statement = psql_statement + ' -c \'CREATE DATABASE "{0}" ENCODING UTF8;\''.format(db_name_albireo)

return_code = subprocess.call('docker run --rm --network {0} --env-file .env postgres:12.8 {1}'.format(
                                docker_network, psql_statement), cwd=target_folder, shell=True)

if return_code != 0:
    print(fg(203) + 'failed to create databases' + attr('reset'))
    exit(-1)

print(fg(33) + 'Apply qBittorrent username and password...' + attr('reset'))
update_qb(qb_user, qb_password)

subprocess.call('docker-compose -f {0} --profile init up'.format(join(target_folder, 'docker-compose.init.yml')),
                cwd=target_folder,
                shell=True)


subprocess.call('docker-compose -f {0} --profile db down'.format(join(target_folder, 'docker-compose.yml')), cwd=target_folder,
                shell=True)

subprocess.call('docker-compose -f {0} --profile init down'.format(join(target_folder, 'docker-compose.init.yml')),
                cwd=target_folder,
                shell=True)

print(fg(33) + 'build picfit locally...' + attr('reset'))
build_picfit()

print(fg('chartreuse_2a') +
      'All done! Don\'t forget to update the host in site section of albireo config file and nginx server_name' +
      attr('reset'))
