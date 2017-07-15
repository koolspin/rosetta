from tornado import httpclient, gen
from tornado.platform.asyncio import AsyncIOMainLoop
from filters.tornado_source import TornadoSource
from graph.filter_base import FilterBase
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class HttpClient(FilterBase):
    """
    An HTTP client filter
    """

    def __init__(self, name, config_dict):
        super().__init__(name, config_dict)
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)
        self._output_pin = OutputPin('output', True)
        self._add_output_pin(self._output_pin)
        self._request_uri = config_dict.get(TornadoSource.METADATA_KEY_REQUEST_URI)

    def run(self):
        AsyncIOMainLoop().install()
        if self._request_uri is not None:
            self._fetch_document(self._request_uri, 'GET')

    def stop(self):
        pass

    def recv(self, mime_type, payload, metadata_dict):
        request_uri = metadata_dict.get(TornadoSource.METADATA_KEY_REQUEST_URI)
        self._fetch_document(request_uri, 'GET')

    @gen.coroutine
    def _fetch_document(self, request_uri, http_method):
        """
        Fetch a document from the http server
        :param remote_uri: The URI to access on the remote server
        :param http_method: The HTTP method to use - GET, POST, etc
        :return:
        """
        try:
            client = httpclient.AsyncHTTPClient()
            resp = yield client.fetch(request_uri)
            # TODO: Move this parser to an utility class
            content_type = resp.headers.get('Content-Type')
            mime_type = ''
            target_charset = 'utf-8'
            ctype = content_type.split(';')
            if len(ctype) > 0:
                mime_type = ctype[0].strip().lower()
            if len(ctype) > 1:
                charset = ctype[1]
                chars = charset.split('=')
                if len(chars) > 1:
                    charset_lit = chars[0].strip().lower()
                    if charset_lit == 'charset':
                        target_charset = chars[1].strip().lower()
            #
            meta_dict = {}
            meta_dict[TornadoSource.METADATA_KEY_MIME_TYPE] = mime_type
            meta_dict[TornadoSource.METADATA_KEY_REQUEST_URI] = request_uri
            meta_dict[TornadoSource.METADATA_KEY_REQUEST_METHOD] = http_method
            meta_dict[TornadoSource.METADATA_KEY_RESPONSE_CHARSET] = target_charset
            if mime_type == 'application/octet-stream':
                self._output_pin.send(mime_type, resp.body, meta_dict)
            else:
                body_str = resp.body.decode(target_charset, 'ignore')
                self._output_pin.send(mime_type, body_str, meta_dict)
        except Exception as e:
            print('Exception: %s %s' % (e, self._request_uri))

