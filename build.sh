#!/bin/bash -ex
rm -rf .testenv
virtualenv .testenv
source .testenv/bin/activate
rm -rf dist
python setup.py sdist
pip install ./dist/ansible-modules-hashivault-*.tar.gz
cd functional
./run.sh
rm -rf .testenv
