from idpproxy.social.openidconnect import OpenIDConnect

__author__ = 'rohe0002'

class PayPal(OpenIDConnect):
    def __init__(self, client_id, client_secret, **kwargs):
        OpenIDConnect.__init__(self, client_id, client_secret, **kwargs)
        self.authn_method = "client_secret_basic"