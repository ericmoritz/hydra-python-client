from rdflib import Namespace, URIRef
from pyld import jsonld
from django.http import HttpResponse
from .settings import DEFAULT_JSONLD_CONTEXT
from hydraclient.core import settings as client_settings
from hydraclient.core.http import best_format_for_accept, SerializerMapping
from django.template.loader import render_to_string


rdf = Namespace(client_settings.DEFAULT_JSONLD_CONTEXT['rdf'])
rdfs = Namespace(client_settings.DEFAULT_JSONLD_CONTEXT['rdfs'])


def object_types(graph, subject_iri):
    """
    TODO: Add the inheritence ordering...
    """
    return list(graph.triples(
        (subject_iri, rdf.type, None)
    )) + [(subject_iri, rdf.type, rdfs.Resource)]


def object_templates(graph, object_iri):
    for (object_iri, pred, type_iri) in object_types(graph, object_iri):
        templates = statement_to_templates(graph, (object_iri, pred, type_iri))
        for template in templates:
            yield template


def render(service_resp, object_iri, user_agent_accept, context_instance=None):
    resp = _requests_response_to_django(service_resp)
    # If the service is a graph, render the object
    if hasattr(service_resp, "graph"):
        render_graph(
            resp,
            service_resp.graph,
            context_instance,
            object_iri,
            user_agent_accept,
        )

    return resp


def render_graph(resp, graph, context_instance, object_iri, user_agent_accept):
    mapping = best_format_for_accept(
        user_agent_accept,
        default=SerializerMapping("text/html", "html", "text/html", "html")
    )
    resp['Content-Type'] = mapping.content_type
    if mapping.format == "html":
        # TODO: Use RDFlib's native serializers plugins for django?
        _render_graph_html(resp, graph, context_instance, object_iri)
    else:
        _render_graph_native(resp, graph, mapping)


def _render_graph_html(resp, graph, context_instance, object_iri):
    template_names = list(object_templates(graph, URIRef(object_iri)))
    if template_names:
        context = {
            '__hydraclient_graph__': graph,
        }
        resp.content = render_to_string(
            template_names,
            context,
            context_instance=context_instance
        )


def _render_graph_native(resp, graph, serializer_mapping):
    resp.content = graph.serialize(format=serializer_mapping.format)


def _requests_response_to_django(service_resp):
    resp = HttpResponse(
        service_resp.content,
        status=service_resp.status_code
    )
    for header, value in service_resp.headers.items():
        resp[header] = value
    return resp


def statement_to_templates(graph, statement):
    s, p, o = statement
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
