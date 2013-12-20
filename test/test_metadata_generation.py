import json
from idpproxy.metadata import secret
from jwkest.jwk import import_rsa_key_from_file
from saml2 import element_to_extension_element
from saml2.config import config_factory
from idpproxy.metadata.secret import MetadataGeneration
from config import idp_proxy_conf
from saml2.extension import mdattr
from idpproxy.utils import MetadataInfo

__author__ = 'roland'


def test():
    # The needed key is the private key, not for encryption but for decryption
    _key = import_rsa_key_from_file("mykey.pem")

    idp_conf = config_factory("idp", "idp_conf")

    generate_metadata = MetadataGeneration(
        idp_proxy_conf.SERVICE, _key, idp_conf,
        idp_conf.xmlsec_path)

    sps = idp_conf.metadata.service_providers()
    qs = {
        "entityId": sps[0],
        "secret": {
            "Google": {
                "key": "lingon",
                "secret": "aaaaa"},
            "Facebook": {
                "key": "hallon",
                "secret": "bbbbb"},
            "Twitter":  {
                "key": "jordgubb",
                "secret": "ccccc"}
        }
    }

    res = generate_metadata.handle_metadata_save({'wsgi.url_scheme': "https",
                                                  'HTTP_HOST': "example.com"},
                                                 None, qs)

    s = res[0].index("<mdattr:EntityAttributes")
    e = res[0].index("</mdattr:EntityAttributes>")

    snippet = res[0][s:e+len("</mdattr:EntityAttributes>")]

    entity_attributes = mdattr.entity_attributes_from_string(snippet)

    entdescr = idp_conf.metadata.metadata["./sp/sp.xml"].entity_descr

    ext = element_to_extension_element(entity_attributes)
    entdescr.spsso_descriptor[0].extensions.extension_elements.append(ext)
    print entity_attributes

    qs = {secret.CONST_BODY: json.dumps({"xml": "%s" % entdescr})}

    generate_metadata.handle_metadata_verify_json({'wsgi.url_scheme':"https",
                                                  'HTTP_HOST': "example.com"},
                                                  None, qs)

if __name__ == "__main__":
    test()