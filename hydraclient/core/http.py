from webob.acceptparse import Accept

def content_type(accept_header):
    """
    >>> content_type("text/html")
    'text/html'

    >>> content_type("aoustah")
    """
    return Accept(accept_header).best_match(
        [
            "text/turtle",
            "application/rdf+xml",
            "application/ld+json",
            "text/html"
        ]
    )

