from oictest import OAuth2

__author__ = 'rohe0002'

class LinkedIn(OAuth2):
    def __init__(self, client_id, client_secret, **kwargs):
        OAuth2.__init__(self, client_id, client_secret, **kwargs)
