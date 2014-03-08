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
            status, ['']
            )[0].upper().replace('_', ' ')

        def result(found):
            self.status, content_type, self._path = found
            self.reason = reason(self.status)
            self.headers = {"Content-Type": content_type or ""}
            BytesIO.__init__(
                self,
                _io_read_file(self.status, self._path)
            )
            
        return result(
            _io_find_file(
                request.headers.get('Accept', "*/*"),
                urlparse(request.url).path
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


def _io_read_file(status, path):
    if status == 200:
        return open(path).read()
    else:
        return ""


def _io_find_file(accepted, path):
    # Is the path a file?
    if os.path.isfile(path):
        mimetype, _ = mimetypes.guess_type(path)
        return _FoundFile(200, mimetype, path)
    # Is the path a directory?
    elif os.path.isdir(path):
        return _find_index(
            accepted,                 
            path,
            glob("{path}/index*.*".format(path=path))
        )
    else:
        return _FoundFile(404, "text/plain", path)

def _find_index(accepted, path, filenames):
    def second(t):
        return t[1]

    index_files_with_type = (lambda: [
        (filename, mimetype)
        for (filename, (mimetype, _)) in
        (
            (filename, mimetypes.guess_type(filename))
            for filename in filenames
        )
    ])()

    # If no index files were found, 404
    if not index_files_with_type:
        return _FoundFile(404, "text/plain", path)
    else:
        offers = list(map(second, index_files_with_type))
        best = Accept(accepted).best_match(offers)

        if best:
            for filename, mimetype in index_files_with_type:
                if mimetype == best:
                    found = _FoundFile(200, mimetype, filename)
                    return found
        # index files exist, but none are acceptable
        return _FoundFile(406, "text/plain", path)

