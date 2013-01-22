import urlparse

__author__ = 'rolandh'


def eppn_from_link(link):
    # link = 'http://www.facebook.com/johan.lundberg.908'

    p = urlparse.urlparse(link)

    return "%s@%s" % (p.path[1:], p.netloc)


print eppn_from_link('http://www.facebook.com/johan.lundberg.908')