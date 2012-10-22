import urllib
import oauth2 as oauth

from urlparse import parse_qs
from idpproxy.social import Social

import logging
logger = logging.getLogger(__name__)

class Twitter(Social):
    def __init__(self, client_id, client_secret, **kwargs):
        Social.__init__(self, client_id, client_secret, **kwargs)
        self.consumer = oauth.Consumer(client_id, client_secret)

    def token_secret_key(sid):
        return "token_secret_%s" % sid
    
    #noinspection PyUnusedLocal
    def begin(self, environ, server_env, start_response, cookie, sid, info):
        """Step 1: Get a request token. This is a temporary token that is used for
        having the user authorize an access token and to sign the request to obtain
        said access token."""

        session = server_env["CACHE"][sid]

        client = oauth.Client(self.consumer)
        resp, content = client.request(self.extra["request_token_url"], "GET")
        if server_env["DEBUG"]:
            logger.info("Client resp: %s" % resp)
            logger.info("Client content: %s" % content)

        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(parse_qs(content))

        token = oauth.Token(request_token['oauth_token'][0],
                            request_token['oauth_token_secret'][0])

        session['oauth_token'] = request_token['oauth_token'][0]
        session[request_token['oauth_token'][0]] = token
        try:
            dig = session["sid_digest"]
        except KeyError:
            dig = server_env["CACHE"].digest(sid)
            session["sid_digest"] = dig

        callback_url = "%stwitter/%s" % (server_env["base_url"],
                                         session["sid_digest"])
        # Step 2: Redirect to the provider.

        args = {
            "oauth_token": request_token['oauth_token'][0],
            "oauth_callback": callback_url,
        }

        server_env["CACHE"][sid] = session

        url = "%s?%s" % (self.extra["authorization_endpoint"],
                         urllib.urlencode(args))
        start_response("302 Found", [("Location", url), cookie])
        return []


    #noinspection PyUnusedLocal
    def phaseN(self, environ, info, server_env, sid):
        """Step 2: Once the consumer has redirected the user back to the
        oauth_callback URL you can request the access token the user has
        approved. You use the request token to sign this request. After this is
        done you throw away the request token and use the access token returned.
        You should store this access token somewhere safe, like a database, for
        future use."""

        logger.info("response_oauth_token: %s" % info["oauth_token"][0])
        session = server_env["CACHE"][sid]

        try:
            key = info["oauth_token"][0]
        except KeyError:
            session["authentication"] = "FAILED"
            return False, "Access denied", session

        token = session[key]

        #token.set_verifier(oauth_verifier)
        client = oauth.Client(self.consumer, token)

        resp, content = client.request(self.extra["token_endpoint"], "POST")
        if resp['status'] != '200':
            return False, "Invalid response %s." % resp['status'], session

        profile = dict(parse_qs(content))
        # Typical reply{'oauth_token_secret': '....',
        #   'user_id': '111111111',
        #   'oauth_token': '.....',
        #   'screen_name': 'RolandHedberg'}
        if server_env["DEBUG"]:
            logger.info("[Twitter phase2] profile: %s" % (profile,))

        session["permanent_id"] = profile["user_id"][0]
        session["service"] = self.extra["name"]
        session["service_info"] = profile
        session["authn_auth"] = self.authenticating_authority
        session["authentication"] = "OK"
        session["status"] = "SUCCESS"

        return True, self.convert(profile), session



    
