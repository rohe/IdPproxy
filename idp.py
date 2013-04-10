#!/usr/bin/env python

import logging
import urlparse
import argparse
import idpproxy

from idpproxy import idp_srv
from idpproxy import utils
from idpproxy.metadata.secret import MetadataGeneration

from saml2 import server
from saml2 import BINDING_HTTP_REDIRECT

from idpproxy import eptid
from idpproxy import cache

from jwkest.jwk import rsa_pub_load, rsa_priv_to_pub

# ----------------------------------------------------------------------------
from saml2.config import LOG_LEVEL

logger = logging.getLogger("")


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

        
EXT_FORMAT = '%(asctime)s %(name)s:%(sid)s:%(remote)s %(levelname)s %(message)s'
EXT_FORMATTER = logging.Formatter(EXT_FORMAT)

BASE = "/"
URLS = [
    #(r'logout$', idpproxy.do_logout),
    (r'status$', idpproxy.status),
]

SERVER_ENV = {}


def application(environ, start_response):
    """
    The main WSGI application. 
    
    If nothing matches call the `not_found` function.
    
    :param environ: The HTTP application environment
    :param start_response: The application to run when the handling of the 
        request is done
    :return: The response as a list of lines
    """

    global SERVER_ENV
    global EXT_FORMATTER

    path = environ.get('PATH_INFO', '')

    logger.debug("ENVIRON: %s" % environ)
    _sid = SERVER_ENV["sid_generator"].next()
    try:
        _remote = environ["REMOTE_HOST"]
    except KeyError:
        _remote = environ["REMOTE_ADDR"]

    _logger = logging.getLogger(name="session")
    if not _logger.handlers:
        _hndl = SERVER_ENV["idp"].config.log_handler()
        _hndl.setFormatter(EXT_FORMATTER)
        _logger.addHandler(_hndl)
    _logger = logging.LoggerAdapter(_logger, {'sid': _sid, "remote": _remote})
    environ["idpproxy.log"] = _logger

    # to avoid getting duplicated entries
    _logger.propagate = False
    _logger.info("%s %s" % (environ.get("REQUEST_METHOD", ''), path))
    
    kaka = environ.get("HTTP_COOKIE", '')
    logger.debug("Cookie: %s" % (kaka,))

    _cache = SERVER_ENV["CACHE"]
    if kaka:
        sid = _cache.known_as(kaka)
        if not sid:
            sid = _cache.sid()
    else:
        sid = _cache.sid()

    logger.debug("SID: %s" % sid)

    if idpproxy.static_file(SERVER_ENV, path):
        return idpproxy.static(environ, start_response,
                               SERVER_ENV["STATIC_DIR"] + path)
    elif idpproxy.metadata_file(SERVER_ENV, path):
        return idpproxy.static(environ, start_response,
                               SERVER_ENV["METADATA_DIR"] + path)
    if path == BASE:
        user = environ.get("REMOTE_USER", "")
#        if not user:
#            user = environ.get("repoze.who.identity", "")

        if user:
            environ['idpproxy.url_args'] = path
            return idpproxy.base(environ, start_response, user)
        else:
            logger.debug("-- No USER --")
            #return idpproxy.not_found(environ, start_response)
            return idpproxy.not_authn(environ, start_response)
    elif path.startswith("/logo/"):
        environ['idpproxy.url_args'] = "." + path
        return idp_srv.logo(environ, start_response, SERVER_ENV)
    elif path == "/logout":
        return idp_srv.logout(environ, start_response, sid, SERVER_ENV)
    elif generateMetadata is not None and generateMetadata.verifyHandleRequest(path):
        return generateMetadata.handleRequest(environ, start_response, path)
    else:
        environ['idpproxy.url_args'] = ""
        return idp_srv.auth_choice(path, environ, start_response, sid,
                                   SERVER_ENV)

# ----------------------------------------------------------------------------
__author__ = 'rohe0002'

from jwkest.jwk import rsa_load

# ----------------------------------------------------------------------------

SERVER_ENV = {}

from mako.lookup import TemplateLookup
ROOT = './'
LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')


def setup_server_env(proxy_conf, conf_mod, key):
    global SERVER_ENV
    global logger
    #noinspection PyUnboundLocalVariable
    SERVER_ENV = dict([(k, v) for k, v in proxy_conf.__dict__.items()
                       if not k.startswith("__")])

    SERVER_ENV["sessions"] = {}

    SERVER_ENV["eptid"] = eptid.Eptid(proxy_conf.EPTID_DB, proxy_conf.SECRET)

    _idp = server.Server(conf_mod)

    args = {"metad": _idp.metadata, "dkeys": {"rsa": [key]}}

    SERVER_ENV["consumer_info"] = utils.ConsumerInfo(proxy_conf.CONSUMER_INFO,
                                                     **args)
    SERVER_ENV["service"] = proxy_conf.SERVICE

    # add the service endpoints
    part = urlparse.urlparse(_idp.config.entityid)
    base = "%s://%s/" % (part.scheme, part.netloc)
    SERVER_ENV["SCHEME"] = part.scheme
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

    SERVER_ENV["HOST"] = host
    SERVER_ENV["PORT"] = port

    endpoints = {"single_sign_on_service": [], "single_logout_service": []}
    for key, _dict in proxy_conf.SERVICE.items():
        _sso = _dict["saml_endpoint"]
        endpoints["single_sign_on_service"].append("%s%s" % (base, _sso))
        endpoints["single_logout_service"].append(("%s%s/logout" % (base, _sso),
                                                   BINDING_HTTP_REDIRECT))

    _idp.config.setattr("idp", "endpoints", endpoints)

    SERVER_ENV["idp"] = _idp
    SERVER_ENV["template_lookup"] = LOOKUP
    SERVER_ENV["sid_generator"] = session_nr()
    SERVER_ENV["base_url"] = base
    SERVER_ENV["STATIC_DIR"] = proxy_conf.STATIC_DIR
    SERVER_ENV["METADATA_DIR"] = proxy_conf.METADATA_DIR
    SERVER_ENV["SIGN"] = proxy_conf.SIGN

    #print SERVER_ENV
    if proxy_conf.CACHE == "memory":
        SERVER_ENV["CACHE"] = cache.Cache(SERVER_ENV["SERVER_NAME"],
                                          SERVER_ENV["SECRET"])
    elif proxy_conf.CACHE.startswith("file:"):
        SERVER_ENV["CACHE"] = cache.Cache(SERVER_ENV["SERVER_NAME"],
                                          SERVER_ENV["SECRET"],
                                          filename=proxy_conf.CACHE[5:])
    
    logger = setup_logger(_idp.config)
    if proxy_conf.DEBUG:
        logger.setLevel(logging.DEBUG)

    logger.debug("SERVER_ENV: %s" % SERVER_ENV)
    return _idp


def usage():
    print "Usage: %s configuration_file [-p port][-d][-h]" % sys.argv[0]
    
if __name__ == '__main__':
    import sys

    #from wsgiref.simple_server import make_server
    from cherrypy import wsgiserver
    #from cherrypy.wsgiserver import ssl_pyopenssl

    from config import idp_proxy_conf

    _parser = argparse.ArgumentParser()
    _parser.add_argument('-d', dest='debug', action='store_true',
                         help="Print debug information")
    _parser.add_argument('-v', dest='verbose', action='store_true',
                         help="Print runtime information")
    _parser.add_argument('-r', dest="rsa_file",
                         help="A file containing a RSA key")
    _parser.add_argument('-p', dest="rsa_public_file",
                         help="A file containing a public RSA key")
    _parser.add_argument("config", nargs="?", help="Server configuration")

    args = _parser.parse_args()

    if args.rsa_file:
        key = rsa_load(args.rsa_file)
    else:
        key = None

    if args.rsa_file:
        _key = rsa_priv_to_pub(args.rsa_file)
    elif args.rsa_public_file:
        _key = rsa_pub_load(args.rsa_public_file)
    else:
        _key = None

    if _key:
        generateMetadata = MetadataGeneration(
            logger, idp_proxy_conf.SERVICE, _key,
            [{"local": ["metadata/swamid-2.0.xml"]}])

    #noinspection PyUnboundLocalVariable
    _idp = setup_server_env(idp_proxy_conf, args.config, key)

    print SERVER_ENV["base_url"]
    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', SERVER_ENV["PORT"]),
                                        application)

    #if idp_proxy_conf.SERVER_CERT and idp_proxy_conf.SERVER_KEY:
    #    SRV.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(idp_proxy_conf.SERVER_CERT,
    #                                                     idp_proxy_conf.SERVER_KEY,
    #                                                     idp_proxy_conf.CERT_CHAIN)

    #SRV = make_server(SERVER_ENV["host"], SERVER_ENV["port"], application)
    print "listening on port: %s" % SERVER_ENV["PORT"]
    logger.info("Server up and running!")

    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
