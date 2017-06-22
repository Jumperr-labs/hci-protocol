#!/usr/bin/env bash
set -e

pushd `dirname ${BASH_SOURCE[0]}`/..

version=`\grep version hci_protocol/__init__.py | \egrep -o '[0-9]+\.[0-9]+\.[0-9]+'`
echo "Found version: ${version}"

if [ `git tag | grep ${version}` ] ; then
    echo "version already exists"
    exit 1
fi;

git tag ${version}
git push --tags

python setup.py register -r pypi
python setup.py sdist upload -r pypi
