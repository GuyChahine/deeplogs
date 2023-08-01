#!/bin/bash

printf "\n\x1b[32m---- Generate sphinx html ----\x1b[0m\n\n"

cd docs
make html
cd ..

printf "\n\x1b[32m---- Generate README.rst ----\x1b[0m\n\n"

> README.rst
echo ".. image:: ../assets/logodeeplogs.png
   :width: 100%
   :align: center
   :alt: DeepLogs Logo
" >> README.rst
echo ".. image:: https://img.shields.io/pypi/v/deeplogs
   :alt: PyPI
   :target: https://pypi.org/project/deeplogs/
" >> README.rst
echo ".. image:: https://img.shields.io/pypi/status/deeplogs
   :alt: PyPI - Status
   :target: https://pypi.org/project/deeplogs/
" >> README.rst
echo ".. image:: https://img.shields.io/pypi/pyversions/deeplogs
   :alt: PyPI - Python Version
   :target: https://pypi.org/project/deeplogs/
" >> README.rst
echo "" >> README.rst
cat ./docs/deeplogs.rst >> README.rst
echo "" >> README.rst
cat ./docs/user_guide/installation.rst >> README.rst
echo "" >> README.rst
echo "Documentation
*************

Documentation is available online at https://guychahine.github.io/deeplogs/.
" >> README.rst

sed -i "s/\.\.\//.\//g" README.rst