import json
import threading
import tornado.ioloop
import tornado.web
from graph.filter_base import FilterBase
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class MainHandler(tornado.web.RequestHandler):
    def initialize(self, filter, output_pin):
        self._filter = filter
        self._output_pin = output_pin
        self._filter.register_active_handler(id(self), self)
        #
        self._meta_dict = {}
        self._meta_dict[TornadoSource.METADATA_KEY_HANDLER_ID] = id(self)
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_URI] = self.request.uri
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_PATH] = self.request.path
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_METHOD] = self.request.method
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_PROTOCOL] = self.request.protocol
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_REMOTE_IP] = self.request.remote_ip
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_HOST] = self.request.host
        headers_copy = {}
        for key in self.request.headers:
            headers_copy[key] = self.request.headers[key]
        self._meta_dict[TornadoSource.METADATA_KEY_REQUEST_HEADERS] = headers_copy
        self._content_type = self.request.headers.get('Content-Type')
        if self._content_type is None:
            self._content_type = ''

    def compute_etag(self):
        return None

    @tornado.web.asynchronous
    def get(self):
        # Since GET shouldn't contain a body, we parse the arguments into json format and pass that instead
        js = json.dumps({k: self.get_argument(k) for k in self.request.arguments})
        self._output_pin.send(TornadoSource.CONTENT_TYPE_APPLICATION_JSON, js, self._meta_dict)

    @tornado.web.asynchronous
    def post(self):
        self._output_pin.send(self._content_type, self.request.body, self._meta_dict)

    @tornado.web.asynchronous
    def put(self):
        self._output_pin.send(self._content_type, self.request.body, self._meta_dict)

    @tornado.web.asynchronous
    def delete(self):
        self._output_pin.send(self._content_type, self.request.body, self._meta_dict)

    def on_finish(self):
        self._filter.unregister_active_handler(id(self))
        super().on_finish()

    def write_response(self, mime_type, payload, metadata_dict):
        resp_code = metadata_dict.get(TornadoSource.METADATA_KEY_RESPONSE_STATUS)
        if resp_code is not None:
            if resp_code >= 400:
                raise tornado.web.HTTPError(resp_code)
            else:
                self.set_status(resp_code)
        self.set_header("Content-Type", mime_type)
        self.set_header("Server", TornadoSource.SERVER_HEADER_FULL)
        self.write(payload)
        self.finish()

class TornadoSource(FilterBase):
    """
    A Tornado instance represented as a source filter
    """
    CONFIG_KEY_URI_PATHS = 'uri_paths'
    METADATA_KEY_HANDLER_ID = 'web_handler_id'
    METADATA_KEY_REQUEST_URI = 'web_request_uri'
    METADATA_KEY_REQUEST_PATH = 'web_request_path'
    METADATA_KEY_REQUEST_METHOD = 'web_request_method'
    METADATA_KEY_REQUEST_PROTOCOL = 'web_request_protocol'
    METADATA_KEY_REQUEST_REMOTE_IP = 'web_request_remote_ip'
    METADATA_KEY_REQUEST_HOST = 'web_request_host'
    METADATA_KEY_REQUEST_HEADERS = 'web_request_headers'
    METADATA_KEY_RESPONSE_STATUS = 'web_response_status'
    #
    CONTENT_TYPE_APPLICATION_JSON = 'application/json'
    #
    SERVER_HEADER_APPENDED_COMPONENT = 'koolspin/rosetta'
    SERVER_HEADER_FULL = 'Tornado/{0} {1}'.format(tornado.version, SERVER_HEADER_APPENDED_COMPONENT)

    def __init__(self, name, config_dict):
        super().__init__(name, config_dict)
        self._active_handlers = {}
        self._uri_paths = self._config_dict.get(TornadoSource.CONFIG_KEY_URI_PATHS)
        for i in range(len(self._uri_paths)):
            mime_type_map = {}
            mime_type_map['*'] = self.recv
            input_pin_name = 'input{0}'.format(i+1)
            ipin = InputPin(input_pin_name, mime_type_map, self)
            self._add_input_pin(ipin)
            output_pin_name = 'output{0}'.format(i+1)
            opin = OutputPin(output_pin_name, True)
            self._add_output_pin(opin)
        #
        self._ioloop_instance = tornado.ioloop.IOLoop.instance()
        self._ioloop_thread = threading.Thread(target=self._ioloop_instance.start)

    def run(self):
        uri_list = []
        for i in range(len(self._uri_paths)):
            output_pin_name = 'output{0}'.format(i+1)
            opin = self.get_output_pin(output_pin_name)
            t = (self._uri_paths[i], MainHandler, dict(filter=self, output_pin=opin))
            uri_list.append(t)
        application = tornado.web.Application(uri_list)
        # application = tornado.web.Application([
        #     (r".*", MainHandler, dict(output_pin=self._output_pin)),
        # ])
        application.listen(8888)
        self._ioloop_thread.start()

    def recv(self, mime_type, payload, metadata_dict):
        handler_id = metadata_dict.get(TornadoSource.METADATA_KEY_HANDLER_ID)
        if handler_id is not None:
            handler = self._get_active_handler(handler_id)
            if handler is not None:
                handler.write_response(mime_type, payload, metadata_dict)

    def register_active_handler(self, handler_id, handler):
        self._active_handlers[handler_id] = handler

    def unregister_active_handler(self, handler_id):
        del self._active_handlers[handler_id]

    def _get_active_handler(self, handler_id):
        return self._active_handlers.get(handler_id)
