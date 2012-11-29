#

from saml2 import samlp

import logging
from idpproxy import exception_log
from idpproxy import err_response
from idpproxy import do_req_response

logger = logging.getLogger(__name__)

class Social(object):
    def __init__(self, client_id, client_secret, social_endpoint=None,
                 attribute_map=None, authenticating_authority=None,
                 name="", **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.attribute_map = attribute_map
        self.social_endpoint = social_endpoint
        self.authenticating_authority = authenticating_authority
        self.name = name
        self.extra = kwargs

    def begin(self, environ, server_env, start_response,
              cookie, sid, info):
        pass

    def phaseN(self, environ, query, server_env, sid):
        pass

    #noinspection PyUnusedLocal
    def callback(self, environ, server_env, start_response, cookie,
                 sid, info):
        _debug = server_env["DEBUG"]
        _service = self.__class__.__name__

        logger.debug("[do_%s] environ: %s" % (_service, environ))
        logger.debug("[do_%s] query: %s" % (_service, info))

        session = server_env["CACHE"][sid]

        if session:
            req_info = session["req_info"]
        else:
            req_info = None

        try:
            result = self.phaseN(environ, info, server_env, sid)
            logger.debug("[do_%s] response: %s" % (_service, result))

            if isinstance(result[2], list): # in process
                start_response(result[0], result[1])
                return result[2]

            (success, identity, session) = result
            try:
                req_info = session["req_info"]
            except KeyError:
                pass

        except Exception, exc:
            exception_log()
            (stat, headers, content) = err_response(server_env, req_info, exc)
            start_response(stat, headers)
            return content

        logger.debug("Session: %s" % session)
        # redirect back to the SP
        if req_info:
            if success:
                session["authentication"] = "OK"
                if self.authenticating_authority:
                    auth_auth = self.authenticating_authority
                else:
                    auth_auth = session["authn_auth"]
                #(server_env, req_info, response, _environ, source,
                #session, service="")
                (stat, headers, content) = do_req_response(server_env,
                                                    req_info, identity,
                                                    environ, auth_auth,
                                                    session,
                                                    self.extra["entity_id"])
                headers.append(cookie)
                if _debug:
                    logger.debug("[do_%s] return headers: %s" % (_service,
                                                                 headers))
            else:
                session["authentication"] = "FAILED"
                error_info = (samlp.STATUS_AUTHN_FAILED , identity)
                (stat, headers, content) = err_response(server_env, req_info,
                                                        error_info)

                headers.append(cookie)
            start_response(stat, headers)
        else:
            content = ["%s" % identity]
            start_response('200 OK', [('Content-Type', 'text/html')])

        #return content
        return content

    def convert(self, profile):
        if self.attribute_map is None:
            return profile

        res = {}
        for key,val in self.attribute_map.items():
            try:
                if isinstance(val, tuple):
                    pat, param = val
                    pval = profile[param]
                    if isinstance(pval, basestring):
                        pval = [pval]
                    try:
                        func = getattr(self, pat)
                        res[key] = [func(v) for v in pval]
                    except AttributeError:
                        res[key] = [pat % v for v in pval]
                else:
                    res[key] = profile[val]
            except KeyError:
                pass
        return res