#!/usr/bin/env python
from saml2 import BINDING_HTTP_REDIRECT

__author__ = 'rolandh'

from idpproxy import exception_log
from idpproxy import bad_request
from urlparse import parse_qs

from saml2.httputil import Response, NotFound, ServiceError, unpack_redirect

import logging
logger = logging.getLogger(__name__)

# =============================================================================

BASE = "/"
AUTH_CHOICE = BASE + "AuthChoice"
POLICY = "policy.html"

def not_found(environ, start_response, text):
    resp = NotFound(text)
    return resp(environ, start_response)

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

#def get_consumer_key_and_secret(social_service, entity_id, server_env):
#    # Consumer key and secret
#    try:
#        server_env["CONSUMER_INFO"][entity_id][social_service]
#    except KeyError:
#        return CONSUMER[social_service]["key"], \
#               CONSUMER[social_service]["secret"]


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

    _dic["DOMAIN"] = server_env["DOMAIN"]

    if _dic is None:
        return not_found(environ, start_response, 'Unknown service: %s' % path)

    logger.debug("[auth_choice] service: %s, function: %s" % (key, func_name))
    logger.debug("environ: %s" % environ)

    environ['idpproxy.url_args'] = local_path(path)
    _cache = server_env["CACHE"]
    if func_name == "callback": # Callback from the Social service
        try:
            query = parse_qs(environ["QUERY_STRING"])
        except KeyError:
            return not_found(environ, start_response, 'Missing argument')

        logger.debug("[auth_choice] query: %s" % query)
        try:
            entity_id = _cache[sid]["entity_id"]
        except KeyError:
            exception_log()
            return bad_request(environ, start_response, "Unknown session")
    else: # This is the SAML endpoint
        # Should I support mote then HTTP redirect
        _dict = unpack_redirect(environ)
        if _dict is None:
            return bad_request(environ, start_response, "Request missing")

        try:
            query = _dict["SAMLRequest"]
        except KeyError:
            return bad_request(environ, start_response, "Request missing")

        if query:
            logger.debug("Query: %s" % query)

            try:
                req_info = server_env["idp"].parse_authn_request(query,
                                                                 BINDING_HTTP_REDIRECT)
            except KeyError:
                exception_log()
                return bad_request(environ, start_response,
                                   "Expected SAML request")
            except Exception, exc:
                exception_log()
                return bad_request(environ, start_response,
                                   "Faulty SAML request: %s" % exc)

            try:
                req_info.relay_state = _dict["RelayState"]
            except KeyError:
                pass

            logger.debug("type req_info: %s message: %s" % (type(req_info),
                                                            type(req_info.message)))

            entity_id = req_info.sender()
            _cache.set(sid, {"req_info": req_info, "entity_id": entity_id})
        else:
            return not_found(environ, start_response, "No query")

    logger.debug("SID: %s" % sid)
    cookie = server_env["CACHE"].create_cookie(sid,
                                        path="/%s" % _dic["social_endpoint"],
                                        expire=60)

    logger.debug("NEW COOKIE: %s" % (cookie,))
    #logger.debug("_dic: %s" % (_dic,))
    # If we use SP specific client id/secret this is where that gets picked up
    try:
        key, sec = server_env["consumer_info"](_dic["name"], entity_id)
    except KeyError, err:
        return not_found(environ, start_response,
                         "No consumer key and secret (%s)" % err)

    c = _dic["class"](key, sec, **_dic)
    func = getattr(c, func_name)
    logger.debug("Proxy function: %s" % func)
    return func(environ, server_env, start_response, cookie, sid, query)


def logo(environ, start_response, serv_env):
    name = environ['idpproxy.url_args']
    try:
        pict = open(name).read()
        resp = Response(pict, headers=[('Content-Type',
                                        serv_env["LOGO_TYPE"][name[7:]])])
    except IOError, exc:
        resp = ServiceError("%s" % exc)

    return resp(environ, start_response)

# ----------------------------------------------------------------------------

def logout(environ, start_response, sid, server_env):
    msg = ""
    resp = Response(msg)
    return resp(environ, start_response)