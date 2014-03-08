"""
Generic client library for surfing a linked data web service
"""
from urlparse import urljoin
from rdflib import Graph
import mimetypes
import urllib2
from collections import namedtuple
import requests
import urlparse
import os

from .requests_file_adapter import FileAdapter

session = requests.Session()
session.mount("file://", FileAdapter())


Response = namedtuple("Response", ["status_code", "graph"])

def irl(base_irl, path_info, query_string):
    """
    >>> irl(u"http://example.com/", u"", u"q=test")
    u'http://example.com/?q=test'

    >>> irl(u"http://example.com/", u"foo", u"q=test")
    u'http://example.com/foo?q=test'

    >>> irl(u"http://example.com/", u"/foo", u"q=test")
    u'http://example.com/foo?q=test'

    >>> irl(u"http://example.com/", u"/foo", None)
    u'http://example.com/foo'

    >>> irl(u"http://example.com/", u"/foo", u"")
    u'http://example.com/foo'

    """
    return __add_qs(
        __irljoin(base_irl, path_info),
        query_string
    )


def get(resource_irl, request_irl):
    g = Graph(identifier=request_irl)
    resp = session.get(resource_irl)
    content_type = __content_type(resp)
    if __is_rdf(content_type):
        resp.graph = g.parse(
            data=resp.content,
            format=content_type,
            publicID=request_irl
        )
        return resp
    else:
        return resp
        


###===================================================================
### Internal
###===================================================================
def __content_type(resp):
    return resp.headers.get("Content-Type", "")

def __is_rdf(content_type):
    return content_type in {
        "application/rdf+xml", 
        "text/turtle", 
        "application/ld+json", 
        "application/json"
    }


def __irljoin(base_irl, path_info):
    return urljoin(base_irl, path_info)


def __add_qs(irl, qs):
    if qs and isinstance(qs, basestring):
        return irl + u"?" + qs
    else:
        return irl
