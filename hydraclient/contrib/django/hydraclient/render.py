from rdflib import Namespace, URIRef
from rdflib.term import Identifier
from pyld import jsonld
from django.http import HttpResponse
from .settings import DEFAULT_JSONLD_CONTEXT
from .template import set_graph, set_doc_statement
from hydraclient.core import settings as client_settings
from hydraclient.core.http import best_format_for_accept, SerializerMapping
from django.template.loader import render_to_string



rdf = Namespace(client_settings.DEFAULT_JSONLD_CONTEXT['rdf'])
rdfs = Namespace(client_settings.DEFAULT_JSONLD_CONTEXT['rdfs'])

###===================================================================
### Public
###===================================================================
def render_response(service_resp, doc_uri, user_agent_accept, context_instance=None):
    resp = _requests_response_to_django(service_resp)
    # If the service is a graph, render the object
    if hasattr(service_resp, "graph"):
        _render_graph_response(
            resp,
            service_resp.graph,
            context_instance,
            URIRef(doc_uri),
            user_agent_accept,
        )
    return resp


def render_statement_html(graph, statement, context_instance):
    template_names = list(_statement_to_templates(graph, statement))
    context = set_doc_statement(
        set_graph({}, graph),
        statement,
    )
    return render_to_string(
        template_names,
        context,
        context_instance=context_instance
    )
        

###===================================================================
### Internal 
###===================================================================
def _render_graph_response(resp, graph, context_instance, doc_uri, user_agent_accept):
    mapping = best_format_for_accept(
        user_agent_accept,
        default=SerializerMapping("text/html", "html", "text/html", "html")
    )
    resp['Content-Type'] = mapping.content_type

    if mapping.format == "html":
        # TODO: Use RDFlib's native serializers plugins for django?
        resp.content = render_statement_html(
            graph, 
            (doc_uri, None, None),
            context_instance
        )
    else:
        resp.content = graph.serialize(format=serializer_mapping.format)



def _requests_response_to_django(service_resp):
    resp = HttpResponse(
        service_resp.content,
        status=service_resp.status_code
    )
    for header, value in service_resp.headers.items():
        resp[header] = value
    return resp


def _rdf_types(graph, uri):
    if isinstance(uri, Identifier):
        return [o for (_,_,o) in graph.triples((uri, rdf.type, None))]
    else:
        return [None]


def _statement_to_templates(graph, s):
    qname = graph.namespace_manager.qname
    subject_types = _rdf_types(graph, s[0])
    predicate = s[1]
    object_types = _rdf_types(graph, s[2])
    for subject_type in subject_types:
        for object_type in object_types:
            yield _type_to_template(qname, subject_type, predicate, object_type)
        
        

def _type_to_template(qname, subject_type, predicate, object_type):
    """
    >>> _type_to_template(lambda x: "q:"+x, "subject", "pred", "object")
    'rdf/q:subject/q:pred/q:object.html'

    >>> _type_to_template(lambda x: "q:"+x, "subject", "pred", None)
    'rdf/q:subject/q:pred/rdf:Resource.html'

    >>> _type_to_template(lambda x: "q:"+x, "subject", None, "object")
    'rdf/q:subject/q:object.html'

    >>> _type_to_template(lambda x: "q:"+x, "subject", None, None)
    'rdf/q:subject.html'

    >>> _type_to_template(lambda x: "q:"+x, None, None, None)
    'rdf/rdf:Resource.html'
    """
    if not subject_type:
        subject_qname = "rdf:Resource"
    else:
        subject_qname = qname(subject_type)
    
    if not object_type:
        object_qname = "rdf:Resource"
    else:
        object_qname = qname(object_type)
        
    if predicate:
        bits = [subject_qname, qname(predicate), object_qname]
    elif object_type:
        bits = [subject_qname, object_qname]
    else:
        bits = [subject_qname]
        
    return "rdf/{}.html".format("/".join(bits))
