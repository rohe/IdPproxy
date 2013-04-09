__author__ = 'Hans Hoerberg - Copyright 2013 Umea Universitet'
import re
import os
import xmldsig
import xmlenc
from saml2.httputil import Response, NotFound
from urlparse import parse_qs
from mako.lookup import TemplateLookup
from jwkest.jwe import encrypt
from jwkest.jwk import rsa_pub_load
from saml2.extension import mdattr
from saml2.saml import Attribute
from saml2.saml import AttributeValue
from saml2.mdstore import MetadataStore
from saml2.sigver import get_xmlsec_binary
from saml2 import attribute_converter
from saml2 import saml
from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import ui
from saml2 import md

"""
The class is responsible for taking care of all requests for generating SP metadata for the social services used by
the IdPproxy.
"""
class MetadataGeneration(object):
    #Base directory for this class.
    CONST_BASE = os.path.dirname(os.path.abspath(__file__))
    #Directory containing all static files.
    CONST_STATIC_FILE = CONST_BASE + "/files/static/"
    #Directory containing all mako files.
    CONST_STATIC_MAKO = CONST_BASE + "/files/mako/"

    #Start path - accessed directly by user.
    CONST_METADATA = "/metadata"
    #Path to show the generated metadata. Next step from the CONST_METADATA path.
    CONST_METADATASAVE = "/metadata/save"

    #Static html file shown when a user tries to access an unknown path under the CONST_METDATA path.
    CONST_UNKNOWFILE = CONST_STATIC_FILE + "unknown.html"
    #Static hthml file that is presented to the user if an unknown error occurs.
    CONST_UNKNOWERROR = CONST_STATIC_FILE + "unknownError.html"

    #Algoritm used to encrypt social service secret and key.
    CONST_ALG = "RSA-OAEP"
    #Encryption method used to encrypt social service secret and key.
    CONST_ENCRYPT = "A256GCM"

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

    def __init__(self, logger, conf, keyFile, metadataList):
        """
        Constructor.
        Initiates the class.
        :param logger: Logger to be used when something needs to be logged.
        :param conf: idp_proxy_conf see IdpProxy/conig/idp_proxy_conf.example.py
        :param keyFile: The public key to be used for encryption.
        :param metadataList: A list of metadata files. [{"local": ["swamid-1.0.xml"]}, {"local": ["sp.xml"]}]
        :raise:
        """
        if (logger is None) or (conf is None) or (keyFile is None):
            raise ValueError("A new instance must include a value for logger, conf and publicKeyFile.")
        #Public key to be used for encryption.
        self.key = rsa_pub_load(keyFile)
        #Used for presentation of mako files.
        self.lookup = TemplateLookup(directories=[MetadataGeneration.CONST_STATIC_MAKO + 'templates',
                                                  MetadataGeneration.CONST_STATIC_MAKO + 'htdocs'],
                                     module_directory=MetadataGeneration.CONST_STATIC_MAKO + 'modules',
                                     input_encoding='utf-8',
                                     output_encoding='utf-8')
        #The logger.
        self.logger = logger
        #A list of all social services used by this IdPproxy.
        self.socialServiceKeyList = []
        #A list of all service providers used by this sp.
        self.spKeyList = []
        for key in conf:
            self.socialServiceKeyList.append(conf[key]["name"])

        try:
            xmlsec_path = get_xmlsec_binary(["/opt/local/bin"])
        except:
            try:
                xmlsec_path = get_xmlsec_binary(["/usr/local/bin"])
            except:
                self.logger.info('Xmlsec must be installed! Tries /usr/bin/xmlsec1.')
                xmlsec_path = '/usr/bin/xmlsec1'

        for metadata in metadataList:
            mds = MetadataStore(MetadataGeneration.CONST_ONTS.values(), MetadataGeneration.CONST_ATTRCONV, xmlsec_path,
                                disable_ssl_certificate_validation=True)
            mds.imp(metadata)
            for entityId in mds.keys():
                self.spKeyList.append(entityId)

    def verifyHandleRequest(self, path):
        """
        Verifies if the given path should be handled by this class.
        :param path: A path.
        :return: True if the path should be handled by this class, otherwise false.
        """
        return re.match(MetadataGeneration.CONST_METADATA + ".*", path)

    def getQueryDict(self, environ):
        """
        Retrieves a dictionary with query parameters.
        :param environ: The wsgi enviroment.
        :return: A dictionary with query parameters.
        """
        query = environ.get('s2repoze.body', ' ')
        if not query:
            query = environ.get("QUERY_STRING", "")
        qs = dict((k, v if len(v) > 1 else v[0]) for k, v in parse_qs(query).iteritems())
        return qs

    def handleRequest(self, environ, start_response, path):
        """
        Call this method from the wsgi application.
        Handles the request if the path i matched by verifyHandleRequest and any static file or
        CONST_METADATA or CONST_METADATASAVE.
        :param environ: wsgi enviroment
        :param start_response: the start response
        :param path: the requested path
        :return: a response fitted for wsgi application.
        """
        try:
            if path == MetadataGeneration.CONST_METADATA:
                return self.handleMetadata(environ, start_response)
            elif path == MetadataGeneration.CONST_METADATASAVE:
                return self.handleMetadataSave(environ, start_response, self.getQueryDict(environ))
            else:
                filename = self.CONST_STATIC_FILE + self.getStaticFileName(path)
                if self.verifyStatic(filename):
                    return self.handleStatic(environ, start_response, filename)
                else:
                    return self.handleStatic(environ, start_response, MetadataGeneration.CONST_UNKNOWFILE)
        except Exception as e:
            self.logger.fatal('Unknown error in handleRequest.', exc_info=True)
            return self.handleStatic(environ, start_response, MetadataGeneration.CONST_UNKNOWERROR)

    def getStaticFileName(self, path):
        """
        Parses out the static file name from the path.
        :param path: The requested path.
        :return: The static file name.
        """
        if self.verifyHandleRequest(path):
            try:
                return path[len(MetadataGeneration.CONST_METADATA) + 1:]
            except:
                pass
        return ""

    def verifyStatic(self, filename):
        """
        Verifies if a static file exists in the folder IdPproxy/src/idpproxy/metadata/files/static
        :param filename: The name of the file.
        :return: True if the file exists, otherwise false.
        """
        try:
            with open(filename):
                pass
        except IOError:
            return False
        return True

    def handleMetadata(self, environ, start_response):
        """
        Creates the response for the first page in the metadata generation.
        :param environ: wsgi enviroment
        :param start_response: wsgi start respons
        :return: wsgi response for the mako file metadata.mako.
        """
        resp = Response(mako_template="metadata.mako", template_lookup=self.lookup,
                        headers=[])

        argv = {
            "action": MetadataGeneration.CONST_METADATASAVE,
            "sociallist": sorted(self.socialServiceKeyList),
            "spKeyList": sorted(self.spKeyList)
        }
        return resp(environ, start_response, **argv)

    def handleMetadataSave(self, environ, start_response, qs):
        """
        Takes the input for the page metadata.mako.
        Encrypts entity id and secret information for the social services.
        Creates the partial xml to be added to the metadata for the service provider.
        :param environ: wsgi enviroment
        :param start_response: wsgi start respons
        :param qs: Query parameters in a dictionary.
        :return: wsgi response for the mako file metadatasave.mako.
        """
        resp = Response(mako_template="metadatasave.mako", template_lookup=self.lookup,
                        headers=[])
        if "entityId" not in qs or "secret" not in qs:
            xml = "Xml could not be generated because no entityId or secret has been sent to the service."
            self.logger.warning(xml)
        else:
            try:
                secretData = '{"entityId": ' + qs["entityId"] + ', "secret":' + qs["secret"] + '}'
                secretDataEncrypted = encrypt(
                    secretData,
                    {"rsa": [self.key]},
                    MetadataGeneration.CONST_ALG,
                    MetadataGeneration.CONST_ENCRYPT,
                    "public",
                    debug=False)
                val = AttributeValue()
                val.set_text(secretDataEncrypted)
                attr = Attribute(name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
                                 name="http://social2saml.nordu.net/customer",
                                 attribute_value=[val])
                eattr = mdattr.EntityAttributes(attribute=[attr])
                nspair = {
                    "mdattr": "urn:oasis:names:tc:SAML:metadata:attribute",
                    "samla": "urn:oasis:names:tc:SAML:2.0:assertion"
                }
                xml = eattr.to_string(nspair)
            except Exception as exp:
                self.logger.fatal('Unknown error in handleMetadataSave.', exc_info=True)
                xml = "Xml could not be generated."
        argv = {
            "home": MetadataGeneration.CONST_METADATA,
            "xml": xml
        }
        return resp(environ, start_response, **argv)

    def handleStatic(self, environ, start_response, path):
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
                resp = Response(text, headers=[('Content-Type', "image/x-icon")])
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