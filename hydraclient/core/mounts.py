"""
Responsible for finding the correct service base URI for the request URI
"""
from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery


rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
hydra = Namespace("http://www.w3.org/ns/hydra/core#")
wf = Namespace("http://vocab-ld.org/vocabs/web-framework#")


def resolve(graph, request_uri):
    """
    >>> g = __test_graph()
    >>> resolve(g, u"http://example.com/lottery/state-DC")
    rdflib.term.URIRef(u'http://api.example.com/services/lottery/state-DC')

    >>> resolve(g, u"http://example.com/null/state-DC") is None
    True
    """
    matches = (
        (prefix, baseURI)
        for (prefix, _, _) in graph.triples((None, rdf.type, wf.ServiceMount))    
        for (_, _, baseURI) in graph.triples((prefix, hydra.entrypoint, None))
    )
    best_match = None
    for prefix, baseURI in matches:
        is_prefixed = request_uri.startswith(prefix)
        prefix_more_precise = (not best_match) or len(prefix) > len(best_match[0])
        if is_prefixed and prefix_more_precise:
            best_match = (prefix, baseURI)

    if best_match:
        return baseURI + request_uri[len(prefix):]


def __test_graph():
    return Graph().parse(
        data='''
    @prefix web-framework: <http://vocab-ld.org/vocabs/web-framework#> .
    @prefix hydra: <http://www.w3.org/ns/hydra/core#> .

    <lottery/>
       a web-framework:ServiceMount ;
       hydra:entrypoint <http://api.example.com/services/lottery/> .

    ''', format="turtle", publicID="http://example.com/")
