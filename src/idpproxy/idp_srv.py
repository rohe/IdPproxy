#!/usr/bin/env python

__author__ = 'rolandh'

import idpproxy
from urlparse import parse_qs

from config.secrets import CONSUMER

import logging
logger = logging.getLogger(__name__)

# =============================================================================

BASE = "/"
AUTH_CHOICE = BASE + "AuthChoice"
POLICY = "policy.html"

def not_found(start_response, text):
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return [text]

def match(path, service):
    """

    :param path: The URL path of the request
    :param service: The service name
    :return: True of the service name is the root of the path otherwise False
    """

    #logger.debug("%s != %s" % (path, service))

    pp = path.split("/")

    if pp[0] == "":
        pp = pp[1:]
    if pp[-1] == "":
        pp = pp[:-1]

    return pp[0] == service

def local_path(path):
    # First non-'' part is the service name

    pp = path.split("/")
    if pp[0] == "":
        pp = pp[1:]
    if pp[-1] == "":
        pp = pp[:-1]

    if len(pp) == 1:
        return ""
    else:
        return "/".join(pp[1:])

def get_consumer_key_and_secret(social_service, entity_id, server_env):
    # Consumer key and secret
    try:
        server_env["CONSUMER_INFO"][entity_id][social_service]
    except KeyError:
        return CONSUMER[social_service]["key"], \
               CONSUMER[social_service]["secret"]

def auth_choice(path, environ, start_response, sid, server_env):
    """

    :param path: The local part or the URL
    :param environ: WSGI environment
    :param start_response: The start_response function
    :param sid: A key into the session cache
    :param server_env:
    :return: A WSGI response
    """

    logger.debug("[auth_choice]")

    if path.startswith("/"):
        path = path[1:]

    _dic = key = None
    func_name = None
    for key, _dict in server_env["service"].items():
        if match(path, _dict["saml_endpoint"]):
            _dic = _dict
            func_name = "begin"
            break
        elif match(path, _dict["social_endpoint"]):
            _dic = _dict
            func_name = "callback"
            break

    if _dic is None:
        return not_found(start_response, 'Unknown service')

    logger.debug("[auth_choice] service: %s, function: %s" % (key, func_name))
    logger.debug("environ: %s" % environ)

    environ['idpproxy.url_args'] = local_path(path)
    _cache = server_env["CACHE"]
    if func_name == "callback": # Callback from the Social service
        try:
            query = parse_qs(environ["QUERY_STRING"])
        except KeyError:
            return not_found(start_response, 'Missing argument')

        logger.debug("[auth_choice] query: %s" % query)
        entity_id = _cache[sid]["entity_id"]
    else: # This is the SAML endpoint
        try:
            query = parse_qs(environ["QUERY_STRING"])
        except KeyError:
            query = None

        if query:
            logger.debug("Query: %s" % query)

            try:
                req_info = server_env["idp"].parse_authn_request(
                                                    query["SAMLRequest"][0])
            except KeyError:
                idpproxy.exception_log()
                return idpproxy.bad_request(start_response,
                                            "Expected SAML request")
            except Exception, exc:
                idpproxy.exception_log()
                return idpproxy.bad_request(start_response,
                                            "Faulty SAML request: %s" % exc)

            req_info["relay_state"] = idpproxy.relay_state(query)

            entity_id = req_info["sp_entity_id"]
            logger.debug("REQ_INFO: %s" % req_info)
            _cache.set(sid, {"req_info": req_info, "entity_id": entity_id})
        else:
            return not_found(start_response, "No query")

    logger.debug("SID: %s" % sid)
    cookie = server_env["CACHE"].create_cookie(sid,
                                        path="/%s" % _dic["social_endpoint"],
                                        expire=60)

    logger.debug("NEW COOKIE: %s" % (cookie,))
    # If we use SP specific client id/secret this is where that gets picked up

    try:
        key, sec = get_consumer_key_and_secret(_dic["name"], entity_id,
                                               server_env)
    except KeyError:
        return not_found(start_response, "No consumer key and secret")

    c = _dic["class"](key, sec, **_dic)
    func = getattr(c, func_name)
    logger.debug("Proxy function: %s" % func)
    return func(environ, server_env, start_response, cookie, sid, query)


def logo(environ, start_response, serv_env):
    name = environ['idpproxy.url_args']
    try:
        pict = open(name).read()
        start_response('200 OK', [('Content-Type',
                                   serv_env["LOGO_TYPE"][name[7:]])])
        return [pict]
    except IOError:
        return idpproxy.not_found(environ, start_response)

# ----------------------------------------------------------------------------
