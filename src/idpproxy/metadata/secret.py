import cgi
import re
import os
import xmldsig
import xmlenc
import logging
import uuid
import json
from idpproxy import utils
from saml2.httputil import Response, NotFound
from urlparse import parse_qs
from mako.lookup import TemplateLookup
from jwkest.jwe import RSAEncrypter
from saml2.extension import mdattr
from saml2.saml import Attribute, NAME_FORMAT_URI
from saml2.saml import AttributeValue
from saml2.mdstore import MetadataStore
from saml2.mdstore import MetaData
from saml2 import attribute_converter
from saml2 import saml
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import ui
from saml2 import md

# The class is responsible for taking care of all requests for generating SP
# metadata for the social services used by the IdPproxy.

_log = logging.getLogger(__name__)

#Body
CONST_BODY = "body"+uuid.uuid4().urn
#JSON
CONST_TYPEJSON = "application/json"
#Base directory for this class.
CONST_BASE = os.path.dirname(os.path.abspath(__file__))
#Directory containing all static files.
CONST_STATIC_FILE = CONST_BASE + "/files/static/"
#Directory containing all mako files.
CONST_STATIC_MAKO = CONST_BASE + "/files/mako/"

#Start path - accessed directly by user.
CONST_METADATA = "/metadata"
# Path to show the generated metadata.
# Next step from the CONST_METADATA path.
CONST_METADATASAVE = "/metadata/save"
# Next step from the CONST_METADATASAVE path.
CONST_METADATAVERIFY = "/metadata/verify"
# Next step from the CONST_METADATAVERIFY1 path.
CONST_METADATAVERIFYJSON = "/metadata/verifyjson"

#Static html file shown when a user tries to access an unknown path under
# the CONST_METDATA path.
CONST_UNKNOWFILE = CONST_STATIC_FILE + "unknown.html"
#Static hthml file that is presented to the user if an unknown error occurs.
CONST_UNKNOWERROR = CONST_STATIC_FILE + "unknownError.html"

#Padding used for the PKCS1 encryption
CONST_PADDING = "pkcs1_oaep_padding"

#Needed for reading metadatafiles.
CONST_ONTS = {
    saml.NAMESPACE: saml,
    mdui.NAMESPACE: mdui,
    mdattr.NAMESPACE: mdattr,
    dri.NAMESPACE: dri,
    ui.NAMESPACE: ui,
    idpdisc.NAMESPACE: idpdisc,
    md.NAMESPACE: md,
    xmldsig.NAMESPACE: xmldsig,
    xmlenc.NAMESPACE: xmlenc
}
#Needed for reading metadatafiles.
CONST_ATTRCONV = attribute_converter.ac_factory("attributemaps")


class MetadataGeneration(object):

    def __init__(self, logger, conf, key, metadata_list, idp_conf, xmlsec_path):
        """
        Constructor.
        Initiates the class.
        :param logger: Logger to be used when something needs to be logged.
        :param conf: Specific metadata conf
        :param key: A RSA key to be used for encryption.
        :param metadata_list: A list of metadata files.
            like this: [{"local": ["swamid-1.0.xml"]}, {"local": ["sp.xml"]}]
        :param idp_conf: idp_conf see IdpProxy/idp_conf.example.py
        :param xmlsec_path:
        :raise:
        """
        if (logger is None) or (conf is None) or (key is None):
            raise ValueError(
                "A new instance must include a value for logger, conf and key.")
        #Key to be used for encryption.
        self.key = key
        #Used for presentation of mako files.
        self.lookup = TemplateLookup(
            directories=[CONST_STATIC_MAKO + 'templates',
                         CONST_STATIC_MAKO + 'htdocs'],
            module_directory='modules',
            input_encoding='utf-8',
            output_encoding='utf-8')
        #The logger.
        self.logger = logger
        #A list of all social services used by this IdPproxy.
        self.social_service_key_list = []
        #A list of all service providers used by this sp.
        self.sp_key_list = []
        for key in conf:
            self.social_service_key_list.append(conf[key]["name"])

        for metadata in metadata_list:
            mds = MetadataStore(CONST_ONTS.values(),
                                CONST_ATTRCONV, idp_conf,
                                disable_ssl_certificate_validation=True)
            mds.imp(metadata)
            for entityId in mds.keys():
                self.sp_key_list.append(entityId)

        self.xmlsec_path = xmlsec_path

    @staticmethod
    def verify_handle_request(path):
        """
        Verifies if the given path should be handled by this class.
        :param path: A path.
        :return: True if the path should be handled by this class, otherwise
            false.
        """
        return re.match(CONST_METADATA + ".*", path)

    @staticmethod
    def get_query_dict(environ):
        """
        Retrieves a dictionary with query parameters.
        :param environ: The wsgi enviroment.
        :return: A dictionary with query parameters.
        """
        qs = {}
        query = environ.get("QUERY_STRING", "")
        if not query:
            post_env = environ.copy()
            post_env['QUERY_STRING'] = ''
            query = cgi.FieldStorage(fp=environ['wsgi.input'], environ=post_env,
                                     keep_blank_values=True)
            if query is not None:
                try:
                    for item in query:
                        qs[query[item].name] = query[item].value
                except:
                    qs[CONST_BODY] = query.file.read()

        else:
            qs = dict((k, v if len(v) > 1 else v[0]) for k, v in
                      parse_qs(query).iteritems())

        return qs

    def handle_request(self, environ, start_response, path):
        """
        Call this method from the wsgi application.
        Handles the request if the path i matched by verify_handle_request
        and any static file or CONST_METADATA or CONST_METADATASAVE.

        :param environ: wsgi enviroment
        :param start_response: the start response
        :param path: the requested path
        :return: a response fitted for wsgi application.
        """
        try:
            if path == CONST_METADATA:
                return self.handle_metadata(environ, start_response)
            elif path == CONST_METADATAVERIFY:
                return self.handle_metadata_verify(environ, start_response)
            elif path == CONST_METADATAVERIFYJSON:
                return self.handle_metadata_verify_json(
                    environ, start_response, self.get_query_dict(environ))
            elif path == CONST_METADATASAVE:
                return self.handle_metadata_save(environ, start_response,
                                                 self.get_query_dict(environ))
            else:
                filename = CONST_STATIC_FILE + self.get_static_file_name(path)
                if self.verify_static(filename):
                    return self.handle_static(environ, start_response, filename)
                else:
                    return self.handle_static(environ, start_response,
                                              CONST_UNKNOWFILE)
        except Exception:
            self.logger.fatal('Unknown error in handle_request.', exc_info=True)
            return self.handle_static(environ, start_response,
                                      CONST_UNKNOWERROR)

    def get_static_file_name(self, path):
        """
        Parses out the static file name from the path.
        :param path: The requested path.
        :return: The static file name.
        """
        if self.verify_handle_request(path):
            try:
                return path[len(CONST_METADATA) + 1:]
            except:
                pass
        return ""

    @staticmethod
    def verify_static(filename):
        """
        Verifies if a static file exists in the folder
        IdPproxy/src/idpproxy/metadata/files/static

        :param filename: The name of the file.
        :return: True if the file exists, otherwise false.
        """
        try:
            with open(filename):
                pass
        except IOError:
            return False
        return True

    def handle_metadata(self, environ, start_response):
        """
        Creates the response for the first page in the metadata generation.
        :param environ: wsgi enviroment
        :param start_response: wsgi start respons
        :return: wsgi response for the mako file metadata.mako.
        """
        resp = Response(mako_template="metadata.mako",
                        template_lookup=self.lookup, headers=[])

        argv = {
            "action": CONST_METADATASAVE,
            "sociallist": sorted(self.social_service_key_list),
            "spKeyList": sorted(self.sp_key_list),
            "verify": CONST_METADATAVERIFY,
        }
        return resp(environ, start_response, **argv)

    def handle_metadata_save(self, environ, start_response, qs):
        """
        Takes the input for the page metadata.mako.
        Encrypts entity id and secret information for the social services.
        Creates the partial xml to be added to the metadata for the service
        provider.
        :param environ: wsgi enviroment
        :param start_response: wsgi start respons
        :param qs: Query parameters in a dictionary.
        :return: wsgi response for the mako file metadatasave.mako.
        """
        resp = Response(mako_template="metadatasave.mako",
                        template_lookup=self.lookup,
                        headers=[])
        if "entityId" not in qs or "secret" not in qs:
            xml = ("Xml could not be generated because no entityId or secret"
                   "has been sent to the service.")
            self.logger.warning(xml)
        else:
            try:
                secret_data = '{"entityId": %s, "secret": %s}' % (
                    qs["entityId"], qs["secret"])
                encrypter = RSAEncrypter()
                secret_data_encrypted = encrypter.encrypt(secret_data, self.key,
                                                          CONST_PADDING)
                val = AttributeValue()
                val.set_text(secret_data_encrypted)
                attr = Attribute(
                    name_format=NAME_FORMAT_URI,
                    name="http://social2saml.nordu.net/customer",
                    attribute_value=[val])
                eattr = mdattr.EntityAttributes(attribute=[attr])
                nspair = {
                    "mdattr": "urn:oasis:names:tc:SAML:metadata:attribute",
                    "samla": "urn:oasis:names:tc:SAML:2.0:assertion"
                }
                xml = eattr.to_string(nspair)
                xml_list = xml.split("\n", 1)

                if len(xml_list) == 2:
                    xml = xml_list[1]

            except Exception:
                self.logger.fatal('Unknown error in handle_metadata_save.',
                                  exc_info=True)
                xml = "Xml could not be generated."
        argv = {
            "home": CONST_METADATA,
            "action": CONST_METADATAVERIFY,
            "xml": xml
        }
        return resp(environ, start_response, **argv)

    def handle_metadata_verify(self, environ, start_response):
        """
        Will show the page for metadata verification (metadataverify.mako).
        :param environ: wsgi enviroment
        :param start_response: wsgi start respons
        :return: wsgi response for the mako file metadatasave.mako.
        """
        resp = Response(mako_template="metadataverify.mako",
                        template_lookup=self.lookup,
                        headers=[])
        argv = {
            "home": CONST_METADATA,
            "action": CONST_METADATAVERIFYJSON
        }
        return resp(environ, start_response, **argv)

    def handle_metadata_verify_json(self, environ, start_response, qs):
        """
        Handles JSON metadata verifications.
        The post body must contains a JSON message like
        { 'xml' : 'a metadata file'}

        :param environ: wsgi enviroment
        :param start_response: wsgi start respons
        :param qs: Query parameters in a dictionary.
        :return: wsgi response contaning a JSON response. The JSON message will
            contain the parameter ok and services.
            ok will contain true if the metadata file can be parsed, otherwise
            false.
            services will contain a list of all the service names contained in
            the metadata file.
        """
        ok = False
        services = "[]"
        try:
            if CONST_BODY in qs:
                json_message = json.loads(qs[CONST_BODY])
                if "xml" in json_message:
                    xml = json_message["xml"]
                    xml = xml.strip()
                    metadata_ok = False
                    ci = None
                    try:
                        mds = MetadataStore(
                            CONST_ONTS.values(), CONST_ATTRCONV,
                            self.xmlsec_path,
                            disable_ssl_certificate_validation=True)

                        _md = MetaData(CONST_ONTS.values(), CONST_ATTRCONV,
                                      metadata=xml)
                        _md.load()
                        entity_id = _md.entity.keys()[0]
                        mds.metadata[entity_id] = _md
                        args = {"metad": mds, "dkeys": {"rsa": [self.key]}}
                        ci = utils.ConsumerInfo(['metadata'], **args)
                        metadata_ok = True
                    except:
                        self.logger.info(
                            'Could not parse the metadata file in handleMetadataVerifyJSON.',
                            exc_info=True)
                    services = "["
                    first = True
                    if ci is not None:
                        for item in ci.info:
                            if item.ava is not None and entity_id in item.ava:
                                for social in item.ava[entity_id]:
                                    if not first:
                                        services += ","
                                    else:
                                        first = False
                                    services += '"' + social + '"'
                    services += "]"
                    if metadata_ok:
                        ok = True
        except:
            self.logger.fatal('Unknown error in handleMetadataVerifyJSON.',
                              exc_info=True)
        resp = Response('{"ok":"' + str(ok) + '", "services":' + services + '}',
                        headers=[('Content-Type', CONST_TYPEJSON)])
        return resp(environ, start_response)

    @staticmethod
    def handle_static(environ, start_response, path):
        """
        Creates a response for a static file.
        :param environ: wsgi enviroment
        :param start_response: wsgi start response
        :param path: the static file and path to the file.
        :return: wsgi response for the static file.
        """
        try:
            text = open(path).read()
            if path.endswith(".ico"):
                resp = Response(text,
                                headers=[('Content-Type', "image/x-icon")])
            elif path.endswith(".html"):
                resp = Response(text, headers=[('Content-Type', 'text/html')])
            elif path.endswith(".txt"):
                resp = Response(text, headers=[('Content-Type', 'text/plain')])
            elif path.endswith(".css"):
                resp = Response(text, headers=[('Content-Type', 'text/css')])
            else:
                resp = Response(text, headers=[('Content-Type', 'text/xml')])
        except IOError:
            resp = NotFound()
        return resp(environ, start_response)