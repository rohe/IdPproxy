from idpproxy.social.openidconnect import OpenIDConnect

from oic.oauth2.message import Message
from oic.oauth2.message import SINGLE_OPTIONAL_STRING
from oic.oauth2.message import OPTIONAL_LIST_OF_SP_SEP_STRINGS
from oic.oauth2.message import SINGLE_REQUIRED_STRING
from oic.oauth2.message import SINGLE_OPTIONAL_INT

from oic.oic import Client as oic_Client

import logging
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/userinfo.profile",
          "https://www.googleapis.com/auth/userinfo.email"]

# According to an earlier version of OpenID Connect
class GoogleAccessTokenResponse(Message):
    c_param = {
        "access_token": SINGLE_REQUIRED_STRING,
        "expires": SINGLE_OPTIONAL_INT,
        "token_type": SINGLE_REQUIRED_STRING,
        "id_token": SINGLE_OPTIONAL_STRING
    }

# The validation messages also old OIC
class ValidationRequest(Message):
    c_param = {
        "access_token": SINGLE_REQUIRED_STRING,
        }

class ValidationResponse(Message):
    c_param = {
        "audience": SINGLE_REQUIRED_STRING,
        "user_id": SINGLE_REQUIRED_STRING,
        "scope": OPTIONAL_LIST_OF_SP_SEP_STRINGS,
        "expires_in":SINGLE_OPTIONAL_INT
        }

class Client(oic_Client):

    def construct_ValidationRequest(self, request_args=None, extra_args=None,
                                    **kwargs):
        return self.construct_request(ValidationRequest, request_args, extra_args)

class GoogleOIC(OpenIDConnect):
    def __init__(self, client_id, client_secret, **kwargs):
        OpenIDConnect.__init__(self, client_id, client_secret, **kwargs)
        self.access_token_response = GoogleAccessTokenResponse
        self.client_cls = Client
        # default
        #self.flow_type = "code"

    def verify_token(self, client, access_token):
        resp = client.do_any(request=ValidationRequest, method="GET",
                             request_args={"access_token": access_token},
                             endpoint=self.extra["verification_endpoint"],
                             response=ValidationResponse)

        logger.info("Verification result: %s" % resp.to_json())
        return resp.to_dict()

    def get_userinfo(self, client, authresp, access_token):
        return client.do_user_info_request(method="GET",
                                           state=authresp["state"],
                                           schema="openid",
                                           token=access_token,
                                           behavior="use_authorization_header")
