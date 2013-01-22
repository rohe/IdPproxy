#!/usr/bin/env python
import logging
import urlparse
from saml2 import server, BINDING_HTTP_REDIRECT
from saml2.config import LOG_LEVEL
from idpproxy import eptid, utils, cache

logger = logging.getLogger("")

__author__ = 'rolandh'

SERVER_ENV = {}

from mako.lookup import TemplateLookup
ROOT = './'
LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')

def setup_logger(conf):
    global logger

    try:
        logger.setLevel(LOG_LEVEL[conf.logger["loglevel"].lower()])
    except KeyError: # reasonable default
        logger.setLevel(logging.INFO)

    logger.addHandler(conf.log_handler())

    return logger

def session_nr():
    n = 0
    while True:
        n += 1
        yield n

def setup_server_env(proxy_conf, conf_mod, key):
    global SERVER_ENV
    global logger
    #noinspection PyUnboundLocalVariable
    SERVER_ENV = dict([(k, v) for k,v in proxy_conf.__dict__.items()\
                       if not k.startswith("__")])

    SERVER_ENV["sessions"] = {}

    SERVER_ENV["eptid"] = eptid.Eptid(proxy_conf.EPTID_DB, proxy_conf.SECRET)

    _idp = server.Server(conf_mod)

    args = {"metad":_idp.metadata, "dkeys":{"rsa": [key]}}

    SERVER_ENV["consumer_info"] = utils.ConsumerInfo(proxy_conf.CONSUMER_INFO,
                                                     **args)
    SERVER_ENV["service"] = proxy_conf.SERVICE

    # add the service endpoints
    part = urlparse.urlparse(_idp.conf.entityid)
    base = "%s://%s/" % (part.scheme, part.netloc)
    SERVER_ENV["SCHEME"] = part.scheme
    try:
        (host,port) = part.netloc.split(":")
        port = int(port)
    except ValueError: # no port specification
        host = part.netloc
        if part.scheme == "http":
            port = 80
        elif part.scheme == "https":
            port = 443
        else:
            raise ValueError("Unsupported scheme")

    SERVER_ENV["HOST"] = host
    SERVER_ENV["PORT"] = port

    endpoints = {"single_sign_on_service": [], "single_logout_service": []}
    for key, _dict in proxy_conf.SERVICE.items():
        _sso = _dict["saml_endpoint"]
        endpoints["single_sign_on_service"].append("%s%s" % (base, _sso))
        endpoints["single_logout_service"].append(("%s%s/logout" % (base,_sso),
                                                   BINDING_HTTP_REDIRECT))

    _idp.conf.setattr("idp", "endpoints", endpoints)

    SERVER_ENV["idp"] = _idp
    SERVER_ENV["template_lookup"] = LOOKUP
    SERVER_ENV["sid_generator"] = session_nr()
    SERVER_ENV["base_url"] = base
    SERVER_ENV["STATIC_DIR"] = proxy_conf.STATIC_DIR
    SERVER_ENV["SIGN"] = proxy_conf.SIGN

    #print SERVER_ENV
    if proxy_conf.CACHE == "memory":
        SERVER_ENV["CACHE"] = cache.Cache(SERVER_ENV["SERVER_NAME"],
                                          SERVER_ENV["SECRET"])
    elif proxy_conf.CACHE.startswith("file:"):
        SERVER_ENV["CACHE"] = cache.Cache(SERVER_ENV["SERVER_NAME"],
                                          SERVER_ENV["SECRET"],
                                          filename=proxy_conf.CACHE[5:])

    logger = setup_logger(_idp.conf)
    if proxy_conf.DEBUG:
        logger.setLevel(logging.DEBUG)

    logger.debug("SERVER_ENV: %s" % SERVER_ENV)
    return _idp

if __name__ == "__main__":
    from config import idp_proxy_conf
    config = "idp_conf"
    key = None

    _idp = setup_server_env(idp_proxy_conf, config, key)
    binding=BINDING_HTTP_REDIRECT
    addrs = _idp.conf.endpoint("single_sign_on_service", binding)
    print addrs
