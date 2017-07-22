from tornado import httpclient, gen
from tornado.platform.asyncio import AsyncIOMainLoop
from filters.tornado_source import TornadoSource
from graph.filter_base import FilterBase, FilterState, FilterType
from graph.input_pin import InputPin


class HttpClientSink(FilterBase):
    """
    An HTTP client sink filter. Implements http POST, PUT and DELETE

    Input Pins:
    input - Accepts any mime type. Used to provide METADATA_KEY_REQUEST_URI and METADATA_KEY_REQUEST_METHOD in the metadata_dict.
    """

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.sink)
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)

    def run(self):
        super().run()
        AsyncIOMainLoop().install()
        self._set_filter_state(FilterState.running)

    def graph_is_running(self):
        super().graph_is_running()

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)

    def recv(self, mime_type, payload, metadata_dict):
        request_uri = metadata_dict.get(TornadoSource.METADATA_KEY_REQUEST_URI)
        http_method = metadata_dict.get(TornadoSource.METADATA_KEY_REQUEST_METHOD)
        if self.filter_state == FilterState.running:
            self._post_document(request_uri, http_method, mime_type, payload)
        else:
            raise RuntimeError('{0} tried to process input while filter state is {1}'.format(self.filter_name, self.filter_state))

    @gen.coroutine
    def _post_document(self, request_uri, http_method, mime_type, payload):
        """
        Fetch a document from the http server
        :param remote_uri: The URI to access on the remote server
        :param http_method: The HTTP method to use - GET, POST, etc
        :param mime_type: The mime_type to be sent
        :param http_method: The payload to be sent
        :return:
        """
        try:
            client = httpclient.AsyncHTTPClient(defaults=dict(user_agent="Rosetta/1.0"))
            headers = {'Content-Type': mime_type}
            resp = yield client.fetch(request_uri, validate_cert=False, method=http_method, headers=headers, body=payload)
            # TODO: Move this parser to an utility class
            print('HTTP code: {0}'.format(resp.code))
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
            # if mime_type == 'application/octet-stream':
            #     self._output_pin.send(mime_type, resp.body, meta_dict)
            # else:
            #     body_str = resp.body.decode(target_charset, 'ignore')
            #     self._output_pin.send(mime_type, body_str, meta_dict)
        except Exception as e:
            print('Exception: %s %s' % (e, self._request_uri))

