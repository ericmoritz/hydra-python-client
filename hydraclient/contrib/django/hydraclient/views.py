from time import time
from django.template import RequestContext
from hydraclient.contrib.django.hydraclient import client
from hydraclient.core import mounts
from hydraclient.core.http import guess_serializer
from .render import render_response
import os
import mimetypes
from functools import wraps
from django.http import Http404


def resource(request, cfg_url=None):
    client_url = request.build_absolute_uri("/") # TODO: use django's equiv to SCRIPT_NAME
    request_url = request.build_absolute_uri()
    cfg_resp = client.get(cfg_url, client_url)

    service_url = mounts.resolve(cfg_resp.graph, request_url)

    if service_url is None:
        raise Http404("no <http://vocabs-ld.org/vocabs/web-framework#ServiceMount> in {} for {}".format(cfg_url, request_url))
 
    service_resp = client.get(service_url, request_url)

    user_agent_accept = request.META.get("HTTP_ACCEPT", "")

    response = render_response(
            service_resp,
            request_url,
            user_agent_accept,
            context_instance=RequestContext(request)
    )
    return response


def tc(callback):
    start = time()
    ret = callback()
    end = time()
    return (end-start, ret)


def time_header_value(seconds):
    return u"{t}ms".format(t=seconds * 10000)


def _ext(path_info):
    bits = path_info.split(".")
    ext = bits[-1]
    base = ".".join(bits[:-1])
    return base, ext
