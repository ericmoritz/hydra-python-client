from webob.acceptparse import Accept
from collections import namedtuple


SerializerMapping = namedtuple(
    "SerializerMapping",
    ["offer", "format", "content_type", "extension"]
)

ParserMapping = namedtuple(
    "ParserMapping",
    ["accept", "format", "extension"]
)


# TODO use the rdf serializer plugins to build this list
SERIALIZER_MAP = [
    SerializerMapping("text/turtle", "turtle", 'text/turtle', "ttl"),
    SerializerMapping("application/rdf+xml", "xml", 'application/rdf+xml', 'rdf'),
    SerializerMapping("application/xml", "xml", 'application/rdf+xml', 'rdf'),
    SerializerMapping("application/ld+json", "json-ld", 'application/ld+json', 'jsonld'),
    SerializerMapping("application/json", "json-ld", 'application/json', 'json'),
    SerializerMapping("text/html", "html", "text/html", 'html'),
]


# TODO use rdf parser plugins to build this list
CLIENT_ACCEPTS = [
    ParserMapping("text/turtle", "turtle", "ttl"),
    ParserMapping("application/rdf+xml", "xml", "rdf"),
    ParserMapping("application/rdf+xml", "xml", "rdf.xml"),
    ParserMapping("application/ld+json", "json-ld", "jsonld"),
    ParserMapping("application/json", "json-ld", "json"),
    ParserMapping("text/html", "html", "html"),
]


def guess_serializer(ext):
    """
    Guess type from URL
    """
    for mapping in SERIALIZER_MAP:
        if mapping.extension == ext:
            return mapping


def best_parser_for_content_type(content_type):
    for mapping in CLIENT_ACCEPTS:
        if mapping.accept == content_type:
            return mapping


def best_format_for_accept(accept,
                           default=SerializerMapping(None, None, None, None)):
    """
    Returns the best rdf format for the accepted format

    # TODO use rdflib's serializer plugins to figure this out

    >>> best_format_for_accept("text/html, text/turtle") == (
    ... SerializerMapping('text/turtle', 'turtle','text/turtle', 'ttl')
    ... )
    True

    >>> best_format_for_accept("text/turtle") == (
    ... SerializerMapping('text/turtle', 'turtle','text/turtle', 'ttl')
    ... )
    True

    """
    offers = [mapping.offer for mapping in SERIALIZER_MAP]
    best = Accept(accept).best_match(offers)
    for mapping in SERIALIZER_MAP:
        if mapping.offer == best:
            return mapping
    return default


def accepted():
    """
    Returns a list of content-types that is supported the installed
    rdflib as a accept header.

    # TODO use rdflib's parser plugins to figure this out

    """
    return "text/turtle, application/ld+json, application/rdf+xml"
