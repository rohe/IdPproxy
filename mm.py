#!/usr/bin/env python
import argparse

from saml2.sigver import read_cert_from_file
from saml2.time_util import in_a_while

__author__ = 'rohe0002'

from saml2 import BINDING_HTTP_REDIRECT
from saml2 import samlp
import xmldsig as ds

from saml2.md import SingleSignOnService
from saml2.md import IDPSSODescriptor
from saml2.md import EntitiesDescriptor
from saml2.md import EntityDescriptor
from saml2.md import KeyDescriptor

def do_key_descriptor(cert):
    return KeyDescriptor(
        key_info = ds.KeyInfo(
            x509_data=ds.X509Data(
                x509_certificate=ds.X509Certificate(text=cert)
            )
        )
    )

def entity_desc(loc, key_descriptor=None, eid=None, validity=None, cache=None,
                id=None):
    sso = SingleSignOnService(binding=BINDING_HTTP_REDIRECT, location=loc)
    idp = IDPSSODescriptor(single_sign_on_service=sso,
                           key_descriptor=key_descriptor,
                           want_authn_requests_signed="false",
                           protocol_support_enumeration=samlp.NAMESPACE)
    ei = EntityDescriptor(idpsso_descriptor=idp, entity_id=eid,
                           id=id)

    return ei

def entities_desc(service, ename, base, cert_file=None, validity="", cache="",
                  social=None):
    ed = []
    if cert_file:
        _cert = read_cert_from_file(cert_file, "pem")
        key_descriptor = do_key_descriptor(_cert)
    else:
        key_descriptor = None

    for name, desc in service.items():
        if social is None or name in social:
            loc = "%s/%s" % (base, desc["saml_endpoint"])
            #eid = "%s/%s" % (base, name)
            ed.append(entity_desc(loc, key_descriptor, loc))

    return EntitiesDescriptor(name=ename, entity_descriptor=ed,
                              valid_until = in_a_while(hours=validity),
                              cache_duration=cache)

if __name__ == "__main__":
    from config import idp_proxy_conf as ipc

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest="cnf",
                              help="The idp configuration file")
    parser.add_argument('-v', dest="validity",
                            help="Indicates the expiration time of the metadata",
                            type=int, default=6)
    parser.add_argument('-d', dest="duration",
                        help="Indicates the maximum length of time a consumer should cache the metadata",
                        type=int)
    parser.add_argument("soc", nargs="*", help="Which social services to include")

    args = parser.parse_args()

    cnf = __import__(args.cnf)

    if cnf.BASE.endswith("/"):
        _base = cnf.BASE[:-1]
    else:
        _base = cnf.BASE[:]

    kwargs = {}
    if args.soc:
        kwargs["social"] = args.soc
    if args.duration:
        kwargs["cache"] = args.duration

    ed = entities_desc(ipc.SERVICE, "%s/md/idpproxy-1.0.xml" % _base,
                       _base, cert_file=cnf.CONFIG["cert_file"],
                       validity=args.validity, **kwargs)

    print ed
