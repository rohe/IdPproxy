#!/bin/sh
rm -f IdPproxy*
sphinx-apidoc -F -o ../doc/ ../src/IdPproxy
make clean
make html