from __future__ import absolute_import
from time import time
from hydraclient.core import client
from .render import render
import mimetypes
import requests
from django.template import RequestContext

session = requests.session()


def resource(request, path_info, base_irl=None):
    print repr(path_info)
    query_string = request.META.get("QUERY_STRING", "")
    user_agent_accept = request.META.get("HTTP_ACCEPT", "")

    request_irl = client.add_qs(path_info, query_string)
    service_irl = client.irljoin(base_irl, request_irl)
    absolute_request_irl = request.build_absolute_uri(request_irl)
    ttlb, service_resp = tc(
        lambda: client.get(session, service_irl, absolute_request_irl)
    )
    ttr, response = tc(
        lambda: render(
            service_resp,
            absolute_request_irl,
            user_agent_accept,
            context_instance=RequestContext(request)
        )
    )
    response['X-Hydra-Service-Time-To-Last-Byte'] = time_header_value(ttlb)
    response['X-Hydra-Client-Time-To-Render'] = time_header_value(ttr)
    return response


def tc(callback):
    start = time()
    ret = callback()
    end = time()
    return (end-start, ret)


def time_header_value(seconds):
    return u"{t}ms".format(t=seconds * 10000)

