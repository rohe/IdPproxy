#!/usr/bin/env python

__author__ = 'rohe0002'

import sys

from saml2.extension import mdattr
from saml2.saml import Attribute
from saml2.saml import AttributeValue

consumer = sys.stdin.read()

val = AttributeValue()
val.set_text(consumer)

attr = Attribute(name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                 name="http://social2saml.nordu.net/customer",
                 attribute_value=[val])

eattr = mdattr.EntityAttributes(attribute=[attr])

nspair = {
    "mdattr": "urn:oasis:names:tc:SAML:metadata:attribute",
    "samla":"urn:oasis:names:tc:SAML:2.0:assertion"
}
print eattr.to_string(nspair)