__author__ = 'rohe0002'

import os
import json

from jwkest.jwe import decrypt

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
    def __init__(self, fil=file, **kwargs):
        Info.__init__(self)
        self.file = fil
        self._mtime = 0
        # initial load
        self.update()
        self.ava = None

    def update(self):
        _timestamp = os.path.getmtime(self.file)
        if self._mtime != _timestamp:
            try:
                info = open(self.file).read()
                try:
                    self.ava = eval(info)
                except Exception, err:
                    logger.error("Could not load consumer info: %s" % err)
            except Exception, err:
                logger.error("Could not read consumer info file: %s" % err)


ENTITY_ATTR = 'urn:oasis:names:tc:SAML:metadata:attribute&EntityAttributes'
ATTR_NAME = "http://social2saml.nordu.net/customer"


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
            if "spsso_descriptor" not in item:
                continue

            for sp in item["spsso_descriptor"]:
                if "extensions" not in sp:
                    continue

                for elem in sp["extensions"]["extension_elements"]:
                    if elem["__class__"] == ENTITY_ATTR:
                        for attr in elem["attribute"]:
                            if attr["name"] == ATTR_NAME:
                                for val in attr["attribute_value"]:
                                    try:
                                        socialsecrets = json.loads(decrypt(val["text"],
                                                                           self.dkeys))
                                        if "entityId" in socialsecrets and ent in socialsecrets["entityId"]:
                                            if "secret" in socialsecrets:
                                                res[ent] = socialsecrets["secret"]
                                    except Exception as exp:
                                        logger.warning('The secrets in the metadata cannot med used for the sp: ' + ent,
                                                       exc_info=True)
        self._ava.update(res)


class ConsumerInfo(object):
    def __init__(self, spec, **kwargs):
        self.info = []
        for sp in spec:
            if sp.startswith("file:"):
                self.info.append(FileInfo(sp[5:], **kwargs))
            elif sp == "metadata":
                self.info.append(MetadataInfo(**kwargs))

    def __call__(self, social_service, entity_id):
        default = {}
        logger.debug("Consumer info for %s/%s" % (social_service, entity_id))
        for src in self.info:
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
