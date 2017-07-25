#
# Make sure you have a ~/.pypirc file first
#
VERSION=$(grep version setup.py | sed -e "s/.*='//" -e "s/',//")
git tag -a $VERSION -m v$VERSION
git push origin --tags
#python setup.py register -r pypi
python setup.py sdist upload -r pypi
