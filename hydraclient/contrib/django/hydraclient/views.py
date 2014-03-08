from __future__ import absolute_import

from hydraclient.core import client
from . import http
from . import render


def resource(request, path_info, base_irl=None):
    query_string = request.META.get("QUERY_STRING", "")
    request_irl = request.build_absolute_uri()

    resource_irl = client.irl(
        base_irl,
        path_info,
        query_string,
    )

    service_resp = client.get(
        resource_irl,
        request_irl
    )

    return http.response(
        service_resp,
        render.render(
            service_resp, 
            request_irl
        )
    )
