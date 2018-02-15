#!/bin/bash -ex
function runtests() {
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
    cd ..
}

rm -rf .testenv
virtualenv .testenv
source .testenv/bin/activate
runtests
rm -rf .testenv

# Python 3
rm -rf .testpy3
virtualenv -p python3.5 .testpy3 2>/dev/null || virtualenv -p python3.6 .testpy3
source .testpy3/bin/activate
runtests
rm -rf .testpy3
