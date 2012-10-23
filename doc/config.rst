.. _config:

Configure IdPproxy
==================

There are two basic configuration files. One that configures
the IdPproxy as a SAML2 IdP. An example of that configuration can be found in
*idp.conf*. How you write this configuration can be found in the
**pysaml2** documentation.

The other configuration file then deals with the IdPproxy as a proxy.
It contains all the necessary directives on how to talk to the
social services you want the proxy to work against.

Configuration directives
::::::::::::::::::::::::

.. contents::
    :local:
    :backlinks: entry

General directives
------------------

CACHE
^^^^^

Information about active sessions are stored in a cache.
This can be either in memory or on a file.

Examples::

    CACHE = "memory"

or::

    CACHE = "file:session.cache"


DEBUG
^^^^^

Whether a more extensive logging should happen.

EPTID_DB
^^^^^^^^

Where the database of constructed and distributed ePTIDs should be stored.

SECRET
^^^^^^

Used when constructing the ePTIDs

SIGN
^^^^

Whether the IdP should sign its responses

STATIC_DIR
^^^^^^^^^^

Where static files are kept


