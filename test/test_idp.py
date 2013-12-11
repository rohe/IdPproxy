#!/usr/bin/env python
import logging
import urlparse
from saml2 import server, BINDING_HTTP_REDIRECT
from saml2.config import LOG_LEVEL
from idpproxy import eptid, utils, cache

logger = logging.getLogger("")

__author__ = 'rolandh'

server_env = {}

from mako.lookup import TemplateLookup

ROOT = './'
LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')


def setup_logger(conf):
    global logger

    try:
        logger.setLevel(LOG_LEVEL[conf.logger["loglevel"].lower()])
    except KeyError:  # reasonable default
        logger.setLevel(logging.INFO)

    logger.addHandler(conf.log_handler())

    return logger


def session_nr():
    n = 0
    while True:
        n += 1
        yield n


def setup_server_env(proxy_conf, conf_mod, key):
    global server_env
    global logger
    #noinspection PyUnboundLocalVariable
    server_env = dict([(k, v) for k, v in proxy_conf.__dict__.items()
                       if not k.startswith("__")])

    server_env["sessions"] = {}

    server_env["eptid"] = eptid.Eptid(proxy_conf.EPTID_DB, proxy_conf.SECRET)

    _idp = server.Server(conf_mod)

    args = {"metad": _idp.metadata, "dkeys": {"rsa": [key]}}

    server_env["consumer_info"] = utils.ConsumerInfo(proxy_conf.CONSUMER_INFO,
                                                     **args)
    server_env["service"] = proxy_conf.SERVICE

    # add the service endpoints
    part = urlparse.urlparse(_idp.config.entityid)
    base = "%s://%s/" % (part.scheme, part.netloc)
    server_env["SCHEME"] = part.scheme
    try:
        (host, port) = part.netloc.split(":")
        port = int(port)
    except ValueError:  # no port specification
        host = part.netloc
        if part.scheme == "http":
            port = 80
        elif part.scheme == "https":
            port = 443
        else:
            raise ValueError("Unsupported scheme")

    server_env["HOST"] = host
    server_env["PORT"] = port

    endpoints = {"single_sign_on_service": [], "single_logout_service": []}
    for _dict in proxy_conf.SERVICE.values():
        _sso = _dict["saml_endpoint"]
        endpoints["single_sign_on_service"].append("%s%s" % (base, _sso))
        endpoints["single_logout_service"].append(("%s%s/logout" % (base, _sso),
                                                   BINDING_HTTP_REDIRECT))

    _idp.config.setattr("idp", "endpoints", endpoints)

    server_env["idp"] = _idp
    server_env["template_lookup"] = LOOKUP
    server_env["sid_generator"] = session_nr()
    server_env["base_url"] = base
    server_env["STATIC_DIR"] = proxy_conf.STATIC_DIR
    server_env["SIGN"] = proxy_conf.SIGN

    #print SERVER_ENV
    if proxy_conf.CACHE == "memory":
        server_env["CACHE"] = cache.Cache(server_env["SERVER_NAME"],
                                          server_env["SECRET"])
    elif proxy_conf.CACHE.startswith("file:"):
        server_env["CACHE"] = cache.Cache(server_env["SERVER_NAME"],
                                          server_env["SECRET"],
                                          filename=proxy_conf.CACHE[5:])

    logger = setup_logger(_idp.config)
    if proxy_conf.DEBUG:
        logger.setLevel(logging.DEBUG)

    logger.debug("SERVER_ENV: %s" % server_env)
    return _idp


if __name__ == "__main__":
    from config import idp_proxy_conf

    config = "idp_conf"
    key_ = None

    idp = setup_server_env(idp_proxy_conf, config, key_)
    binding = BINDING_HTTP_REDIRECT
    addrs = idp.config.endpoint("single_sign_on_service", binding)
    print addrs
