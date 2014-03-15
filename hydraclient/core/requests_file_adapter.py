### Do not import anything from hydraclient
### This module will likely be given its own package.

import requests
from urlparse import urlparse
import os
from glob import glob
import mimetypes
from six import BytesIO
from six.moves import map
from collections import namedtuple
from webob.acceptparse import Accept

_FoundFile = namedtuple("_FoundFile", ["status", "content_type", "path"])

mimetypes.add_type("text/turtle", ".ttl")
mimetypes.add_type("application/ld+json", ".jsonld")
mimetypes.add_type("application/rdf+xml", ".rdf")

class FileAdapter(requests.adapters.HTTPAdapter):
    def send(self, request, **kwargs):
        return self.build_response(
            request,
            _FileResponse(request)
        )


class _FileResponse(BytesIO):
    def __init__(self, request):
        def reason(status):
            return requests.status_codes._codes.get(
                status,
                ['']
            )[0].upper().replace('_', ' ')

        def result(found):
            self.status, content_type, self._path = found
            self.reason = reason(self.status)
            self.headers = {"Content-Type": content_type or ""}
            BytesIO.__init__(
                self,
                _io_read_file(self.status, self._path)
            )

        path = _file_path(request.url)
        return result(
            _io_find_file(
                request.headers.get('Accept', "*/*"),
                path
            )
        )

    @property
    def msg(self):
        return self

    def read(self, chunk_size, **kwargs):
        return BytesIO.read(self, chunk_size)

    def info(self):
        return self

    def get_all(self, name, default):
        result = self.headers.get(name)
        if not result:
            return default
        return [result]

    def getheaders(self, name):
        return self.get_all(name, [])

    def release_conn(self):
        self.close()


def _file_path(url):
    return urlparse(url).path

def _io_read_file(status, path):
    if status == 200:
        return open(path).read()
    elif status == 404:
        return "{path} not found".format(path=path)
    else:
        return ""


def _guess_type(url):
    base = url.split("?")[0]
    return mimetypes.guess_type(base)


def _io_find_file(accepted, path):
    if os.path.isfile(path):
        mimetype, _ = _guess_type(path)
        return _FoundFile(200, mimetype, path)
    else:
        return _FoundFile(404, "text/plain", path)
