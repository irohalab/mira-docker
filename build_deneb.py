import subprocess
from os import mkdir
from os.path import join, expanduser, exists, abspath
from shutil import copytree, rmtree

from colored import fg, attr
from lib.utils import config_path, config_dict, prompt, write_json

home = expanduser('~')
mira = join(home, 'mira')

tmp_folder = './web/build'

if exists(tmp_folder):
    print(fg(111) + 'clean tmp folder' + attr('reset'))
    rmtree(tmp_folder, ignore_errors=True)
mkdir(tmp_folder)

target_folder = config_dict.get('target_folder')
if not target_folder:
    target_folder = mira
    config_dict['target_folder'] = target_folder
    print(fg(10) + 'target_folder not found, target_folder set to ' + target_folder + attr('reset'))

web_folder = config_dict.get('web_folder')
if not web_folder:
    web_folder = join(target_folder, 'web')
    print(fg(10) + 'web_folder not found, web_folder set to ' + web_folder + attr('reset'))


def ask_env():
    chrome_extension_id = prompt('Enter CHROME_EXTENSION_ID')
    firefox_extension_id = prompt('Enter FIREFOX_EXTENSION_ID')
    firefox_extension_url = prompt('Enter FIREFOX_EXTENSION_URL')
    ga = prompt('Enter GA')
    site_title = prompt('Enter SITE_TITLE')

    config_dict['web']['chrome_extension_id'] = chrome_extension_id
    config_dict['web']['firefox_extension_id'] = firefox_extension_id
    config_dict['web']['firefox_extension_url'] = firefox_extension_url
    config_dict['web']['ga'] = ga
    config_dict['web']['site_title'] = site_title

    write_json(config_path, config_dict)


if config_dict.get('web') is None:
    config_dict['web'] = {}
    ask_env()
else:
    print('There is a previous saved config:')
    for key in config_dict['web']:
        print(fg(116) + key + '=' + config_dict['web'][key] + attr('reset'))
    use_saved = prompt('Do you want to use these configuration? y for yes, n for no: ')
    if use_saved == 'n':
        ask_env()

use_tag = None
while use_tag != 'y' and use_tag != 'n':
    use_tag = prompt('Do you want to use tag for building? y for yes, n for no')

tag_to_checkout = None
if use_tag == 'y':
    tag_to_checkout = prompt('You choose use tag, please specify the tag you want to use (e.g. v4.2.0): ')
else:
    print(fg(154) + 'You choose not use tag, will checkout master branch' + attr('reset'))

cmd_base = 'docker run --rm -v {0}:/build'.format(abspath(tmp_folder))
if config_dict.get('web') is not None:
    env_list = []
    for key in config_dict.get('web'):
        env_list.append('--env {0}={1}'.format(key, config_dict['web'][key]))
    cmd_base = cmd_base + ' ' + ' '.join(env_list)
cmd = cmd_base + ' node:16 bash -c \'cd /build && git clone https://github.com/irohalab/Deneb.git Deneb && cd Deneb && '
if tag_to_checkout is not None:
    cmd = cmd + 'git checkout tags/{0} -b {0}-branch && '.format(tag_to_checkout)
cmd = cmd + 'yarn install && npm run build:aot:prod\''
return_code = subprocess.call(cmd, shell=True, cwd=target_folder)

if return_code != 0:
    print(fg(9) + 'build failed!' + attr('reset'))
    exit(-1)

copytree(tmp_folder, web_folder)

print('All done! built files is copied to ' + web_folder)
