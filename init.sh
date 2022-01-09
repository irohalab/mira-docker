#!/bin/bash

set -e
BASEDIR=$(dirname $0)
python3 -m venv ${BASEDIR}/venv

source ${BASEDIR}/venv/bin/activate

python3 -m pip install -r requirements.txt

python3 ./init_helper.py