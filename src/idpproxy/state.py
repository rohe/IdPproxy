
#!/usr/bin/env python

import hashlib
import uuid
import hmac
import time
import memcache

from Cookie import SimpleCookie
from saml2 import time_util
from saml2 import mcache
from saml2.mcache import ToOld
import logging

logger = logging.getLogger(__name__)

def _expiration(timeout, strformat=None):
    if timeout == "now":
        return time_util.instant(strformat)
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, format=strformat)

class State(object):
    def __init__(self, memcached_servers, name, cookie_str="", secret=""):
        self.name = name
        self.session_cache = mcache.Cache(memcached_servers)
        self.ref_cache = memcache.Client(memcached_servers)
        self._secret = secret
        self.sid = ""
        self.get_id(cookie_str)
        #print "State.sid: %s" % self.sid

    def _sid(self):
        sid = str(uuid.uuid4())
        while True:
            if not self.ref_cache.get(sid):
                break
            sid = str(uuid.uuid4())
        return sid
        
    def __str__(self):
        result = {}
        for session_id in self.get_sessions(): 
            session = Session(self.session_cache, self.sid, session_id)
            result[session_id] = session.active()
        return "%s" % (result,)
        
    def known_session(self, session_id):
        if session_id in self.get_sessions():
            return True
        else:
            return False
    
    def old_session(self, session_id):
        if self.known_session(session_id):
            return self.get_session(session_id)
        
        return None
    
    def session_by_alternate_id(self, aid):
        for session_id in self.get_sessions(): 
            session = Session(self.session_cache, self.sid, session_id)
            if session.sid_digest == aid:
                return session
        
        return None
        
    def get_sessions(self):
        try:
            result = self.ref_cache.get(self.sid)
            if result is None:
                return []
            else:
                return result
        except KeyError:
            return []
        
    def add_session(self, session_id):
        """ This is in reality maintained by mcache 
        
        :param session_id: Is in fact the entity ID of the SP
        :return: A Session instance
        """
        sessions = self.get_sessions()
        if session_id not in sessions:
            sessions.append(session_id)
            self.ref_cache.set(self.sid, sessions)

    def get_session(self, session_id):
        """ Returns an active Session description or a newly constructed.
        
        :param session_id: Is in fact the entity ID of the SP
        :return: A Session instance
        """
        return Session(self.session_cache, self.sid, session_id, self._secret)
    
    def sessions(self):
        """ Iterator of the known sessions """
        for session_id in self.get_sessions(): 
            session = Session(self.session_cache, self.sid, session_id)
            yield session
        
    def any_active(self):
        """ For management purposes. Returns all the active sessions that
        exists for this 'user'.
        
        :returr: True if there is at least one active session, otherwise False
        """
        for session_id in self.get_sessions():
            session = Session(self.session_cache, self.sid, session_id)
            try:
                info = session.get()
                if "authentication" in info and info["authentication"] == "OK":
                    return True
            except ToOld:
                pass
                
        return False
        
    def get_id(self, cookie_str=""):
        if cookie_str:
            #print "-connection by cookie-"
            cookie_obj = SimpleCookie(cookie_str)
            morsel = cookie_obj.get(self.name)
            if morsel is not None:
                self.sid = self.parse_cookie(morsel.value)

        if not self.sid:
            #print "-New connection-"
            self.sid = self._sid()
            
    def cookie(self, expire=0, domain="",  path=""):
        """
        :param expire: Number of minutes before this cookie goes stale
        :param domain: The domain of the cookie
        :param path: The path specification for the cookie
        :return: A tuple to be added to headers
        """
        cookie = SimpleCookie()
        timestamp = str(int(time.time()))
        signature = self.cookie_signature(self.sid, timestamp)
        cookie[self.name] = "|".join([self.sid, timestamp, signature])
        if path:
            cookie[self.name]["path"] = path
        if domain:
            cookie[self.name]["domain"] = domain
        if expire:
            cookie[self.name]["expires"] = \
                _expiration(expire, "%a, %d-%b-%Y %H:%M:%S CET")

        return tuple(cookie.output().split(": ", 1))

    def parse_cookie(self, value):
        """Parses and verifies a cookie value """
        if not value: return None
        parts = value.split("|")
        if len(parts) != 3: return None
        # verify the cookie signature
        if self.cookie_signature(parts[0], parts[1]) != parts[2]:
            raise Exception("Invalid cookie signature %r", value)

        try:
            return parts[0].strip()
        except KeyError:
            return None

    def cookie_signature(self, *parts):
        """Generates a cookie signature.
        """
        sha1 = hmac.new(self._secret, digestmod=hashlib.sha1)
        for part in parts: 
            sha1.update(part)
        return sha1.hexdigest()


def digest(item):
    return hmac.new("1234", item, digestmod=hashlib.sha1).hexdigest()
    
class Session(object):
    """ Knowledge connected to a specific authentication session """
    def __init__(self, cache, group, session_id = "", secret = ""):
        self.group = group
        self._cache = cache
        self._secret = secret
        self.session_id = session_id
        self.sid_digest = digest(session_id)
        
    def cache_identity(self, session_id, identity, until):
        self._cache.update(self.group, session_id, {"ava":identity})
        # not_on_or_after = 
        #   self.server.conf.idp_policy().policy.not_on_or_after()
        self._cache.valid_to(self.group, session_id, until)
    
    def remember(self, info, session_id=""):
        if not session_id:
            session_id = self.session_id

        until = _expiration(30) # half a hour to log in ?!
        self._cache.set(self.group, self.session_id, {"req_info": info}, until)
        return self.session_id

    def __setitem__(self, key, value):
        self._cache.update(self.group, self.session_id, {key: value})

    def __contains__(self, key):
        if key in self._cache.get(self.group, self.session_id):
            return True
        else:
            return False
        
    def get(self, session_id=None):
        """ Will raise an exception if the information is to old. """
        if not session_id:
            session_id = self.session_id
        return self._cache.get(self.group, session_id)

    def __getitem__(self, key):
        try:
            return self._cache.get(self.group, self.session_id)[key]
        except (ValueError, KeyError):
            return None

    def __str__(self):
        return "%s" % self.get()

    def duplicate(self):
        session = Session(self._cache, self.group)
        session.session_id = self.session_id
        return session

    def reset(self):
        self._cache.reset(self.group, self.session_id)

    def valid_to(self, tid):
        """
        :param tid: Number of seconds this information should be valid
        """
        self._cache.valid_to(self.group, self.session_id, tid)

    def keys(self):
        try:
            return self._cache.get(self.group, self.session_id).keys()
        except (ValueError, KeyError):
            return []

    def active(self):
        return self._cache.active(self.group, self.session_id)
    
    def __eq__(self, other):
        if self.group == other.group:
            if self.session_id == other.session_id:
                return True
        return False

    def info(self):
        try:
            return self._cache.get(self.group, self.session_id)["req_info"]
        except (ValueError, KeyError):
            return None
        
    def authn_service(self):
        return self._cache.get(self.group, self.session_id)["service"]