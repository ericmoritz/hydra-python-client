from collections import namedtuple
from rdflib import Namespace, URIRef
from pyld import jsonld
from django.http import HttpResponse
from .settings import DEFAULT_JSONLD_CONTEXT
from hydraclient.core import settings as  client_settings
from django.shortcuts import render_to_response

rdf = Namespace(client_settings.DEFAULT_JSONLD_CONTEXT['rdf'])


def object_types(graph, subject_iri):
    """
    TODO: Add the inheritence ordering...
    """
    return graph.triples( (subject_iri, rdf.type, None) )


def object_templates(graph, object_iri):
    for (object_iri, pred, type_iri) in object_types(graph, object_iri):
        for template in statement_to_templates(graph, (object_iri, pred, type_iri) ):
            yield template


def render(service_resp, object_iri, context_instance=None):
    if hasattr(service_resp, "graph"):
        template_names = object_templates(service_resp.graph, URIRef(object_iri))
        context = {
            '__hydraclient_graph__': service_resp.graph,
            'resource_iri': object_iri
        }

        return render_to_response(
             list(template_names),
            context,
            context_instance=context_instance
        )
    else:
        return HttpResponse(
            service_resp.content,
            content_type=service_resp.headers['Content-Type']
        )

            
def statement_to_templates(graph, statement):
    s,p,o = statement
    for (_, _, subject_type_iri) in object_types(graph, s):
        bits = dict(
            subject_type=rdf_to_template(subject_type_iri),
            pred=rdf_to_template(p),
            obj=rdf_to_template(o),
        )
        yield "rdf/{subject_type}/{pred}/{obj}.html".format(**bits)
        yield "rdf/{pred}/{obj}.html".format(**bits)
    

def rdf_to_template(uriref):
    """
    Converts the full URI to a short URI using a JSON-LD context
    """
    uri = uriref.toPython()
    obj = { 
        "@id": uri,
        "@type": uri,
    }
    compacted = jsonld.compact(obj, DEFAULT_JSONLD_CONTEXT)
    return compacted['@id']


