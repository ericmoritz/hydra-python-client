"""
Generic client library for surfing a linked data web service
"""
from urlparse import urljoin
from rdflib import Graph
from collections import namedtuple
from webob.acceptparse import Accept
from .http import accepted
import mimetypes

# Make sure that mimetypes supports the RDF extensions
mimetypes.add_type("application/ld+json", ".jsonld")
mimetypes.add_type("application/rdf+xml", ".rdf")
mimetypes.add_type("text/turtle", ".ttl")

from .requests_file_adapter import FileAdapter


Response = namedtuple("Response", ["status_code", "graph"])


def get(session, resource_irl, request_irl):
    if not isinstance(session.adapters.get("file://"), FileAdapter):
        session.mount("file://", FileAdapter())

    g = Graph(identifier=request_irl)
    accept = accepted()
    resp = session.get(
        resource_irl,
        headers={"Accept": accept}
    )
    content_type = __content_type(resp)
    # If we can use this as a graph, parse it.
    if __is_acceptable_graph(accept, content_type):
        resp.graph = g.parse(
            data=resp.content,
            format=content_type,
            publicID=request_irl
        )
        return resp
    else:
        return resp


def add_qs(irl, qs):
    """
    >>> add_qs(u"http://example.com/", u"q=test")
    u'http://example.com/?q=test'

    >>> add_qs(u"http://example.com/foo", u"q=test")
    u'http://example.com/foo?q=test'

    >>> add_qs(u"http://example.com/foo", None)
    u'http://example.com/foo'

    >>> add_qs(u"http://example.com/foo", u"")
    u'http://example.com/foo'
    """

    if qs and isinstance(qs, basestring):
        return irl + u"?" + qs
    else:
        return irl


def irljoin(base_irl, path_info):
    return urljoin(base_irl, path_info)


###===================================================================
### Internal
###===================================================================
def __content_type(resp):
    return resp.headers.get("Content-Type", "")


def __is_acceptable_graph(accepted, content_type):
    return Accept(accepted).best_match([content_type]) is not None
