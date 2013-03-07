#!/usr/bin/env python
from Cookie import SimpleCookie
import hashlib
import hmac

import shelve
import logging
import uuid
import time
from oic.utils import time_util

logger = logging.getLogger(__name__)

def _expiration(timeout, strformat=None):
    if timeout == "now":
        return time_util.instant(strformat)
    else:
        # validity time should match lifetime of assertions
        return time_util.in_a_while(minutes=timeout, time_format=strformat)

class Cache(object):
    def __init__(self, name="", secret="", filename=None):
        self._secret = secret
        self.name = name
        if filename:
            self._db = shelve.open(filename, writeback=True)
            self._sync = True
        else:
            self._db = {}
            self.alt_id = {}
            self._sync = False

    def sid(self):
        sid = str(uuid.uuid4())
        while True:
            if sid not in self._db:
                break
            sid = str(uuid.uuid4())
        return sid

    def __delitem__(self, key):
        del self._db[key]

        if self._sync:
            self._db.sync()

    def __setitem__(self, key, value):
        self._db[key] = value
        if self._sync:
            self._db.sync()

    def set(self, key, value):
        self[key] = value

    def __getitem__(self, item):
        return self._db[item]

    def keys(self):
        return self._db.keys()

    def __contains__(self, sid):
        return sid in self._db

    def known_as(self, kaka):
        logger.info("KAKA: %s" % kaka)
        sid = self.get_id(kaka)
        if sid in self._db:
            return sid
        else:
            return None

    def alternate_sid(self, sid, aid):
        self.alt_id[aid] = sid

# =============================================================================

    def cookie_signature(self, *parts):
        """Generates a cookie signature.
        """
        sha1 = hmac.new(self._secret, digestmod=hashlib.sha1)
        for part in parts:
            sha1.update(part)
        return sha1.hexdigest()

    def get_id(self, cookie_str):
        """

        :param cookie_str:
        :return:
        """
        cookie_obj = SimpleCookie(cookie_str)
        morsel = cookie_obj.get(self.name)
        if morsel is not None:
            return self.parse_cookie(morsel.value)
        return None

    def create_cookie(self, sid, expire=0, domain="",  path=""):
        """
        Create Cookies

        :param expire: Number of minutes before this cookie goes stale
        :param domain: The domain of the cookie
        :param path: The path specification for the cookie
        :return: A tuple to be added to headers
        """
        cookie = SimpleCookie()
        timestamp = str(int(time.time()))
        signature = self.cookie_signature(sid, timestamp)
        cookie[self.name] = "|".join([sid, timestamp, signature])
        if path:
            cookie[self.name]["path"] = path
        if domain:
            cookie[self.name]["domain"] = domain
        if expire:
            cookie[self.name]["expires"] =\
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

    def digest(self, item):
        return hmac.new(self._secret, item, digestmod=hashlib.sha1).hexdigest()

