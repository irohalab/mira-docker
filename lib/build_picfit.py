import subprocess
from os import mkdir
from os.path import exists, join
from shutil import rmtree

from colored import attr, fg


def build_picfit():
    tmp_folder = './picfit/build'
    if exists(tmp_folder):
        print(fg(111) + 'clean tmp folder' + attr('reset'))
        rmtree(tmp_folder)
    mkdir(tmp_folder)

    return_code = subprocess.call('git clone https://github.com/thoas/picfit.git picfit', cwd=tmp_folder, shell=True)
    if return_code != 0:
        raise Exception('failed to clone picfit repo')

    return_code = subprocess.call('docker build -t picfit-local .', cwd=join(tmp_folder, 'picfit'), shell=True)
    if return_code != 0:
        raise Exception('failed to build picfit')
