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

Below you will find a list of all the used directives in alphabetic order.
The configuration is written as a python module.

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

Directives specific per service
-------------------------------

All directives concerning services are collected under the general
**SERVICE** directive.

A typical service configuration looks like this::

    "facebook":{
        "saml_endpoint":"facebook_sso",
        "social_endpoint":"facebook",
        "class":FacebookOAuth2,
        "authenticating_authority": 'https://graph.facebook.com/oauth/',
        "token_endpoint": "https://graph.facebook.com/oauth/access_token",
        "authorization_endpoint": 'https://graph.facebook.com/oauth/authorize',
        "userinfo_endpoint": "https://graph.facebook.com/me",
        "scope": ["email"],
        "attribute_map": {
            "givenName": "first_name",
            "surName": "last_name",
            "displayName": "name",
            "uid": "link",
        },
        "name": "Facebook",
    },

The key to the dictionary has to be unique, among all the services
but is not used anywhere in the code. It's still a good practise to use
meaningful names.

The service specific directives are in alphabetic order

attribute_map
^^^^^^^^^^^^^

How the information returned by the social service should be mapped
into something the SAML IdP side could return.
This is a very simple one-to-one mapping or a simpe value construction.
If it's a one-to-one mapping the the key in the dictionary is the
SAML attribute value while the key value is the attribute name that the
social service returns.

Dynamic constructing of value are base on simple stringformats::

    "eduPersonPrincipalName": ("%s@twitter.com", "screen_name")

The resulting email like value has a *local_part* which is the
 screen_name returned by the social service and the *domain_part* is
 statically defined

authenticating_authority
^^^^^^^^^^^^^^^^^^^^^^^^

The string that is return in the AuthenticatingAuthority part of the
AuthnContext in the SAML2 response.

authorization_endpoint
^^^^^^^^^^^^^^^^^^^^^^

The URL to which the authorization request should be sent.

class
^^^^^

The class that describes how the communication with the social service
should look like.

name
^^^^

A short name for the Social service

saml_endpoint
^^^^^^^^^^^^^

The endpoint the SAML2 authentication request is received on.
Here only the postfix is specified the whole URL is constructed based
on the BASE specification in the idp configuration file.

scope
^^^^^

Which user information that are requested.

social_endpoint
^^^^^^^^^^^^^^^

The endpoint that the social service redirects the user to once the
authentication/authorization is done. Again as with saml_endpoint only
the postfix are needed.

srv_discovery_url
^^^^^^^^^^^^^^^^^

If dynamic provider info discovery and registration a'la OpenID Connect is
performed this is where that starts. If dynamic discovery/registration is
used none of the social service endpoints are necessary to specify.

token_endpoint
^^^^^^^^^^^^^^

The URL to which the token request should be sent

userinfo_endpoint
^^^^^^^^^^^^^^^^^

The URL to which the userinfo request should be sent
