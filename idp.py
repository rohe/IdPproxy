#!/usr/bin/env python

import logging
import urlparse
import argparse
import idpproxy
from idpproxy import idp_srv

#USAGE = "single"

#from urlparse import parse_qs

from saml2 import server
from saml2 import BINDING_HTTP_REDIRECT

from idpproxy import eptid
from idpproxy import cache

# ----------------------------------------------------------------------------
from saml2.config import LOG_LEVEL

logger = logging.getLogger("")

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

        
EXT_FORMAT = '%(asctime)s %(name)s:%(sid)s:%(remote)s %(levelname)s %(message)s'
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
    _debug = SERVER_ENV["DEBUG"]
    #_usage = SERVER_ENV["USAGE"]
    path = environ.get('PATH_INFO', '')

    _sid = SERVER_ENV["sid_generator"].next()
    _logger = logging.LoggerAdapter(logger,
                                    { 'sid' : _sid,
                                      "remote": environ["REMOTE_HOST"]})

    # to avoid getting to duplicated entries
    _logger.propagate = False
    _logger.info( "%s %s" % (environ.get("REQUEST_METHOD", ''), path))
    
    kaka = environ.get("HTTP_COOKIE", '')
    _logger.debug("Cookie: %s" % (kaka,))

    _cache = SERVER_ENV["CACHE"]
    if kaka:
        sid = _cache.known_as(kaka)
        if not sid:
            sid = _cache.sid()
    else:
        sid = _cache.sid()

    _logger.debug("SID: %s" % sid)

    if idpproxy.static_file(SERVER_ENV, path):
        return idpproxy.static(environ, start_response,
                               SERVER_ENV["STATIC_DIR"]+path)
    if path == BASE:
        user = environ.get("REMOTE_USER", "")
        if not user:
            user = environ.get("repoze.who.identity", "")

        if user:
            environ['idpproxy.url_args'] = path
            return idpproxy.base(environ, start_response, user)
        else:
            _logger.debug("-- No USER --")
            return idpproxy.not_found(environ, start_response)
            #return idp_srv.not_authn(environ, start_response, _logger,
            # state)
    elif path.startswith("/logo/"):
        environ['idpproxy.url_args'] = "."+path
        return idp_srv.logo(environ, start_response, SERVER_ENV)
    else:
        environ['idpproxy.url_args'] = ""
        return idp_srv.auth_choice(path, environ, start_response, sid,
                                   SERVER_ENV)

# ----------------------------------------------------------------------------
__author__ = 'rohe0002'

import json

from jwkest.jwe import decrypt
from jwkest.jwk import rsa_load

from saml2 import extension_elements_to_elements
from saml2.extension import mdattr, idpdisc
from saml2.extension.mdattr import EntityAttributes


def customer_info(metad, dkeys):
    res = {}

    for ent,item in metad.entity.items():
        if "sp_sso" not in item:
            continue

        for sp in item["sp_sso"]:
            if sp.extensions is None:
                continue

            elems = extension_elements_to_elements(sp.extensions.extension_elements,
                                                   [mdattr, idpdisc])
            for elem in elems:
                if isinstance(elem, EntityAttributes):
                    for attr in elem.attribute:
                        if attr.name == "http://swamid.sunet.se/customer":
                            for val in attr.attribute_value:
                                res[ent] = json.loads(decrypt(val.text, dkeys,
                                                              "private"))
    return res

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
    SERVER_ENV = dict([(k, v) for k,v in proxy_conf.__dict__.items() \
                                                if not k.startswith("__")])

    SERVER_ENV["sessions"] = {}

    SERVER_ENV["eptid"] = eptid.Eptid(proxy_conf.EPTID_DB, proxy_conf.SECRET)

    _idp = server.Server(conf_mod)

    SERVER_ENV["CUSTOMER_INFO"] = customer_info(_idp.metadata, {"rsa": [key]})
    SERVER_ENV["service"] = proxy_conf.SERVICE

    # add the service endpoints
    part = urlparse.urlparse(_idp.conf.entityid)
    base = "%s://%s/" % (part.scheme, part.netloc)

    endpoints = {"single_sign_on_service": [], "single_logout_service": []}
    for key, _dict in proxy_conf.SERVICE.items():
        _sso = _dict["saml_endpoint"]
        endpoints["single_sign_on_service"].append("%s%s" % (base, _sso))
        endpoints["single_logout_service"].append(("%s%s/logout" % (base,_sso),
                                                   BINDING_HTTP_REDIRECT))

    _idp.conf._attr["idp"]["endpoints"] = endpoints

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

    return _idp

def usage():
    print "Usage: %s configuration_file [-p port][-d][-h]" % sys.argv[0]
    
if __name__ == '__main__':
    import sys

    #from wsgiref.simple_server import make_server
    from cherrypy import wsgiserver
    from cherrypy.wsgiserver import ssl_pyopenssl

    from config import idp_proxy_conf

    _parser = argparse.ArgumentParser()
    _parser.add_argument('-p', dest='port', default=8089, type=int,
                              help="Print debug information")
    _parser.add_argument('-d', dest='debug', action='store_true',
                              help="Print debug information")
    _parser.add_argument('-v', dest='verbose', action='store_true',
                              help="Print runtime information")
    _parser.add_argument('-r', dest="rsa_file",
                        help="A file containing a RSA key")
    _parser.add_argument("config", nargs="?", help="Server configuration")

    args = _parser.parse_args()

    if args.rsa_file:
        key = rsa_load(args.rsa_file)
    else:
        key = None

    idp_proxy_conf.PORT = args.port
    #noinspection PyUnboundLocalVariable
    _idp = setup_server_env(idp_proxy_conf, args.config, key)

    print SERVER_ENV["base_url"]
    SRV = wsgiserver.CherryPyWSGIServer(('0.0.0.0', args.port), application)

    SRV.ssl_adapter = ssl_pyopenssl.pyOpenSSLAdapter(idp_proxy_conf.SERVER_CERT,
                                                     idp_proxy_conf.SERVER_KEY,
                                                     idp_proxy_conf.CERT_CHAIN)

    #SRV = make_server(idp_proxy_conf.HOST_NAME, args.port, application)
    print "listening on port: %s" % args.port
    logger.info("Server up and running!")

    try:
        SRV.start()
    except KeyboardInterrupt:
        SRV.stop()
