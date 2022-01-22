import subprocess
from os import mkdir
from os.path import exists, join
from shutil import rmtree

from colored import attr, fg

from lib.utils import prompt


def build_picfit():
    build_image = None
    while build_image != 'y' and build_image != 'n':
        build_image = prompt('Do you want to build a new picfit image, '
                             'if you have previously built a image. you can choose no, y for yes, n for no: ')
    if build_image == 'y':
        print(fg(33) + 'build a new picfit image' + attr('reset'))
        return subprocess.call('docker build -t mira/picfit https://github.com/thoas/picfit.git',
                               cwd='./picfit', shell=True)
    else:
        print(fg(33) + 'use existing image' + attr('reset'))
        return 0
