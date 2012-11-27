from saml2 import md
import sys
from saml2.md import EntitiesDescriptor

__author__ = 'rolandh'

xml_str = open(sys.argv[1]).read()

entities_descr = md.entities_descriptor_from_string(xml_str)

keep = sys.argv[2:]
eds = []

for entity_descr in entities_descr.entity_descriptor:
    if entity_descr.entity_id in keep:
        eds.append(entity_descr)

print EntitiesDescriptor(name=entities_descr.name, entity_descriptor=eds,
                         valid_until = entities_descr.valid_until,
                         cache_duration=entities_descr.cache_duration)