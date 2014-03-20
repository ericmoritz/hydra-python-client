"""
Utility to abstract away how the graph is accessed in the template
"""

_GRAPH_VARNAME = '__hydraclient_graph__'
_DOC_STATEMENT_VARNAME = '__hydraclient_doc_statement__'

def get_graph(context):
    return context[_GRAPH_VARNAME]


def set_graph(context, graph):
    context[_GRAPH_VARNAME] = graph
    return context


def set_doc_statement(context, statement):
    context[_DOC_STATEMENT_VARNAME] = statement
    return context


def get_doc_statement(context):
    return context['_DOC_STATEMENT_VARNAME']
