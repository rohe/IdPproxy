# The port the service will listen on
from idpproxy.social.facebook import FacebookOAuth2
from idpproxy.social.falltrough import FallTrough
from idpproxy.social.google import GoogleOIC
from idpproxy.social.twitter import Twitter
from idpproxy.social.liveid import LiveIDOAuth2
from idpproxy.social.openidconnect import OpenIDConnect

# The name of the service, is used in the cache and in the cookies returned
SERVER_NAME = "idpproxy"
    
CACHE = "memory"
# CACHE = "file:..."
# CACHE = "memcache:['127.0.0.1:11212']"

# Name of the eduPersonTargetedID database
EPTID_DB = "eptid.db"

# debugging or not
DEBUG=True

STATIC_DIR = "static/"
SECRET = "hemlig_text"
SIGN = True

# SAML endpoint, Social protocol endpoint, protocol handler class
SERVICE = {
    "facebook":{
        "saml_endpoint":"facebook_sso",
        "social_endpoint":"facebook",
        "class":FacebookOAuth2,
        "authenticating_authority": 'https://graph.facebook.com/oauth/',
        "token_endpoint": "https://graph.facebook.com/oauth/access_token",
        "authorization_endpoint": 'https://graph.facebook.com/oauth/authorize',
        "userinfo_endpoint": "https://graph.facebook.com/me",
        "permissions": ["email"],
        "attribute_map": {
            "givenName": "first_name",
            "surName": "last_name",
            "displayName": "name",
            "uid": "link",
        },
        "name": "Facebook",
    },
    "twitter":{
        "saml_endpoint":"twitter_sso",
        "social_endpoint":"twitter",
        "authenticating_authority": 'http://api.twitter.com/oauth/',
        "request_token_url": 'http://api.twitter.com/oauth/request_token',
        "token_endpoint": 'http://api.twitter.com/oauth/access_token',
        "authorization_endpoint": 'http://api.twitter.com/oauth/authorize',
        "class":Twitter,
        "attribute_map": {
            "eduPersonPrincipalName": ("%s@twitter.com", "screen_name"),
            "displayName": "screen_name",
            "uid": "user_id",
            },
        "name": "Twitter",
    },
    "google": {
        "saml_endpoint":"google_sso",
        "social_endpoint":"google",
        "authenticating_authority": "https://www.google.com/accounts/o8/id", # No completely true but ..
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/auth",
        "token_endpoint": "https://accounts.google.com/o/oauth2/token",
        "verification_endpoint": "https://www.googleapis.com/oauth2/v1/tokeninfo",
        "userinfo_endpoint": "https://www.googleapis.com/oauth2/v1/userinfo",
        "scope": ["https://www.googleapis.com/auth/userinfo.profile",
                  "https://www.googleapis.com/auth/userinfo.email"],
        "attribute_map": {
            "uid": "id",
            "email": "email",
            #"verified_email": true,
            "displayName": "name",
            "givenName": "given_name",
            "surname": "family_name",
        },
        "class":GoogleOIC,
        "name": "Google",
    },
    "fallthrough":{ # Just for testing
        "saml_endpoint":"fallthrough_sso",
        "social_endpoint":"fallthrough",
        "class":FallTrough,
        "variable": "session_id",
        "attribute_map": None,
        "name": "Fallthrough",
    },
    "roland":{
        "saml_endpoint": "oic_sso",
        "social_endpoint": "oic",
        "class": OpenIDConnect,
        "variable": "state",
        "srv_discovery_url": "https://lingon.ladok.umu.se:8092/",
        #"authenticating_authority": "https://lingon.ladok.umu.se:8092/",
        "scope": ["openid", "email", "profile"],
        "name": "Roland",
        "attribute_map": {
            "displayName": "name",
            "uid": "user_id",
            "email": "email",
            "given_name": "given_name",
            "surname": "family_name"
        }
    },
    "liveid": {
        "saml_endpoint": "liveid_sso",
        "social_endpoint": "liveid",
        "class": LiveIDOAuth2,
        "authenticating_authority": "consent.live.com",
        "token_endpoint": "https://login.live.com/oauth20_token.srf",
        "authorization_endpoint": 'https://login.live.com/oauth20_authorize.srf',
        "userinfo_endpoint": "https://apis.live.net/v5.0/me",
        "name": "LiveID",
        "permissions": ["wl.basic"],
        "attribute_map": {
            "uid": "id",
            #"email": "email",
            #"verified_email": true,
            "displayName": "name",
            "givenName": "first_name",
            "surname": "last_name",
            },
    }
}
