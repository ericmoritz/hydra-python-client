import requests
from urlparse import urlparse
import os
from glob import glob
import mimetypes
from six import BytesIO


class FileAdapter(requests.adapters.HTTPAdapter):
    def send(self, request, **kwargs):
        return self.build_response(
            request,
            _FileResponse(request)
        )


class _FileResponse(BytesIO):
    def __init__(self, request):
        irl = request.url
        found = self.__find_file(
            request.headers.get('Accept', ''), 
            urlparse(irl).path,
        )
        self.status, (content_type, encoding), self._path = found

        self.reason = requests.status_codes._codes.get(
            self.status, ['']
        )[0].upper().replace('_', ' ')

        self.headers = {
            "Content-Type": content_type or ""
        }

        if self.status == 200:
            BytesIO.__init__(self, open(self._path).read())
        else:
            BytesIO.__init__(self, "")

            
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


    @staticmethod
    def __find_file(accepted, path):
        not_found = 404, ("text/plain", "utf-8"), path
        # Is the path a file?
        if not os.path.exists(path):
            return not_found
        if os.path.isfile(path):
            # return the path as is
            return 200, mimetypes.guess_type(path), path
        # Is the path a directory?
        elif os.path.isdir(path):
            # determine the which index file to return based on the
            # accept header
            files = _FileResponse.__offers(
                glob("{path}/index.*".format(path=path))
            )
            try:
                content_type, file_path = files.next()
                return 200, content_type, file_path
            except StopIteration:
                return not_found
            

    @staticmethod
    def __offers(files):
        return (
            (mimetypes.guess_type(file), file)
            for file in files
        )

