#!/bin/bash

printf "\n\x1b[32m---- Generate sphinx html ----\x1b[0m\n\n"

cd docs
make html
cd ..

printf "\n\x1b[32m---- Generate README.rst ----\x1b[0m\n\n"

> README.rst
echo ".. image:: ../assets/logodeeplogs.png
   :height: 200
   :align: center
   :alt: DeepLogs Logo
" >> README.rst
cat ./docs/deeplogs.rst >> README.rst
echo "" >> README.rst
cat ./docs/user_guide/installation.rst >> README.rst
echo "" >> README.rst
cat ./docs/user_guide/usage.rst >> README.rst
echo "" >> README.rst
cat ./docs/user_guide/examples.rst >> README.rst

sed -i "s/\.\.\//.\//g" README.rst