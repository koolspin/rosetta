import binascii
from graph.filter_base import FilterBase, FilterState, FilterType
from graph.pad_template import PadTemplate
from graph.pad_capabilities import PadCapabilities
from graph.input_pin import InputPin
from graph.output_pin import OutputPin


class LoggerSink(FilterBase):
    """
    A logger sink filter.

    Input Pins:
    input - Accepts any mime type. Whatever is sent here gets logged.
    """
    FilterBase.filter_meta[FilterBase.FILTER_META_NAME] = "LoggerSink"
    FilterBase.filter_meta[FilterBase.FILTER_META_DESC] = "Logs whatever data arrives on the sink pad."
    FilterBase.filter_meta[FilterBase.FILTER_META_VER] = "0.9.0"
    FilterBase.filter_meta[FilterBase.FILTER_META_RANK] = FilterBase.FILTER_RANK_SECONDARY
    FilterBase.filter_meta[FilterBase.FILTER_META_ORIGIN_URL] = "https://github.com/koolspin"
    FilterBase.filter_meta[FilterBase.FILTER_META_KLASS] = "Sink/Logger"

    # Here we initialize the template for this element
    # TODO: Can we move all this init stuff to a static method?
    # Create a sink pad that accepts anything and is always available
    sink_pad_cap = PadCapabilities.create_caps_any()
    sink_pad_template = PadTemplate.create_pad_always_sink([sink_pad_cap])
    FilterBase.filter_pad_templates['sink'] = sink_pad_template

    def __init__(self, name, config_dict, graph_manager):
        super().__init__(name, config_dict, graph_manager, FilterType.sink)
        self._output_pin = OutputPin('output', True)
        self._add_output_pin(self._output_pin)
        #
        mime_type_map = {}
        mime_type_map['*'] = self.recv
        ipin = InputPin('input', mime_type_map, self)
        self._add_input_pin(ipin)
        self._output_pin = OutputPin('output', True)
        self._add_output_pin(self._output_pin)

    def run(self):
        super().run()
        self._set_filter_state(FilterState.running)

    def stop(self):
        super().stop()
        self._set_filter_state(FilterState.stopped)

    def recv(self, mime_type, payload, metadata_dict):
        print('Mime type: {0}'.format(mime_type))
        print('meta-dict: {0}'.format(metadata_dict))
        if isinstance(payload, str):
            # String format, print directly
            print('Payload: {0}'.format(payload))
        else:
            # Must be a binary format, convert to hex first
            print('Payload: {0}'.format(self._stringify_payload(mime_type, payload)))
        if self.filter_state == FilterState.running:
            self._output_pin.send(mime_type, payload, metadata_dict)
        else:
            raise RuntimeError('{0} tried to process input while filter state is {1}'.format(self.filter_name, self.filter_state))

    def _stringify_payload(self, mime_type, payload):
        ret_string = ''
        if mime_type == 'application/octet-stream':
            ret_string = binascii.hexlify(payload)
        else:
            ret_string = payload.decode("utf-8")
        return ret_string


