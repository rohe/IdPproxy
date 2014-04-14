#!/bin/sh
rm -f idpproxy*
sphinx-apidoc -F -o ../doc/ ../src/idpproxy
make clean
make html