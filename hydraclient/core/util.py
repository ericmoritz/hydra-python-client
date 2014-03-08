from rdflib import plugin
from rdflib import util
import mimetypes


def accepted():
    """
    Returns a list of content-types that is supported the installed rdflib as a accept header

    # TODO use rdflib to build list
    """
    return "text/turtle; application/ld+json"


