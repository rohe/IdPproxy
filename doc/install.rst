.. _install:

Quick install guide
===================

Before you can use IdPproxy, you'll need to get it installed. This guide
will guide you to a simple, minimal installation.

Install IdPproxy
----------------

For all this to work you need to have Python installed.
The development has been done using 2.6.
There is no 3.X version yet.

Prerequisites
^^^^^^^^^^^^^

You will need these:

* pysaml2 (https://github.com/rohe/pysaml2)
* pyoidc (https://github.com/rohe/pyoidc)
* pyjwkest (https://github.com/rohe/pyjwkest)

and possibly

* python-oauth (http://github.com/simplegeo/python-oauth2)

This you can get from PyPy

* python-mako (>= 0.3.4)

Quick build instructions
^^^^^^^^^^^^^^^^^^^^^^^^

Once you have installed all the necessary prerequisites a simple::

    python setup.py install

will install the basic code.

