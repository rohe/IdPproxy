__author__ = 'rohe0002'

import os
import json

from jwkest.jwe import decrypt

from saml2 import extension_elements_to_elements
from saml2.extension import mdattr, idpdisc
from saml2.extension.mdattr import EntityAttributes

import logging
logger = logging.getLogger(__name__)

class Info(object):
    def __init__(self):
        self._ava = {}

    def update(self):
        return

    def get_consumer_key_and_secret(self, social_service, entity_id):
        # Consumer key and secret

        self.update()
        try:
            return 1, self._ava[entity_id][social_service]
        except KeyError:
            return 0, self._ava["DEFAULT"][social_service]

    def __call__(self):
        self.update()

class FileInfo(Info):
    def __init__(self, file=file, **kwargs):
        Info.__init__(self)
        self.file = file
        self._mtime = 0
        # initial load
        self.update()

    def update(self):
        _timestamp = os.path.getmtime(self.file)
        if self._mtime != _timestamp:
            try:
                info = open(self.file).read()
                try:
                    _ava = eval(info)
                    self._ava = _ava
                except Exception, err:
                    logger.error("Could not load consumer info: %s" % err)
            except Exception, err:
                logger.error("Could not read consumer info file: %s" % err)

class MetadataInfo(Info):
    def __init__(self, dkeys, metad, **kwargs):
        Info.__init__(self)
        self.dkeys = dkeys
        self.metad = metad
        metad.post_load_process = self
        self.__call__()

    def __call__(self):
        res = {}

        for ent,item in self.metad.items():
            if "sp_sso" not in item:
                continue

            for sp in item["sp_sso"]:
                if "extensions" not in sp:
                    continue

                elems = extension_elements_to_elements(
                                        sp["extensions"]["extension_elements"],
                                        [mdattr, idpdisc])
                for elem in elems:
                    if isinstance(elem, EntityAttributes):
                        for attr in elem.attribute:
                            if attr.name == "http://swamid.sunet.se/customer":
                                for val in attr.attribute_value:
                                    res[ent] = json.loads(decrypt(val.text,
                                                                  self.dkeys,
                                                                  "private"))

        self._ava.update(res)


class ConsumerInfo(object):
    def __init__(self, spec, **kwargs):
        self._info = []
        for sp in spec:
            if sp.startswith("file:"):
                self._info.append(FileInfo(sp[5:], **kwargs))
            elif sp == "metadata":
                self._info.append(MetadataInfo(**kwargs))

    def __call__(self, social_service, entity_id):
        default = {}
        logger.debug("Consumer info for %s/%s" % (social_service, entity_id))
        for src in self._info:
            try:
                ix, di = src.get_consumer_key_and_secret(social_service,
                                                         entity_id)
                if ix:
                    return di["key"], di["secret"]
                elif not default:
                    default = di
            except KeyError:
                pass

        if default:
            return default["key"], default["secret"]
        else:
            raise KeyError
