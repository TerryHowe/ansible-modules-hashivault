#!/usr/bin/env bash
#
# Make sure you have a ~/.pypirc file first
#
CHANGES=$(git diff-index --name-only HEAD --)
if [ -n "${CHANGES}" ]
then
    echo "Changes have not been committed"
    exit 1
fi
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "${BRANCH}" != "main" ]
then
    echo "You must be on main"
    exit 1
fi
git pull
pip install gitchangelog
pip install twine
pip install build
OLDVERSION=$(grep '^version' pyproject.toml | sed -e 's/.*= "//' -e 's/"//')
vi pyproject.toml
VERSION=$(grep '^version' pyproject.toml | sed -e 's/.*= "//' -e 's/"//')
if [ "$OLDVERSION" == "$VERSION" ]
then
    echo "Old version $OLDVERSION same as $VERSION"
    read ANS
fi
git tag -a $VERSION -m v$VERSION
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=log.showsignature GIT_CONFIG_VALUE_0=false gitchangelog
vi CHANGELOG.rst
echo "Ready to push $VERSION (cntrl-c to quit)?"
read ANS
git commit -m "Version $VERSION" CHANGELOG.rst pyproject.toml
git push origin main
git tag --force  -a $VERSION -m v$VERSION
git push origin --tags
#python setup.py register -r pypi

# old school
# python setup.py sdist upload -r pypi

# twine
rm -rf dist
python3.9 -m build --sdist
twine upload dist/*
