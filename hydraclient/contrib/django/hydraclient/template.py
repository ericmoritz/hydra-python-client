"""
Utility to abstract away how the graph is accessed in the template
"""

_GRAPH_VARNAME = '__hydraclient_graph__'

def get_graph(context):
    return context[_GRAPH_VARNAME]


def set_graph(context, graph):
    context[_GRAPH_VARNAME] = graph
    return context
