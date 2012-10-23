.. _secrets

How to handle the consumer information
======================================

Where you register at the social services.

Facebook:
 - general information: http://developers.facebook.com/docs/authentication/
 - registration: http://developers.facebook.com/setup/

Google:
 - general information: http://code.google.com/apis/accounts/docs/OpenID.html
 - registration: http://code.google.com/apis/accounts/docs/RegistrationForWebAppsAuto.html

Microsoft Live ID:
 - general information: http://msdn.microsoft.com/en-us/windowslive/default.aspx
 - registration: http://manage.dev.live.com/

Twitter:
 - general information and registration: http://dev.twitter.com/apps

Single Service
--------------

After you have registered at the services you want to use each one
provides you with a identifier and a secret.

If you are running a IdPproxy that only supports one organization
you should place this information in config/secrets.
A typical layout of this file is::

    CONSUMER = {
        "Google": {
            "key": "lingon",
            "secret": "aaaaa"},
        "Facebook": {
            "key": "hallon",
            "secret": "bbbbb"},
        "Twitter":  {
            "key": "jordgubbar",
            "secret": "ccccc"},
    }

*key* is the identifier and *secret* is the the secret you got.

If on the other hand you are running an IdPproxy that will support a number
of organizations you should consider use another pattern.

Central Service
---------------

Here we expect the following:

1. Each organization registers at the social services it wants to use
2. The collected keys and secrets are placed in a file with the same
    format as the CONSUMER variable above.
3. The content of the file is encrypted and placed in a JWT structure
    according to the http://tools.ietf.org/html/draft-ietf-jose-json-web-encryption-06
    specification. The jwenc.py script from the pyjwkest module can be used
    for this. The key used for the encryption should be the public part of
    a RSA key owned by the IdPproxy.
4. The resulting JWT is placed as a value in a EntityAttributes structure that
    can be added to the metadata file for SPs that wants to use the IdPproxy.
    A script *script/create_entity_attribute.py* in the distribution can be
    used for this.
5. The SP metadata with the included EntityAttributes structure is sent to the
    IdPproxy. It will read the info, decypt the JWT and store away the information
    to be used later when the SP wants to use a social service.