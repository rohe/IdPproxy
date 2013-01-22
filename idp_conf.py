from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_REDIRECT
from saml2.saml import NAME_FORMAT_URI

__author__ = 'rolandh'

#BASE = "http://localhost:8091/"
#BASE = "http://lingon.catalogix.se:8091/"
BASE = "http://lingon.ladok.umu.se:8091/"

CONFIG = {
    "entityid" : BASE+"idp",
    "service": {
        "idp": {
            "name" : "SAML proxy IdP",
            "endpoints" : {
                "single_sign_on_service" : [(BASE, BINDING_HTTP_REDIRECT)],
                "single_logout_service" : [(BASE+"logout", BINDING_SOAP)],
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes": 240},
                    "attribute_restrictions": None, # means all I have
                    "name_form": NAME_FORMAT_URI
                },
            },
            "subject_data": "./idp.subject.db",
        }
    },
    "debug" : 1,
    "key_file" : "pki/mykey.pem",
    "cert_file" : "pki/mycert.pem",
    "xmlsec_binary" : "/opt/local/bin/xmlsec1",
    "metadata" : {
        "local": ["test/sp/sp.xml"],
    },
    "organization": {
        "display_name": "Rolands Social proxy",
        "name": "Rolands Social proxy",
        "url":"http://www.example.com/roland",
    },
    # This database holds the map between a subjects local identifier and
    # the identifier returned to a SP
    "attribute_map_dir" : "./attributemaps",
    "secret": "1234567890",
    "logger": {
        "rotating": {
            "filename": "idp_proxy.log",
            "maxBytes": 100000,
            "backupCount": 5,
        },
        "loglevel": "debug",
        #"format": "%(asctime)s %(name)s:%(func)s %(levelname)s %(message)s",
        "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
    }
}
