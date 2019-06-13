#!/usr/bin/env bash
export PLUGINS=''
rm -rf ansible-repo
mkdir ansible-repo && cd ansible-repo
git clone https://github.com/ansible/ansible.git && cd ansible &&  git checkout v2.7.6 && cd ..
pip install sphinx sphinx_rtd_theme
pip install -r ansible/requirements.txt
rm -rf ansible/lib/ansible/modules/ && mkdir -p ansible/lib/ansible/modules/hashivault
cp -r ../ansible/modules/hashivault/hashivault*.py ansible/lib/ansible/modules/hashivault/
ls ansible/lib/ansible/modules/hashivault
cd ansible/docs/docsite/

export MODULES=$(ls -m ../../lib/ansible/modules/hashivault/ | grep -v '^_' | tr -d '[:space:]'  | sed 's/.py//g')
make webdocs . || true
touch _build/html/.nojekyll
