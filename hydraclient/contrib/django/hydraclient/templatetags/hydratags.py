from django import template
from django.template.base import TagHelperNode, parse_bits
from inspect import getargspec

# TODO use a namedtuple for the sparql result

register = template.Library()


def assignment_tag_with_cdata(library, func=None, takes_context=None,

                              name=None):
    def dec(func):
        params, varargs, varkw, defaults = getargspec(func)

        class AssignmentNode(TagHelperNode):
            def __init__(self, nodelist, takes_context, args,
                         kwargs, target_var):
                super(AssignmentNode, self).__init__(
                    takes_context,
                    args,
                    kwargs
                )
                self.nodelist = nodelist
                self.target_var = target_var

            def render(self, context):
                resolved_args, resolved_kwargs = self.get_resolved_arguments(
                    context
                )
                resolved_kwargs['cdata'] = self.nodelist.render(context)
                context[self.target_var] = func(
                    *resolved_args,
                    **resolved_kwargs
                )
                return ''

        function_name = (
            name or
            getattr(func, '_decorated_function', func).__name__
        )

        end_name = "end{0}".format(function_name)

        def compile_func(parser, token):
            bits = token.split_contents()[1:]
            if len(bits) < 2 or bits[-2] != 'as':
                raise template.TemplateSyntaxError(
                    "'%s' tag takes at least 2 arguments and the "
                    "second last argument must be 'as'" % function_name)
            target_var = bits[-1]
            bits = bits[:-2]
            args, kwargs = parse_bits(
                parser, bits, params, varargs, varkw,
                defaults, takes_context, function_name
            )

            nodelist = parser.parse((end_name, ))
            parser.delete_first_token()

            return AssignmentNode(
                nodelist, takes_context, args, kwargs, target_var
            )

        compile_func.__doc__ = func.__doc__
        library.tag(function_name, compile_func)
        return func

    if func is None:
        # @register.assignment_tag(...)
        return dec
    elif callable(func):
        # @register.assignment_tag
        return dec(func)
    else:
        raise template.TemplateSyntaxError(
            "Invalid arguments provided to assignment_tag_with_cdata"
        )


@assignment_tag_with_cdata(register, name="sparql", takes_context=True)
def sparql(context, cdata=""):
    """
    Executes a sparql query on the template's graph

    >>> from rdflib import Graph
    >>> g = Graph()
    >>> g = g.parse(
    ... data='''
    ... @prefix schema: <http://schema.org/> .
    ... <foo> schema:title "This is the title 2014" .
    ... ''',
    ... format="text/turtle"
    ... )
    ...
    >>> object_iri = '<file:///Users/emoritz/Projects/django-hydra-client/foo>'
    >>> c = template.Context({
    ...   '__graph__': g,
    ...   'object_iri': object_iri,
    ... })
    ...
    >>> t = template.Template('''
    ... {% load hydratags %}
    ... {% sparql as obj %}
    ... PREFIX schema: <http://schema.org/>
    ... SELECT ?title
    ... {
    ...     {{ object_iri|safe }} schema:title ?title .
    ... }
    ... {% endsparql %}
    ... {{ obj.0.0.toPython }}
    ... ''')
    >>> t.render(c).strip()
    u'This is the title 2014'

    Notice that the schema:dateCreated value is still a string, you
    will still need to parse it using a filter.
    """
    graph = context['__hydraclient_graph__']
    try:
        r = graph.query(cdata)
        return list(r)
    except Exception, e:
        raise template.TemplateSyntaxError(
            """Unable to execute the following SPARQL query:

{query}

For the following reason:

{exception}""".format(query=annotate_sparql(cdata), exception=e)
        )


def annotate_sparql(query):
    lines = []
    for i, line in enumerate(query.splitlines()):
        lines.append("{i}. {line}".format(i=i+1, line=line))
    return "\n".join(lines)
                     
