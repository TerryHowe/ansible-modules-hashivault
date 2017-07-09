#!/bin/bash -ex
rm -rf .venv
virtualenv .venv
source .venv/bin/activate
rm -rf dist
python setup.py sdist
pip install ./dist/ansible-modules-hashivault-*.tar.gz
cd functional
./run.sh
