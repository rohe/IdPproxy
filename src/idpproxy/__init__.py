#!/usr/bin/env python
__author__ = 'rolandh'

import os
import sys
import base64
import urlparse
import traceback
import logging

from urlparse import parse_qs

from saml2 import saml, mcache, samlp
from saml2 import s_utils
from saml2 import BINDING_HTTP_REDIRECT, BINDING_SOAP, BINDING_HTTP_POST

from saml2.s_utils import UnknownPrincipal
from saml2.s_utils import UnsupportedBinding

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------

#noinspection PyUnusedLocal
def NOT_AUTHN(environ, start_response, state, req_info):
    return bad_request(start_response, "Unimplemented")

# ----------------------------------------------------------------------------

def exception_log():
    for line in traceback.format_exception(*sys.exc_info()):
        logger.info("## %s" % line.strip("\n"))

def cgi_field_storage_to_dict( field_storage ):
    """Get a plain dictionary, rather than the '.value' system used by the
    cgi module."""

    params = {}
    for key in field_storage.keys():
        try:
            params[ key ] = field_storage[ key ].value
        except AttributeError:
            if isinstance(field_storage[ key ], basestring):
                params[key] = field_storage[key]

    return params

# ----------------------------------------------------------------------------

#noinspection PyUnusedLocal
def soap_logout_response(idp, req_info, status=None):
    logger.info("LOGOUT of '%s' by '%s'" % (req_info.subject_id(),
                                            req_info["sp_entity_id"]))
    
    resultcode, headers, message = idp.logout_response(req_info,
                                                       [BINDING_SOAP],
                                                       status)
    return resultcode, headers, message

#noinspection PyUnusedLocal
def logout_response(server_env, req_info, status=None):
    logger.info("LOGOUT of '%s' by '%s'" % (req_info.subject_id(),
                                            req_info["sp_entity_id"]))

    return server_env["idp"].logout_response(req_info, [BINDING_HTTP_REDIRECT,
                                             BINDING_HTTP_POST], status,
                                             sign=server_env["SIGN"])

def err_response(server_env, req_info, info):
    """
    :param info: Either an exception or and 2-tuple (SAML error code, txt)
    """

    err_resp = server_env["idp"].error_response(req_info["consumer_url"],
                                                req_info["id"],
                                                req_info["sp_entity_id"], info)

    logger.info("LOGIN failed ErrResponse: %s" % err_resp)

    argv = {
        "action": req_info["consumer_url"],
        "response": base64.b64encode("%s" % err_resp),
        "state": req_info["relay_state"],
    }

    template = server_env["template_lookup"].get_template("sso_form.mako")
    return '200 OK', [('Content-Type', 'text/html')], [template.render(**argv)]

def authn_response(server_env, req_info, userid, identity,
                   authn=None, authn_decl=None, service=""):
    # base 64 encoded request

    logger.debug("User info: %s" % identity)

    if service:
        issuer = "%s%s" % (server_env["base_url"], service)
    else:
        issuer = None

    logger.info("ISSUER: %s" % issuer)
    authn_resp = server_env["idp"].create_authn_response(identity,
                                req_info["id"],
                                req_info["consumer_url"],
                                req_info["sp_entity_id"],
                                req_info["request"].name_id_policy,
                                str(userid),
                                authn=authn, sign_assertion=server_env["SIGN"],
                                authn_decl=authn_decl,
                                issuer=issuer)

    logger.info("LOGIN success: sp_entity_id=%s#authn=%s" % (
                                            req_info["sp_entity_id"],
                                            authn))
    logger.debug("AuthNResponse: %s" % authn_resp)

    argv = {
        "action": req_info["consumer_url"],
        "response": base64.b64encode("".join(authn_resp)),
        "state": req_info["relay_state"],
    }

    logger.debug("template action:%s state:%s" % (argv["action"],
                                                  argv["state"]))

    template = server_env["template_lookup"].get_template("sso_form.mako")
    return ('200 OK', [('Content-Type', 'text/html')],
                                            [template.render(**argv)])

# -----------------------------------------------------------------------------

#noinspection PyUnusedLocal
def get_eptid(server_env, req_info, identity, session):

    args_ = (session["permanent_id"], [session["authn_auth"]])
    return server_env["eptid"].get(server_env["idp"].conf.entityid,
                                    req_info["sp_entity_id"],
                                    args_)

#noinspection PyUnusedLocal
def do_req_response(server_env, req_info, response, _environ, source,
                    session, service=""):
    if session["status"] == "FAILURE":
        info = (samlp.STATUS_AUTHN_FAILED, response)
        return err_response(server_env, req_info, info)

    identity = response
    if identity:
        userid = identity["uid"] #
        if "eduPersonTargetedID" not in identity:
            identity["eduPersonTargetedID"] = get_eptid(server_env, req_info,
                                                        identity, session)
    else:
        userid = "anonymous"

    logger.debug("[do_req_response] identity: %s" % (identity,))

    session["identity"] = identity
    session["eptid"] = identity["eduPersonTargetedID"]
    return authn_response(server_env, req_info, userid, identity,
                            authn=(saml.AUTHN_PASSWORD, source),
                            service=service)

def do_logout_response(req_info, status=None):
    if status:
        status = s_utils.error_status_factory((status, "Logout failed"))

    return logout_response(req_info, status)

# -----------------------------------------------------------------------------

def return_active_info(environ, start_response, server_env, state):

    logger.debug("[return_active_info]")

    try:
        req_info = get_authn_request(environ, server_env)
    except UnknownPrincipal:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ["Don't know the SP that referred you here"]
    except UnsupportedBinding:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ["Don't know how to reply to the SP that referred you here"]
    except Exception:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ["Exception while parsing the AuthnRequest"]

    if req_info is None:
        # return error message
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ["Missing SAMLRequest"]

    if req_info:
        session = state.old_session(req_info["sp_entity_id"])
        if session:
            if req_info["request"].force_authn: # even if active session
                session.reset()
                session["req_info"] = req_info
                start_response("302 Found", [("Location", "/")])
                return [""]

            identity = session["identity"]
            if not identity:
                return NOT_AUTHN(environ, start_response, state,
                                    req_info)
        if not session or not session.active():
            return NOT_AUTHN(environ, start_response, state, req_info)
    else:
        return NOT_AUTHN(environ, start_response, state, req_info)


    logger.debug("[return_active_info] Old session: %s" % session)
    identity = session["identity"]
    try:
        _eptid = session["eptid"]
    except KeyError:
        _eptid = get_eptid(server_env, req_info, identity, session)
        session["eptid"] = _eptid

    identity["eduPersonTargetedID"] = _eptid
    authn_auth = session["authn_auth"]
    #def do_req_response(req_info, response, _environ, source, session,
    #service):

    (resp, head, content) = do_req_response(server_env, req_info, identity,
                                            environ, authn_auth, session)
    start_response(resp, head)
    return content

# ----------------------------------------------------------------------------

def do_logout(environ, start_response, server_env, state):
    """ Get a POSTed request """

    if environ['REQUEST_METHOD'].upper() != 'POST':
        start_response("400 Bad request", [('Content-Type', 'text/plain')])
        return []

    content_type = environ.get('CONTENT_TYPE', 'application/soap+xml')
    if content_type != 'application/soap+xml':
        start_response("400 Bad request", [('Content-Type', 'text/plain')])
        return []

    _debug = server_env["DEBUG"]

    length = int(environ["CONTENT_LENGTH"])
    request = environ["wsgi.input"].read(length)

    try:
        req_info = server_env["idp"].parse_logout_request(request)
        logger.debug("LOGOUT request parsed OK")
        logger.debug("REQ_INFO: %s" % req_info.message)
    except KeyError, exc:
        logger.error("logout request error: %s" % (exc,))
        start_response("400 Bad request", [('Content-Type', 'text/plain')])
        return ["Erroneous logout request"]

    if not state.known_session(req_info.issuer()):
        start_response("400 Bad request", [('Content-Type', 'text/plain')])
        return ["Logout request from someone I know nothing about"]

    # look for the subject
    subject = req_info.subject_id()
    logger.debug("Logout subject: %s" % (subject.text.strip(),))
    status = None

    session = state.old_session(req_info["sp_entity_id"])
    if session:
        session["authentication"] = "OFF"

    (resp, head, content) = do_logout_response(req_info.message,
                                                status)
    start_response(resp, head)
    return content

def redirect_logout(environ, start_response, server_env, state):

    logout_req = None
    if "QUERY_STRING" in environ:
        _debug = server_env["DEBUG"]
        query = parse_qs(environ["QUERY_STRING"])
        logger.debug("[redirect_logout] query: %s" % query)
        try:
            logout_req = server_env["idp"].parse_logout_request(
                                query["SAMLRequest"][0], BINDING_HTTP_REDIRECT)
            logger.debug("LOGOUT request parsed OK")
            logger.debug("LOGOUT_REQ: %s" % logout_req)
        except KeyError:
            # return error reply
            start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
            return ['Missing session']

    if logout_req is None:
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])
        return ['Missing logout request']

    # look for the subject
    subject = logout_req.subject_id()
    logger.info("Logout subject: %s" % (subject.text.strip(),))
    status = None

    (resp, head, content) = do_logout_response(logout_req.message,
                                                status)
    head.append(state.cookie(expire="now"))
    start_response(resp, head)
    return content

# ----------------------------------------------------------------------------

def relay_state(dic):
    try:
        return dic["RelayState"][0]
    except KeyError:
        return ""

def authentication_state(info):
    try:
        return info["authentication"]
    except KeyError:
        return ""

def get_session_id(environ):
    try:
        parres = urlparse.urlparse(environ["HTTP_REFERER"])
        qdict = parse_qs(parres.query)
        return qdict["sessionid"][0]
    except KeyError:
        qdict = parse_qs(environ["QUERY_STRING"])
        return qdict["sessionid"][0]

def bad_request(start_response, msg):
    start_response('400 Bad Request', [('Content-Type', 'text/plain')])
    return [msg]

#noinspection PyUnusedLocal
def base(_environ, start_response, _user):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ["PLACEHOLDER !!!"]

# =============================================================================

def get_authn_request(environ, server_env):
    """
    Tries to pry and parse the AuthnRequest from the query.

    :param environ: The environ variables
    :param server_env: Server environment
    :return: The request info if no error was encountered while parsing the
        AuthnRequest. None if an error was encountered. None if there was no
        AuthnRequest.
    """

    if "QUERY_STRING" in environ:
        _debug = server_env["DEBUG"]
        query = parse_qs(environ["QUERY_STRING"])
        logger.debug("[get_authn_request] query: %s" % query)
        if query:
            try:
                req_info = server_env["idp"].parse_authn_request(
                                                        query["SAMLRequest"][0])
                req_info["relay_state"] = relay_state(query)
                logger.debug("[get_authn_request] AUTHN request parsed OK")
                logger.debug("[get_authn_request] REQ_INFO: %s" % req_info)
                return req_info
            except KeyError:
                return None
            except (UnknownPrincipal, UnsupportedBinding):
                logger.error(
                    "[get_authn_request] Unknown principal or unknown binding")
                raise

    return None

#noinspection PyUnusedLocal
def authn_init(environ, start_response, server_env, state, _debug,
               _service):
    """ Initialize an authentication session. Creates a session instance
    and adds it to the server state information.

    :param environ:
    :param start_response:
    :param server_env:
    :param state:
    :param _debug:
    :param _service:
    :return:
    """
    logger.debug("[%s]" % _service)

    try:
        req_info = get_authn_request(environ, server_env)
    except Exception:
        raise Exception("Exception while parsing the AuthnRequest")

    if req_info:
        logger.debug("[%s]req_info: %s" % (_service, req_info))
        session = state.get_session(req_info["sp_entity_id"])
        state.add_session(session.session_id)
        _ = session.remember(req_info)
        sidd = session.sid_digest
    else:
        session = None
        sidd = 0

    logger.debug("[%s]SESSION[%s]: %s" % (_service, sidd, session))

    return session, sidd


# ----------------------------------------------------------------------------

#noinspection PyUnusedLocal
def not_found(_environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']

# ----------------------------------------------------------------------------

def static_file(server_env, path):
    try:
        os.stat(server_env["STATIC_DIR"]+path)
        return True
    except os.error:
        return False

def static(environ, start_response, path):
    try:
        text = open(path).read()
        if path.endswith(".ico"):
            start_response('200 OK', [('Content-Type', "image/x-icon")])
        elif path.endswith(".html"):
            start_response('200 OK', [('Content-Type', 'text/html')])
        elif path.endswith(".txt"):
            start_response('200 OK', [('Content-Type', 'text/plain')])
        else:
            start_response('200 OK', [('Content-Type', "text/xml")])
        return [text]
    except IOError:
        return not_found(environ, start_response)

# ----------------------------------------------------------------------------
#
def _dict_to_table(dic, border=""):
    result = ["<table border=\"%s\">" % border]
    for key, val in dic.items():
        result.append("<tr><td>%s</td><td>%s</td></tr>" % (key, val))
    result.append("</table>")
    return "\n".join(result)

SOCIAL_SRV = ["twitter", "openid", "google", "facebook", "liveid"]

#noinspection PyUnusedLocal
def status(environ, start_response, state):
    """ Return the status of the users SSO sessions """
    result = []
    for session in state.sessions():
        for typ in SOCIAL_SRV:
            if session[typ]:
                result.append("<h2>%s</h2>" % typ.upper())
                break

        result.append("<table border=\"1\">")
        for prop in ["authentication", "authn_auth", "identity"]:
            val = session[prop]
            if isinstance(val, dict):
                val = _dict_to_table(val)
            result.append("<tr><td>%s</td><td>%s</td></tr>" % (prop, val))
        result.append("</table>")
        result.append("<br>")

    start_response('200 OK', [('Content-Type', 'text/html')])
    return result

# ----------------------------------------------------------------------------

def active_session(session):
    try:
        info = session.get()
        if "authentication" in info and info["authentication"] == "OK":
            return True
    except mcache.ToOld:
        pass

    return False

def login_attempt(environ):
    try:
        query = parse_qs(environ["QUERY_STRING"])
        if query and "SAMLRequest" in query:
            return True
    except KeyError:
        pass

    return False

# ----------------------------------------------------------------------------
