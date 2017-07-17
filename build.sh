#!/bin/bash -ex
rm -rf .testenv
virtualenv .testenv
source .testenv/bin/activate
rm -rf dist
python setup.py sdist

if [ "$(uname)" == "Dawrin" ]; then
  #brew install gmp
  env "CFLAGS=-I/usr/local/include -L/usr/local/lib" pip install ./dist/ansible-modules-hashivault-*.tar.gz
else
  pip install ./dist/ansible-modules-hashivault-*.tar.gz
fi

cd functional
./run.sh
rm -rf .testenv
