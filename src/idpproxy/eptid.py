
# # A newer form, more compatible with commercial SAML implementations has the 
# attribute name urn:oid:1.3.6.1.4.1.5923.1.1.1.10 and this new form comprises 
# the entity name of the identity provider, the entity name of the service 
# provider, and the opaque string value. 
# These strings are separated by "!" symbols. This form is advocated by 
# Internet2 and may overtake the other form in due course.

import hashlib
import shelve

import logging

logger = logging.getLogger(__name__)

class Eptid(object):
    def __init__(self, filename, secret):
        self._db = shelve.open(filename, writeback=True)
        self.secret = secret 
        
    def make(self, idp, sp, args):
        md5 = hashlib.md5()
        for arg in args:
            md5.update(arg.encode("utf-8"))
        md5.update(sp)
        md5.update(self.secret)
        md5.digest()
        hashval = md5.hexdigest()
        return "!".join([idp, sp, hashval])
    
    def get(self, idp, sp, args):
        subs = [sp]
        subs.extend(args[1])
        # key is a combination of sp_entity_id and object id
        key = (".".join([sp, args[0]])).encode("utf-8")
        try:
            return self._db[key]
        except KeyError:
            val = self.make(idp, sp, args[1])
            self._db[key] = val
            return val
            
            
